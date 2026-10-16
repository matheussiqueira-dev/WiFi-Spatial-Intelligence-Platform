import { z } from "zod";

export const scenarioSchema = z.enum([
  "empty",
  "stationary",
  "walking",
  "entering",
  "leaving",
  "interference",
  "packet_loss",
  "disconnect",
]);
export const configSchema = z.object({
  scenario: scenarioSchema,
  seed: z.number().int().min(0).max(4294967295),
  occupants: z.number().int().min(0).max(20),
  speed: z.number().min(0.25).max(4),
});
export const internalEventSchema = z
  .object({
    schema_version: z.literal("1.0.0"),
    event_id: z.guid(),
    timestamp: z.iso.datetime(),
    source_id: z.literal("simulator-01"),
    room_id: z.literal("living-room"),
    event_type: z.literal("simulation.observation"),
    source_type: z.literal("SIMULATED"),
    evidence_level: z.literal("L0_SYNTHETIC"),
    validation_status: z.literal("IMPLEMENTED_SYNTHETIC"),
    measurements: z.object({
      presence_detected: z.boolean(),
      occupancy_estimate: z.number().int().min(0).max(20),
      ground_truth_positions: z
        .array(z.tuple([z.number().min(0).max(8), z.number().min(0).max(6)]))
        .max(20),
    }),
    quality: z.object({ signal_quality: z.null(), confidence: z.null() }),
    model: z.object({ id: z.null(), version: z.null() }),
    provenance: z.object({
      generator: z.literal("local-simulator"),
      seed: z.number().refine(Number.isInteger),
      tick: z.number().int().nonnegative(),
      scenario: z.string(),
      dataset_id: z.string().nullable(),
    }),
    privacy: z.object({
      classification: z.literal("synthetic"),
      consent_record_id: z.null(),
    }),
    processing_latency_ms: z.number().nonnegative().nullable(),
  })
  .refine(
    (e) =>
      e.measurements.occupancy_estimate ===
        e.measurements.ground_truth_positions.length &&
      e.measurements.presence_detected ===
        e.measurements.occupancy_estimate > 0,
    "Observação inconsistente",
  );
export const ruviewEventSchema = z
  .object({
    schema_version: z.literal("1.1.0"),
    event_id: z.guid(),
    timestamp: z.iso.datetime(),
    source_id: z.literal("ruview-01"),
    room_id: z.literal("living-room"),
    event_type: z.literal("simulation.ruview.observation"),
    source_type: z.literal("SIMULATED"),
    evidence_level: z.literal("L0_SYNTHETIC"),
    validation_status: z.literal("IMPLEMENTED_SYNTHETIC"),
    measurements: z.object({
      presence_detected: z.boolean(),
      occupancy_estimate: z.number().int().min(0).max(20).nullable(),
      ground_truth_positions: z
        .array(z.tuple([z.number(), z.number()]))
        .length(0),
    }),
    quality: z.object({ signal_quality: z.null(), confidence: z.null() }),
    model: z.object({ id: z.null(), version: z.null() }),
    provenance: z.object({
      generator: z.literal("ruview-simulated"),
      scenario: z.literal("ruview-simulated"),
      seed: z.null(),
      tick: z.number().int().nonnegative(),
      dataset_id: z.null(),
      upstream_source: z.literal("simulated"),
      upstream_type: z.literal("sensing_update"),
      adapter_version: z.literal("1.0.0"),
    }),
    privacy: z.object({
      classification: z.literal("synthetic"),
      consent_record_id: z.null(),
    }),
    processing_latency_ms: z.number().nonnegative().nullable(),
  })
  .refine(
    (e) =>
      e.measurements.occupancy_estimate === null ||
      e.measurements.presence_detected ===
        e.measurements.occupancy_estimate > 0,
    "Presença e contagem RuView inconsistentes",
  );
