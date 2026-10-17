import assert from "node:assert/strict";
import { test } from "node:test";
import { ruleSchema, ruleTimeline } from "../src/lib/automation";

const base = {
  id: "00000000-0000-4000-8000-000000000001",
  name: "Sala ocupada",
  field: "occupancy",
  threshold: 2,
  active: true,
  version: 1,
  mode: "DRY_RUN",
};

test("rule contract accepts pre-history rules and rejects local timestamps", () => {
  assert.ok(
    ruleSchema.safeParse({ ...base, created_at: null, revoked_at: null })
      .success,
  );
  const created = "2026-10-16T10:00:00+00:00";
  assert.ok(
    ruleSchema.safeParse({ ...base, created_at: created, revoked_at: null })
      .success,
  );
  assert.equal(
    ruleSchema.safeParse({ ...base, created_at: "16/10/2026" }).success,
    false,
  );
  assert.equal(ruleSchema.safeParse(base).success, false);
});

test("timeline never invents a creation date and appends revocation", () => {
  const format = (iso: string) => `<${iso}>`;
  assert.equal(
    ruleTimeline({ created_at: null, revoked_at: null }, format),
    "criação anterior ao histórico",
  );
  assert.equal(
    ruleTimeline({ created_at: "a", revoked_at: "b" }, format),
    "criada <a> · revogada <b>",
  );
});
