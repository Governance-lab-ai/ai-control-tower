import type { InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from "react";

const labelClass = "text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]";
const controlClass = "mt-2 w-full rounded-lg border border-line-700 bg-navy-900 px-3 py-2 text-sm text-[#E6EEF8] outline-none focus:border-trust-teal";
const checkboxClass = "flex items-center gap-3 rounded-lg border border-line-700 bg-navy-900 px-3 py-2 text-sm text-[#E6EEF8]";

export function TextField({
  label,
  className = "",
  ...props
}: InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  className?: string;
}) {
  return (
    <label className={className}>
      <span className={labelClass}>{label}</span>
      <input className={controlClass} {...props} />
    </label>
  );
}

export function TextareaField({
  label,
  className = "",
  ...props
}: TextareaHTMLAttributes<HTMLTextAreaElement> & {
  label: string;
  className?: string;
}) {
  return (
    <label className={className}>
      <span className={labelClass}>{label}</span>
      <textarea className={`${controlClass} min-h-28`} {...props} />
    </label>
  );
}

export function SelectField({
  label,
  options,
  hideLabel = false,
  className = "",
  ...props
}: SelectHTMLAttributes<HTMLSelectElement> & {
  label: string;
  options: readonly string[];
  hideLabel?: boolean;
  className?: string;
}) {
  return (
    <label className={className}>
      <span className={hideLabel ? "sr-only" : labelClass}>{label}</span>
      <select className={`${controlClass} capitalize`} {...props}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

export function CheckboxField({
  label,
  children,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  children?: ReactNode;
}) {
  return (
    <label className={checkboxClass}>
      <input type="checkbox" {...props} />
      {children ?? label}
    </label>
  );
}
