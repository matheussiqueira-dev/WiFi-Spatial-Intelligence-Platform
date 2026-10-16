import { z } from "zod";

export const regulatoryLabels = {
  NONE: "Sem enquadramento específico",
  LGPD_PERSONAL: "LGPD — dado pessoal",
  LGPD_SENSITIVE: "LGPD — dado sensível",
  ANATEL_RADIO: "Anatel — hardware de rádio",
  ANVISA_SAMD: "ANVISA — software médico",
} as const;
export const groupLabels = {
  A: "A · Rede",
  B: "B · Ambiente",
  C: "C · Saúde e segurança",
  D: "D · Identificação",
} as const;
const profile = z.enum(["lab", "commercial-br"]);
export const capabilityCatalogSchema = z.object({
  profile,
  disclaimer: z.string(),
  capabilities: z
    .array(
      z.object({
        id: z.string().regex(/^[a-z0-9_.]+$/),
        name: z.string(),
        group: z.enum(["A", "B", "C", "D"]),
        status: z.enum([
          "UNVERIFIED",
          "PARTIAL",
          "IMPLEMENTED_SYNTHETIC",
          "IMPLEMENTED_LIVE",
          "INTEGRATED_LEGACY",
          "VALIDATED_REAL_DATA",
          "PLANNED",
          "BLOCKED",
        ]),
        evidence_ceiling: z
          .enum([
            "L0_SYNTHETIC",
            "L1_RECORDED_UNVALIDATED",
            "L2_LIVE_UNVALIDATED",
            "L3_REFERENCE_VALIDATED",
          ])
          .nullable(),
        regulatory: z.array(
          z.enum([
            "NONE",
            "LGPD_PERSONAL",
            "LGPD_SENSITIVE",
            "ANATEL_RADIO",
            "ANVISA_SAMD",
          ]),
        ),
        requires_hardware: z.boolean(),
        requires_consent: z.boolean(),
        profiles: z.array(profile),
        endpoint: z.string().startsWith("/api/v1/").nullable(),
        note: z.string(),
        enabled: z.boolean(),
      }),
    )
    .max(200),
});
export type CapabilityCatalog = z.infer<typeof capabilityCatalogSchema>;

/** Capabilities the active profile enables; the API refuses the others with 403. */
export function enabledCapabilities(catalog: CapabilityCatalog) {
  return new Set(
    catalog.capabilities.filter((item) => item.enabled).map((item) => item.id),
  );
}
