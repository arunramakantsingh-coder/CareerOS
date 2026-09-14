from __future__ import annotations

import asyncio
import logging

from app.api.intelligence_health import _run_configured_health_checks, get_health_policy
from app.core.database import SessionLocal

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
                db = SessionLocal()
                try:
                    result = await _run_configured_health_checks(db)
                    logger.info(
                        "Automatic Intelligence health check completed: healthy=%s total=%s",
                        result.get("healthy"),
                        result.get("total"),
                    )
                except Exception:
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
