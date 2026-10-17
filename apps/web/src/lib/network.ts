import { z } from "zod";

const metric = z.number().nonnegative().nullable();
export const locationSchema = z
  .string()
  .min(1)
  .max(48)
  .regex(/^[\p{L}\p{N}][\p{L}\p{N}_ .-]*$/u);
export const networkSampleSchema = z.object({
  schema_version: z.literal("1.0.0"),
  data_class: z.literal("HOST_NETWORK_TELEMETRY"),
  evidence_level: z.literal("L2_LIVE_UNVALIDATED"),
  source: z.literal("windows-netsh"),
  sample_id: z.guid(),
  collector_id: z.guid(),
  timestamp: z.iso.datetime({ offset: true }),
  location: locationSchema,
  link_state: z.enum(["CONNECTED", "DISCONNECTED", "UNAVAILABLE"]),
  signal_percent: z.number().int().min(0).max(100).nullable(),
  channel: z.number().int().min(1).max(233).nullable(),
  radio_type: z
    .enum([
      "802.11a",
      "802.11b",
      "802.11g",
      "802.11n",
      "802.11ac",
      "802.11ax",
      "802.11be",
    ])
    .nullable(),
  rx_mbps: metric,
  tx_mbps: metric,
  probe_sent: z.number().int().min(0).max(3),
  probe_rtt_ms: z.array(z.number().min(0).max(10000)).max(3),
  probe_status: z.enum(["NOT_RUN", "COMPLETED", "UNAVAILABLE"]),
  collector_error: z.string().nullable(),
});
const summary = z.object({
  samples: z.number().int().nonnegative(),
  connected_samples: z.number().int().nonnegative(),
  disconnected_samples: z.number().int().nonnegative(),
  unavailable_samples: z.number().int().nonnegative(),
  connected_percent: z.number().min(0).max(100).nullable(),
  signal_mean_percent: z.number().min(0).max(100).nullable(),
  signal_min_percent: z.number().min(0).max(100).nullable(),
  gateway_mean_ms: metric,
  gateway_p95_ms: metric,
  gateway_loss_percent: z.number().min(0).max(100).nullable(),
  disconnect_events: z.number().int().nonnegative(),
  missing_seconds: z.number().nonnegative(),
  last_seen: z.iso.datetime({ offset: true }).nullable(),
  collector_stale: z.boolean(),
});
export const networkReportSchema = z.object({
  data_class: z.literal("HOST_NETWORK_TELEMETRY"),
  evidence_level: z.literal("L2_LIVE_UNVALIDATED"),
  start: z.iso.datetime({ offset: true }),
  end: z.iso.datetime({ offset: true }),
  summary,
  latest: networkSampleSchema.nullable(),
  items: z.array(networkSampleSchema),
  total: z.number().int().nonnegative(),
  limit: z.number().int().positive(),
  offset: z.number().int().nonnegative(),
  locations: z.array(locationSchema).max(20),
  configured_location: locationSchema,
  comparisons: z.array(z.object({ location: locationSchema, summary })).max(20),
});
export type NetworkReport = z.infer<typeof networkReportSchema>;
export function networkWarnings(report: NetworkReport): string[] {
  const warnings: string[] = [];
  if (report.summary.collector_stale)
    warnings.push(
      "Coletor sem atualização recente. Isso não comprova queda da rede.",
    );
  else if (report.latest?.link_state === "DISCONNECTED")
    warnings.push("O computador informou Wi-Fi desconectado.");
  else if (report.latest?.link_state === "UNAVAILABLE")
    warnings.push("O coletor não conseguiu ler o estado do Wi-Fi.");
  if (
    report.latest?.signal_percent != null &&
    report.latest.signal_percent < 40
  )
    warnings.push(
      "Sinal abaixo de 40% na última leitura; compare com outros pontos.",
    );
  if ((report.summary.gateway_loss_percent ?? 0) > 20)
    warnings.push(
      "Mais de 20% das sondas ao roteador ficaram sem resposta no período; ICMP pode estar limitado.",
    );
  return warnings;
}

const band = z.enum(["2.4GHz", "5GHz", "6GHz"]);
const channelNumber = z.number().int().min(1).max(233);
const occupancy = z.object({
  band,
  channel: channelNumber,
  ap_count: z.number().int().min(1).max(500),
  strongest_signal_percent: z.number().int().min(0).max(100),
  utilization_percent: z.number().int().min(0).max(100).nullable(),
});
export const channelPlanSchema = z.object({
  data_class: z.literal("HOST_NETWORK_TELEMETRY"),
  evidence_level: z.literal("L2_LIVE_UNVALIDATED"),
  start: z.iso.datetime({ offset: true }),
  end: z.iso.datetime({ offset: true }),
  location: locationSchema.nullable(),
  surveys: z.number().int().nonnegative(),
  failed_surveys: z.number().int().nonnegative(),
  last_survey_at: z.iso.datetime({ offset: true }).nullable(),
  bands: z
    .array(
      z.object({
        band,
        observed: z.array(occupancy).max(64),
        candidates: z
          .array(
            z.object({
              channel: channelNumber,
              observed_ap_count: z.number().nonnegative(),
              interference_score: z.number().nonnegative(),
            }),
          )
          .max(16),
        current_channel: channelNumber.nullable(),
        current_score: z.number().nonnegative().nullable(),
        recommended_channel: channelNumber.nullable(),
        advice: z.enum([
          "KEEP",
          "CONSIDER_CHANGE",
          "NO_CURRENT",
          "NOT_MODELED",
        ]),
      }),
    )
    .max(3),
  limitations: z.array(z.string()).max(10),
});
export type ChannelPlan = z.infer<typeof channelPlanSchema>;
export type BandPlan = ChannelPlan["bands"][number];

