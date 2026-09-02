/** Small formatters. Kept out of component modules so Fast Refresh works. */

export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${Math.floor(seconds)}s`;
  const minutes = Math.floor(seconds / 60);
  const rest = Math.floor(seconds % 60);
  if (minutes < 60) return rest ? `${minutes}m ${rest}s` : `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m`;
}

const ROMAN = ["", "I", "II", "III", "IV", "V"];

export function toRoman(value: number): string {
  return ROMAN[value] ?? String(value);
}
