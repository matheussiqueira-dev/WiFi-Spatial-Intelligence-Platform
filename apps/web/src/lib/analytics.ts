import { z } from "zod";
import { eventSchema } from "./contracts";

const page = <T extends z.ZodType>(item: T) =>
  z.object({
    items: z.array(item),
    total: z.number().int().nonnegative(),
    limit: z.number().int().positive(),
    offset: z.number().int().nonnegative(),
  });
const evidence = z.literal("L0_SYNTHETIC");
const utcDate = z.iso
  .datetime({ offset: true })
  .refine(
    (value) => value.endsWith("Z") || value.endsWith("+00:00"),
    "Timestamp must be UTC",
  );
const nullableMetric = z.number().nonnegative().nullable();
export const analyticsSchema = z.object({
  schema_version: z.literal("1.0.0"),
  evidence_level: evidence,
  validation_status: z.literal("IMPLEMENTED_SYNTHETIC"),
  mode: z.literal("HISTORICAL"),
  query: z.object({
    start: utcDate,
    end: utcDate,
    bucket: z.enum(["minute", "five_minutes", "hour", "day"]),
  }),
  summary: z.object({
    samples: z.number().int().nonnegative(),
    segments: z.number().int().nonnegative(),
    entries_estimate: z.number().int().nonnegative(),
    exits_estimate: z.number().int().nonnegative(),
    unknown_count_samples: z.number().int().nonnegative(),
    presence_seconds: z.number().nonnegative(),
    absent_seconds: z.number().nonnegative(),
    unknown_seconds: z.number().nonnegative(),
    excluded_transitions: z.number().int().nonnegative(),
    event_rate: nullableMetric,
    queue_wait_p50_ms: nullableMetric,
    queue_wait_p95_ms: nullableMetric,
    rf_drop_rate: z.null(),
  }),
  buckets: page(
    z.object({
      timestamp: utcDate,
      source_id: z.enum(["native-01", "simulator-01", "ruview-01"]),
      samples: z.number().int().positive(),
      occupancy_mean: nullableMetric,
      occupancy_max: nullableMetric,
      presence_fraction: z.number().min(0).max(1),
      unknown_count_samples: z.number().int().nonnegative(),
      entries_estimate: z.number().int().nonnegative(),
      exits_estimate: z.number().int().nonnegative(),
      evidence_level: evidence,
    }),
  ),
  intervals: page(
    z.object({
      start: utcDate,
      end: utcDate,
      state: z.enum(["present", "absent", "unknown"]),
      duration_seconds: z.number().nonnegative(),
      source_id: z.string(),
      segment_id: z.string().nullable(),
      evidence_level: evidence,
    }),
  ),
  transitions: page(
    z.object({
      timestamp: utcDate,
      event_id: z.uuid(),
      source_id: z.string(),
      segment_id: z.string().nullable(),
      from_count: z.number().int().nonnegative(),
      to_count: z.number().int().nonnegative(),
      entries_estimate: z.number().int().nonnegative(),
      exits_estimate: z.number().int().nonnegative(),
      evidence_level: evidence,
    }),
  ),
  limitations: z.array(z.string()),
});
export const replaySchema = page(
  z.object({ event: eventSchema, segment_id: z.string().nullable() }),
).extend({
  evidence_level: evidence,
  mode: z.literal("REPLAY"),
  snapshot_end: utcDate,
});
export const reportsSchema = page(
  z.object({ id: z.uuid(), created_at: utcDate }),
);
export type Analytics = z.infer<typeof analyticsSchema>;
export type ReplayFrame = z.infer<typeof replaySchema>["items"][number];

export function download(name: string, text: string, type: string) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
