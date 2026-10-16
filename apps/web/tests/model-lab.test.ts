import assert from "node:assert/strict";
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { experimentSchema } from "../src/lib/model-lab";

test("experiment fixture validates L0 and rejects invented evidence and malformed metrics", () => {
  const fixture = JSON.parse(
    readFileSync(
      new URL(
        "../../../packages/contracts/experiment-result.example.json",
        import.meta.url,
      ),
      "utf8",
    ),
  );
  const result = experimentSchema.parse(fixture);
  assert.equal(result.evaluation.samples, 32);
  assert.equal(result.evaluation.rejected, 8);
  assert.equal(
    experimentSchema.safeParse({
      ...result,
      evidence_level: "L3_REFERENCE_VALIDATED",
    }).success,
    false,
  );
  assert.equal(
    experimentSchema.safeParse({
      ...result,
      evaluation: { ...result.evaluation, accuracy_accepted: 2 },
    }).success,
    false,
  );
});
