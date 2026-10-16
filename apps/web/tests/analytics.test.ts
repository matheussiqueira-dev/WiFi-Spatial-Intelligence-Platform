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

import {
  analyticsParams,
  collectReplay,
  occupancyBar,
  pageParams,
} from "../src/lib/analytics";

const filters = {
  start: "2026-10-15T10:00",
  end: "",
  bucket: "minute",
  source: "",
  scenario: "walking",
  segment: "",
};

test("applied analytics query freezes 'now' so pagination keeps the same window", () => {
  const now = new Date("2026-10-15T15:00:00Z");
  const base = analyticsParams(filters, now);
  assert.equal(base.get("end"), "2026-10-15T15:00:00.000Z");
  assert.equal(base.get("scenario"), "walking");
  assert.equal(base.has("offset"), false);
  const second = pageParams(base.toString(), 100);
  assert.equal(second.get("end"), base.get("end"));
  assert.equal(second.get("offset"), "100");
  assert.equal(second.get("limit"), "100");
});

test("invalid analytics dates fail with a Portuguese message, not a RangeError", () => {
  assert.throws(
    () => analyticsParams({ ...filters, start: "" }),
    /Informe a data inicial/,
  );
  assert.throws(
    () => analyticsParams({ ...filters, end: "invalid" }),
    /data final/,
  );
});

test("replay collection stops when retention changes the selection mid-load", async () => {
  const totals = [450, 450, 449];
  let call = 0;
  await assert.rejects(
    collectReplay(async (offset) => ({
      items: Array.from(
        { length: Math.min(200, 450 - offset) },
        (_, i) => offset + i,
      ),
      total: totals[call++],
    })),
    /histórico mudou durante a carga/,
  );
  const frames = await collectReplay(async (offset) => ({
    items: Array.from(
      { length: Math.min(200, 450 - offset) },
      (_, i) => offset + i,
    ),
    total: 450,
  }));
  assert.equal(frames.length, 450);
  assert.deepEqual(frames.slice(198, 202), [198, 199, 200, 201]);
});

test("occupancy bars never draw an unknown count as zero", () => {
  assert.deepEqual(occupancyBar(null), { kind: "unknown", height: "100%" });
  assert.deepEqual(occupancyBar(0), { kind: "zero", height: "0%" });
  assert.deepEqual(occupancyBar(0.4), { kind: "value", height: "4%" });
  assert.deepEqual(occupancyBar(10), { kind: "value", height: "50%" });
});
