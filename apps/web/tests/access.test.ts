import assert from "node:assert/strict";
import { test } from "node:test";
import {
  allows,
  identityLabel,
  identitySchema,
  tokenCreatedSchema,
  tokenListSchema,
} from "../src/lib/access";

const view = {
  id: "00000000-0000-4000-8000-000000000001",
  label: "Ana",
  role: "operator",
  created_at: "2026-10-17T10:00:00+00:00",
  revoked_at: null,
  last_used_at: null,
  active: true,
};

test("role hierarchy matches the API and refuses when disconnected", () => {
  assert.ok(allows("admin", "operator"));
  assert.ok(allows("operator", "operator"));
  assert.ok(allows("viewer", "viewer"));
  assert.ok(!allows("viewer", "operator"));
  assert.ok(!allows("operator", "admin"));
  assert.ok(!allows(null, "viewer"));
});

test("token listing never accepts a token value or unknown role", () => {
  assert.ok(
    tokenListSchema.safeParse({ items: [view], maximum_active: 50 }).success,
  );
  // Strip unknown keys is zod's default; the listing type has no token field at all.
  const parsed = tokenListSchema.parse({
    items: [{ ...view, token: "wsp_leak" }],
    maximum_active: 50,
  });
  assert.equal("token" in parsed.items[0], false);
  assert.ok(
    !tokenListSchema.safeParse({
      items: [{ ...view, role: "root" }],
      maximum_active: 50,
    }).success,
  );
});

test("created token must carry the personal prefix", () => {
  assert.ok(
    tokenCreatedSchema.safeParse({ ...view, token: "wsp_" + "a".repeat(43) })
      .success,
  );
  assert.ok(
    !tokenCreatedSchema.safeParse({ ...view, token: "x".repeat(47) }).success,
  );
});

test("identity label names the role and hides the bootstrap secret", () => {
  const bootstrap = identitySchema.parse({
    subject_id: "bootstrap",
    label: "SPATIAL_TOKEN",
    role: "admin",
    bootstrap: true,
  });
  assert.equal(identityLabel(bootstrap), "Administração · token de bootstrap");
  assert.equal(
    identityLabel({
      ...bootstrap,
      label: "Ana",
      role: "viewer",
      bootstrap: false,
    }),
    "Leitura · Ana",
  );
});
