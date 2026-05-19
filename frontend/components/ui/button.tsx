import Link from "next/link";
import type { AnchorHTMLAttributes, ButtonHTMLAttributes, ReactNode } from "react";

const primaryClass =
  "inline-flex items-center justify-center gap-2 rounded-lg border border-trust-teal/50 bg-trust-teal px-4 py-2.5 text-sm font-semibold text-[#04111F] disabled:cursor-not-allowed disabled:opacity-60";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
};

type ActionLinkProps = AnchorHTMLAttributes<HTMLAnchorElement> & {
  href: string;
  children: ReactNode;
};

export function Button({ children, className = "", ...props }: ButtonProps) {
  return (
    <button className={`${primaryClass} ${className}`} {...props}>
      {children}
    </button>
  );
}

export function ActionLink({ href, children, className = "", ...props }: ActionLinkProps) {
  return (
    <Link href={href} className={`${primaryClass} ${className}`} {...props}>
      {children}
    </Link>
  );
}