export const nativeEventSchema = z
  .object({
    ...internalEventSchema.shape,
    schema_version: z.literal("2.0.0"),
    source_id: z.literal("native-01"),
    event_type: z.literal("synthetic.spatial.observation"),
    provider: z.literal("synthetic-native"),
    provenance: internalEventSchema.shape.provenance.extend({
      generator: z.literal("synthetic-native"),
      seed: configSchema.shape.seed,
      scenario: scenarioSchema,
      dataset_id: z.null(),
    }),
  })
  .refine(
    (event) =>
      event.measurements.occupancy_estimate < 0 ||
      event.measurements.occupancy_estimate > 20 ||
      (event.measurements.occupancy_estimate ===
        event.measurements.ground_truth_positions.length &&
        event.measurements.presence_detected ===
          event.measurements.occupancy_estimate > 0),
    "Observação nativa inconsistente",
  );
export const eventSchema = z.discriminatedUnion("schema_version", [
  internalEventSchema,
  ruviewEventSchema,
  nativeEventSchema,
]);
export const sourceDiagnosticsSchema = z.object({
  service_status: z.enum([
    "stopped",
    "connecting",
    "waiting",
    "receiving",
    "reconnecting",
  ]),
  connected: z.boolean(),
  received_frames: z.number().int().nonnegative(),
  rejected_frames: z.number().int().nonnegative(),
  ignored_frames: z.number().int().nonnegative(),
  duplicate_frames: z.number().int().nonnegative(),
  reconnections: z.number().int().nonnegative(),
  last_event_age_seconds: z.number().nonnegative().nullable(),
  stale: z.boolean(),
  last_error: z.string().nullable(),
  data_quality: z.string(),
  upstream_source: z.literal("simulated"),
  evidence_level: z.literal("L0_SYNTHETIC"),
});
export const statusSchema = z.object({
  metrics: z
    .object({
      window_seconds: z.number().nonnegative(),
      event_rate: z.number().nonnegative(),
      queue_depth: z.number().int().nonnegative(),
      visualization_drops: z.number().int().nonnegative(),
      visualization_drop_rate: z.number().min(0).max(1).nullable(),
      queue_wait_p50_ms: z.number().nonnegative().nullable(),
      queue_wait_p95_ms: z.number().nonnegative().nullable(),
      segment_id: z.string().nullable(),
      last_seen: z.string().nullable(),
      reconnections: z.number().int().nonnegative(),
      rf_drop_rate: z.null(),
    })
    .optional(),
  state: z.enum(["stopped", "running", "paused"]),
  provider: z.enum(["synthetic-native", "SIMULATED", "RUVIEW_STREAM"]),
  legacy_lab_enabled: z.boolean().optional(),
  evidence_level: z.literal("L0_SYNTHETIC"),
  latest: eventSchema.nullable(),
  produced_events: z.number().int().nonnegative(),
  dropped_visualization_events: z.number().int().nonnegative(),
  queue_depth: z.number().int().nonnegative(),
  error: z.string().nullable(),
  config: configSchema,
  connected: z.boolean(),
  source_diagnostics: sourceDiagnosticsSchema.nullable().optional(),
});
export const historySchema = z.object({
  items: z.array(eventSchema),
  total: z.number().int().nonnegative(),
  limit: z.number().int(),
  offset: z.number().int(),
});
export const streamSchema = z.discriminatedUnion("type", [
  z.object({ type: z.literal("status"), data: statusSchema }),
  z.object({ type: z.literal("event"), data: eventSchema }),
]);
export const sensorSchema = z.object({
  id: z.string(),
  source_type: z.literal("SIMULATED"),
  virtual: z.literal(true),
  position_m: z.tuple([z.number(), z.number()]),
  connected: z.boolean(),
  firmware: z.null(),
  signal_quality: z.null(),
  evidence_level: z.literal("L0_SYNTHETIC"),
});
export type SensingEvent = z.infer<typeof eventSchema>;
export type Status = z.infer<typeof statusSchema>;
export type SimulationConfig = z.infer<typeof configSchema>;
export type Sensor = z.infer<typeof sensorSchema>;
