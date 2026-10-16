import assert from "node:assert/strict";
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { eventSchema } from "../src/lib/contracts";

test("native v2 contract preserves evidence and reads alongside legacy versions", () => {
  const raw: unknown = JSON.parse(
    readFileSync(
      new URL(
        "../../../packages/contracts/native-event.example.json",
        import.meta.url,
      ),
      "utf8",
    ),
  );
  const event = eventSchema.parse(raw);
  assert.equal(event.source_id, "native-01");
  assert.equal(event.evidence_level, "L0_SYNTHETIC");
  assert.equal(event.provenance.generator, "synthetic-native");
  assert.equal(
    eventSchema.safeParse({
      ...event,
      evidence_level: "L3_REFERENCE_VALIDATED",
    }).success,
    false,
  );
  assert.equal(
    eventSchema.safeParse({
      ...event,
      measurements: { ...event.measurements, presence_detected: false },
    }).success,
    false,
  );
});
