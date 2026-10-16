import { z } from "zod";

export const jobSchema = z.object({
  id: z.uuid(),
  seed: z.number().int(),
  state: z.enum([
    "queued",
    "preparing",
    "training",
    "persisting",
    "completed",
    "cancelled",
    "failed",
    "interrupted",
  ]),
  progress: z.number().min(0).max(100),
  run_id: z.uuid().nullable(),
  error: z.string().nullable(),
  evidence_level: z.literal("L0_SYNTHETIC"),
});

const motionClass = z.enum(["stationary", "walking", "unknown"]);
const rate = z.number().min(0).max(1).nullable();
const evaluation = z.object({
  classes: z.array(motionClass),
  confusion_matrix: z.array(z.array(z.number().int().nonnegative())),
  samples: z.number().int().nonnegative(),
  support: z.record(z.string(), z.number().int().nonnegative()),
  rejected: z.number().int().nonnegative(),
  rejection_rate: rate,
  accuracy_accepted: rate,
  false_positive_rate: rate,
  predictions: z.array(
    z.object({
      session_id: z.string(),
      window: z.number().int().nonnegative(),
      prediction: motionClass,
      reference: motionClass,
      quality: z.enum(["gap", "complete"]),
      mean_speed: z.number().nonnegative().nullable(),
      start_seconds: z.number().nonnegative(),
      end_seconds: z.number().nonnegative(),
    }),
  ),
});
export const experimentSchema = z.object({
  id: z.uuid(),
  created_at: z.string(),
  seed: z.number().int().nonnegative(),
  duration_ms: z.number().nonnegative(),
  evidence_level: z.literal("L0_SYNTHETIC"),
  dataset_version: z.literal("virtual-motion-v1"),
  dataset_sha256: z.string().regex(/^[a-f0-9]{64}$/),
  model: z.object({
    id: z.literal("geometry-motion-v1"),
    version: z.literal("geometry-speed-v1"),
    threshold_m_per_s: z.number().positive(),
    abstention_margin: z.number().min(0).max(1),
    features: z.array(z.string()),
    sha256: z.string().regex(/^[a-f0-9]{64}$/),
  }),
  validation: evaluation,
  evaluation,
  splits: z.record(z.string(), z.array(z.string())),
  unsupported: z.array(z.string()),
  limitation: z.string(),
});
export const experimentListSchema = z.object({
  items: z.array(z.object({ id: z.uuid(), created_at: z.string() })),
  total: z.number().int().nonnegative(),
  limit: z.number().int(),
  offset: z.number().int(),
});
export type Experiment = z.infer<typeof experimentSchema>;
