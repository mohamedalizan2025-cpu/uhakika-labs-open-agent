// Formatting helpers. Revenue is shown as a whole-number TZS amount with
// thousands separators; values always originate from the backend response.

export function formatTzs(amount: number): string {
  const safe = Number.isFinite(amount) ? Math.max(0, Math.round(amount)) : 0;
  return `TZS ${safe.toLocaleString("en-US")}`;
}

export function formatConfidence(confidence?: number | null): string | null {
  if (confidence == null || !Number.isFinite(confidence)) return null;
  return `${Math.round(confidence * 100)}%`;
}

export function formatClock(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}
