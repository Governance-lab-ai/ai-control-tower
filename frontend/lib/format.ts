export function formatBooleanYesNo(value: boolean): string {
  return value ? "Yes" : "No";
}

export function formatRequired(value: boolean): string {
  return value ? "Required" : "Not required";
}

export function formatDateTime(value: string): string {
  return new Date(value).toLocaleString();
}

export function formatCurrencyUsd(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 6,
    maximumFractionDigits: 6,
  }).format(value);
}

export function formatLatency(value: number): string {
  return `${value}ms`;
}
