import { z } from "zod";

const rate = z.number().min(0).max(1);
const sha256 = z.string().regex(/^[a-f0-9]{64}$/);

export const fingerprintEvaluationSchema = z.object({
  method: z.literal("rf-fingerprint-zscore-v1"),
  evidence_level: z.literal("L0_SYNTHETIC"),
  transport: z.literal("SWF1"),
  seed: z.number().int(),
  fingerprint_sha256: sha256,
  reference_frames: z.number().int().positive(),
  window_frames: z.number().int().positive(),
  min_frames: z.number().int().positive(),
  subcarriers: z.number().int().positive(),
  threshold: z.number().positive(),
  reference_scores_max: z.number().nonnegative(),
  normal_windows: z.number().int(),
  false_positives: z.number().int(),
  false_positive_rate: rate,
  changed_windows: z.number().int(),
  detections: z.number().int(),
  detection_rate: rate,
  subtle_windows: z.number().int(),
  subtle_detection_rate: rate,
  other_environment_windows: z.number().int(),
  other_environment_detection_rate: rate,
  sparse_windows: z.number().int(),
  abstained: z.number().int(),
  frames_received: z.number().int(),
  limitations: z.array(z.string()).min(1),
});
export type FingerprintEvaluation = z.infer<typeof fingerprintEvaluationSchema>;

export const licenses = [
  "MIT",
  "Apache-2.0",
  "BSD-2-Clause",
  "BSD-3-Clause",
  "CC-BY-4.0",
  "CC-BY-NC-4.0",
  "GPL-3.0-only",
  "PROPRIETARY",
  "UNKNOWN",
] as const;

const card = z.object({
  id: z.uuid(),
  created_at: z.iso.datetime({ offset: true }),
  origin: z.literal("third_party"),
  name: z.string(),
  version: z.string(),
  license: z.enum(licenses),
  source_url: z.string().startsWith("https://"),
  sha256,
  intended_use: z.string(),
  commercial_use: z.enum(["ALLOWED", "REVIEW_REQUIRED", "NOT_ALLOWED"]),
  status: z.literal("NOT_LOADED"),
  evidence_level: z.literal("UNVERIFIED"),
});
export const modelRegistrySchema = z.object({
  project: z
    .array(
      z.object({
        origin: z.literal("project"),
        id: z.string(),
        version: z.string(),
        sha256,
        size_bytes: z.number().int().nonnegative(),
        integrity: z.enum(["VERIFIED", "MISMATCH", "UNREADABLE"]),
        license: z.literal("MIT"),
        evidence_level: z.literal("L0_SYNTHETIC"),
      }),
    )
    .max(200),
  third_party: z.array(card).max(50),
  maximum_third_party: z.number().int().positive(),
});
export type ModelRegistry = z.infer<typeof modelRegistrySchema>;
export const modelCardSchema = card;

const percent = (value: number) =>
  `${(value * 100).toLocaleString("pt-BR", { maximumFractionDigits: 0 })}%`;

/** Plain-language rows; every rate stays tied to its synthetic scope. */
export function evaluationRows(result: FingerprintEvaluation) {
  return [
    {
      label: "Alarmes falsos (mesmo ambiente)",
      value: `${percent(result.false_positive_rate)} de ${result.normal_windows} janelas`,
    },
    {
      label: "Mudanças grandes detectadas",
      value: `${percent(result.detection_rate)} de ${result.changed_windows} janelas`,
    },
    {
      label: "Mudanças sutis detectadas",
      value: `${percent(result.subtle_detection_rate)} de ${result.subtle_windows} janelas`,
    },
    {
      label: "Outro ambiente reconhecido como diferente",
      value: `${percent(result.other_environment_detection_rate)} de ${result.other_environment_windows} janelas`,
    },
    {
      label: "Abstenções por poucos quadros",
      value: `${result.abstained} de ${result.sparse_windows} janelas`,
    },
  ];
}

export const commercialUse = {
  ALLOWED: "Uso comercial permitido pela licença",
  REVIEW_REQUIRED: "Exige revisão jurídica",
  NOT_ALLOWED: "Licença não comercial",
} as const;