export function channelAdvice(plan: BandPlan): string {
  switch (plan.advice) {
    case "KEEP":
      return `Manter o canal ${plan.current_channel}: nenhum candidato é claramente menos congestionado.`;
    case "CONSIDER_CHANGE":
      return `Considerar o canal ${plan.recommended_channel} no roteador; o canal atual ${plan.current_channel} está mais congestionado.`;
    case "NO_CURRENT":
      return plan.recommended_channel == null
        ? "Sem varreduras no período para recomendar."
        : `O computador não está nesta banda. Canal menos congestionado: ${plan.recommended_channel}.`;
    case "NOT_MODELED":
      return "Banda listada apenas como observação; sem recomendação.";
  }
}

export const networkHealthSchema = z.object({
  data_class: z.literal("HOST_NETWORK_TELEMETRY"),
  evidence_level: z.literal("L2_LIVE_UNVALIDATED"),
  mode: z.literal("ADVISORY"),
  start: z.iso.datetime({ offset: true }),
  end: z.iso.datetime({ offset: true }),
  location: locationSchema.nullable(),
  bucket_minutes: z.number().int().min(15).max(240),
  buckets: z
    .array(
      z.object({
        start: z.iso.datetime({ offset: true }),
        end: z.iso.datetime({ offset: true }),
        summary,
      }),
    )
    .max(96),
  recent: summary,
  baseline: summary,
  alerts: z
    .array(
      z.object({
        code: z.enum([
          "SIGNAL_DROP",
          "LATENCY_RISE",
          "PACKET_LOSS",
          "FREQUENT_DISCONNECTS",
          "COLLECTOR_STALE",
        ]),
        severity: z.enum(["info", "warning"]),
        metric: z.string(),
        recent: z.number().nullable(),
        baseline: z.number().nullable(),
        threshold: z.number(),
        message: z.string(),
      }),
    )
    .max(5),
  abstentions: z.array(z.string()).max(5),
});
export type NetworkHealth = z.infer<typeof networkHealthSchema>;
type Summary = z.infer<typeof summary>;
export type LocationGrade = "Bom" | "Regular" | "Fraco" | "Sem dados";

/**
 * Operator-facing grade of a measured point. Heuristic over Windows signal quality (%)
 * and gateway probe loss; it ranks points of the same home, it is not a speed test.
 */
export function locationGrade(point: Summary): LocationGrade {
  const signal = point.signal_mean_percent;
  if (point.samples === 0 || signal == null) return "Sem dados";
  const loss = point.gateway_loss_percent ?? 0;
  if (signal >= 70 && loss < 5) return "Bom";
  if (signal >= 45 && loss < 15) return "Regular";
  return "Fraco";
}

const gradeOrder: Record<LocationGrade, number> = {
  Bom: 0,
  Regular: 1,
  Fraco: 2,
  "Sem dados": 3,
};

/** Points ordered best first; ungraded points last, ties by signal then name. */
export function rankLocations<T extends { location: string; summary: Summary }>(
  points: T[],
): T[] {
  return [...points].sort(
    (a, b) =>
      gradeOrder[locationGrade(a.summary)] -
        gradeOrder[locationGrade(b.summary)] ||
      (b.summary.signal_mean_percent ?? -1) -
        (a.summary.signal_mean_percent ?? -1) ||
      a.location.localeCompare(b.location),
  );
}

export const webhookStatusSchema = z.object({
  configured: z.boolean(),
  destination: z.string().nullable(),
  interval_seconds: z.number().positive(),
  active_alerts: z.number().int().nonnegative(),
  cycles: z.number().int().nonnegative(),
  last_error: z.string().nullable(),
  mode: z.literal("ADVISORY"),
  deliveries: z
    .array(
      z.object({
        id: z.guid(),
        created_at: z.iso.datetime({ offset: true }),
        event: z.enum(["alert.raised", "alert.cleared", "webhook.test"]),
        alert_code: z.string().nullable(),
        location: z.string().nullable(),
        delivered: z.boolean(),
        http_status: z.number().int().nullable(),
        error: z.string().nullable(),
      }),
    )
    .max(20),
});
export type WebhookStatus = z.infer<typeof webhookStatusSchema>;
