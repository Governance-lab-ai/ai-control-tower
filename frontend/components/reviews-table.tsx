import Link from "next/link";

import { ReviewPriorityBadge, ReviewStatusBadge } from "@/components/review-badges";
import { formatDateTime } from "@/lib/format";
import type { HumanReview } from "@/lib/types";

export function ReviewsTable({ reviews }: { reviews: HumanReview[] }) {
  if (reviews.length === 0) {
    return <p className="p-5 text-sm text-[#A8B8CA]">No pending human reviews.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-navy-900/70 text-xs uppercase tracking-[0.04em] text-[#718198]">
          <tr>
            <th className="px-5 py-3 font-semibold">Review</th>
            <th className="px-5 py-3 font-semibold">Reason</th>
            <th className="px-5 py-3 font-semibold">Priority</th>
            <th className="px-5 py-3 font-semibold">Status</th>
            <th className="px-5 py-3 font-semibold">Run</th>
            <th className="px-5 py-3 font-semibold">Created</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line-700">
          {reviews.map((review) => (
            <tr key={review.id} className="hover:bg-panel-825/60">
              <td className="px-5 py-4">
                <Link href={`/reviews/${review.id}`} className="font-mono text-xs text-signal-cyan hover:text-[#E6EEF8]">
                  {review.id.slice(0, 8)}
                </Link>
                <p className="mt-1 max-w-xl truncate text-xs text-[#A8B8CA]">{review.summary}</p>
              </td>
              <td className="px-5 py-4 font-mono text-xs text-[#A8B8CA]">{review.reason}</td>
              <td className="px-5 py-4">
                <ReviewPriorityBadge priority={review.priority} />
              </td>
              <td className="px-5 py-4">
                <ReviewStatusBadge status={review.status} />
              </td>
              <td className="px-5 py-4">
                <Link href={`/runs/${review.model_run_id}`} className="font-mono text-xs text-signal-cyan hover:text-[#E6EEF8]">
                  {review.model_run_id.slice(0, 8)}
                </Link>
              </td>
              <td className="px-5 py-4 text-[#A8B8CA]">{formatDateTime(review.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
