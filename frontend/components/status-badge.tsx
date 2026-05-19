import { Badge, type BadgeTone } from "@/components/ui/badge";

type StatusBadgeProps = {
  label: string;
  tone: BadgeTone;
};

export function StatusBadge({ label, tone }: StatusBadgeProps) {
  return <Badge tone={tone}>{label}</Badge>;
}
