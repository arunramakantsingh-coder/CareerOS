from __future__ import annotations

import asyncio
import logging
import time

from app.api.intelligence_health import _run_configured_health_checks, get_health_policy
from app.core.database import SessionLocal
from app.intelligence.runtime_trace import event, finish, start_trace

logger = logging.getLogger(__name__)


async def run_health_scheduler(stop_event: asyncio.Event) -> None:
    """Run non-generative provider health checks on the configured interval."""
    while not stop_event.is_set():
        try:
            db = SessionLocal()
            try:
                policy = get_health_policy(db)
            finally:
                db.close()

            interval = int(policy["interval_seconds"])
            if policy["enabled"]:
                trace_id = start_trace("provider_health_check", [])
                cycle_started = time.perf_counter()
                event(trace_id, "HEALTH_CYCLE_STARTED", "Automatic provider health cycle started", interval_seconds=interval)
                db = SessionLocal()
                try:
                    result = await _run_configured_health_checks(db, trace_id=trace_id)
                    event(trace_id, "HEALTH_CYCLE_COMPLETED", "Automatic provider health cycle completed", healthy=result.get("healthy"), total=result.get("total"))
                    finish(trace_id, status="completed", total_latency_ms=(time.perf_counter() - cycle_started) * 1000)
                    logger.info("Automatic Intelligence health check completed: healthy=%s total=%s", result.get("healthy"), result.get("total"))
                except Exception as exc:
                    event(trace_id, "HEALTH_CYCLE_FAILED", "Automatic provider health cycle failed", error=str(exc)[:500])
                    finish(trace_id, status="failed", total_latency_ms=(time.perf_counter() - cycle_started) * 1000)
                    logger.exception("Automatic Intelligence health check failed")
                finally:
                    db.close()

            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            continue
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Intelligence health scheduler loop error")
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=60)
            except asyncio.TimeoutError:
                pass
