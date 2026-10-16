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
