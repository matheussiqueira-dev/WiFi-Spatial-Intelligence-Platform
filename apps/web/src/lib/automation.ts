import { z } from "zod";

export const ruleSchema = z.object({
  id: z.uuid(),
  name: z.string().min(1).max(60),
  field: z.enum(["presence", "occupancy"]),
  threshold: z.number().int().min(0).max(20),
  active: z.boolean(),
  version: z.literal(1),
  mode: z.literal("DRY_RUN"),
  // null for rules created before migration 0009 (time unknown, never backfilled).
  created_at: z.iso.datetime({ offset: true }).nullable(),
  revoked_at: z.iso.datetime({ offset: true }).nullable(),
});
export const rulesSchema = z.object({
  items: z.array(ruleSchema).max(20),
  maximum_rules: z.literal(20),
  maximum_decisions: z.literal(1000),
  decision_capacity_reached: z.boolean(),
});
type RuleTimes = Pick<z.infer<typeof ruleSchema>, "created_at" | "revoked_at">;

/** Human-readable lifecycle; pre-0009 rules say so instead of inventing a date. */
export function ruleTimeline(rule: RuleTimes, format = formatTime): string {
  const created = rule.created_at
    ? `criada ${format(rule.created_at)}`
    : "criação anterior ao histórico";
  return rule.revoked_at
    ? `${created} · revogada ${format(rule.revoked_at)}`
    : created;
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleString("pt-BR");
}

export const decisionsSchema = z.object({
  items: z.array(
    z.object({
      id: z.uuid(),
      rule_id: z.uuid(),
      event_id: z.uuid(),
      created_at: z.string(),
      rule_version: z.literal(1),
      matched: z.boolean(),
      mode: z.literal("DRY_RUN"),
      evidence_level: z.literal("L0_SYNTHETIC"),
      dispatched: z.literal(false),
    }),
  ),
  total: z.number().int().nonnegative(),
  limit: z.number().int(),
  offset: z.number().int(),
});
