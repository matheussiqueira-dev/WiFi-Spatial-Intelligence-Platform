import { z } from "zod";

export const ruleSchema = z.object({
  id: z.uuid(),
  name: z.string().min(1).max(60),
  field: z.enum(["presence", "occupancy"]),
  threshold: z.number().int().min(0).max(20),
  active: z.boolean(),
  version: z.literal(1),
  mode: z.literal("DRY_RUN"),
});
export const rulesSchema = z.object({
  items: z.array(ruleSchema).max(20),
  maximum_rules: z.literal(20),
  maximum_decisions: z.literal(1000),
  decision_capacity_reached: z.boolean(),
});
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
