import { z } from "zod";

export const roles = ["viewer", "operator", "admin"] as const;
export const roleSchema = z.enum(roles);
export type Role = z.infer<typeof roleSchema>;

export const roleLabels: Record<Role, string> = {
  viewer: "Leitura",
  operator: "Operação",
  admin: "Administração",
};

/** Same hierarchy as the API; hiding a control is convenience, the API still refuses. */
export function allows(role: Role | null, minimum: Role): boolean {
  return role !== null && roles.indexOf(role) >= roles.indexOf(minimum);
}

export const identitySchema = z.object({
  subject_id: z.string().min(1).max(36),
  label: z.string().min(1).max(48),
  role: roleSchema,
  bootstrap: z.boolean(),
});
export type Identity = z.infer<typeof identitySchema>;

const timestamp = z.iso.datetime({ offset: true });
export const tokenViewSchema = z.object({
  id: z.uuid(),
  label: z.string().min(1).max(48),
  role: roleSchema,
  created_at: timestamp,
  revoked_at: timestamp.nullable(),
  last_used_at: timestamp.nullable(),
  active: z.boolean(),
});
export type TokenView = z.infer<typeof tokenViewSchema>;
export const tokenListSchema = z.object({
  items: z.array(tokenViewSchema).max(500),
  maximum_active: z.number().int().positive(),
});
// The one response that carries a token value; it is shown once and never stored.
export const tokenCreatedSchema = tokenViewSchema.extend({
  token: z.string().startsWith("wsp_").min(32).max(128),
});

export function identityLabel(identity: Identity): string {
  const who = identity.bootstrap ? "token de bootstrap" : identity.label;
  return `${roleLabels[identity.role]} · ${who}`;
}
