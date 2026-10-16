import assert from "node:assert/strict";
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { analyticsSchema } from "../src/lib/analytics";

const fixture: unknown = JSON.parse(
  readFileSync(
    new URL(
      "../../../packages/contracts/analytics-report.example.json",
      import.meta.url,
    ),
    "utf8",
  ),
);
test("Python analytics fixture validates without promoting synthetic evidence", () => {
  const report = analyticsSchema.parse(fixture);
  assert.equal(report.summary.samples, 1);
  assert.equal(report.summary.rf_drop_rate, null);
  assert.equal(report.summary.event_rate, null);
  assert.equal(report.summary.entries_estimate, 0);
  assert.equal(
    analyticsSchema.safeParse({ ...report, evidence_level: "L3_VALIDATED" })
      .success,
    false,
  );
  assert.equal(
    analyticsSchema.safeParse({
      ...report,
      summary: { ...report.summary, samples: -1 },
    }).success,
    false,
  );
});

test("local DST offsets convert to consecutive UTC instants, not a missing historical hour", () => {
  const before = new Date("2026-03-08T01:59:59-05:00");
  const after = new Date("2026-03-08T03:00:00-04:00");
  assert.equal(after.getTime() - before.getTime(), 1000);
  const report = analyticsSchema.parse(fixture);
  assert.equal(
    analyticsSchema.safeParse({
      ...report,
      query: { ...report.query, start: "2026-03-08T01:59:59-05:00" },
    }).success,
    false,
  );
});
