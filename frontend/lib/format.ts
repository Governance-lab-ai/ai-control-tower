export function formatBooleanYesNo(value: boolean): string {
  return value ? "Yes" : "No";
}

export function formatRequired(value: boolean): string {
  return value ? "Required" : "Not required";
}

export function formatDateTime(value: string): string {
  return new Date(value).toLocaleString();
}
