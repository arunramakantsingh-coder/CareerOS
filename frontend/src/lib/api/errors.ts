export function formatApiError(payload: any, fallback = "Something went wrong."): string {
  const detail = payload?.detail ?? payload?.message ?? payload?.error;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item?.msg) return String(item.msg);
        return "Validation error";
      })
      .filter(Boolean);
    if (messages.length) return messages.join(" • ");
  }
  if (detail && typeof detail === "object") {
    if (detail.msg) return String(detail.msg);
    try { return JSON.stringify(detail); } catch { return fallback; }
  }
  return fallback;
}
