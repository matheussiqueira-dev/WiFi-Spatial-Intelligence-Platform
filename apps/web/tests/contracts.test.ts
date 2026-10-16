import assert from "node:assert/strict";
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { analyticsSchema, replaySchema } from "../src/lib/analytics";
import { configSchema, eventSchema, streamSchema } from "../src/lib/contracts";

const sample: unknown = JSON.parse(
  readFileSync(
    new URL(
      "../../../packages/contracts/synthetic-event.example.json",
      import.meta.url,
    ),
    "utf8",
  ),
);

test("accepts the event fixture exported by the Python contract", () => {
  const parsed = eventSchema.parse(sample);
  assert.equal(parsed.evidence_level, "L0_SYNTHETIC");
  assert.equal(parsed.model.id, null);
  assert.equal(parsed.quality.confidence, null);
  assert.equal(
    streamSchema.parse({ type: "event", data: sample }).type,
    "event",
  );
});
test("rejects real evidence, fabricated inference, and unbounded positions", () => {
  const parsed = eventSchema.parse(sample);
  assert.equal(
    eventSchema.safeParse({ ...parsed, evidence_level: "L3_VALIDATED" })
      .success,
    false,
  );
  assert.equal(
    eventSchema.safeParse({ ...parsed, model: { id: "fake", version: null } })
      .success,
    false,
  );
  assert.equal(
    eventSchema.safeParse({
      ...parsed,
      measurements: {
        ...parsed.measurements,
        ground_truth_positions: [[99, 0]],
      },
    }).success,
    false,
  );
  assert.equal(
    eventSchema.safeParse({
      ...parsed,
      measurements: { ...parsed.measurements, presence_detected: false },
    }).success,
    false,
  );
});
test("rejects malformed streams and invalid simulation configuration", () => {
  assert.equal(
    streamSchema.safeParse({ type: "event", data: {} }).success,
    false,
  );
  for (const config of [
    { occupants: 21 },
    { scenario: "real" },
    { speed: Number.NaN },
    { seed: -1 },
  ]) {
    assert.equal(
      configSchema.safeParse({
        scenario: "walking",
        seed: 42,
        occupants: 2,
        speed: 1,
        ...config,
      }).success,
      false,
    );
  }
});

test("accepts the additive RuView fixture without altering the internal contract", () => {
  const raw: unknown = JSON.parse(
    readFileSync(
      new URL(
        "../../../packages/contracts/ruview-event.example.json",
        import.meta.url,
      ),
      "utf8",
    ),
  );
  const event = eventSchema.parse(raw);
  assert.equal(event.source_id, "ruview-01");
  assert.equal(event.evidence_level, "L0_SYNTHETIC");
  assert.deepEqual(event.measurements.ground_truth_positions, []);
  assert.equal(event.provenance.seed, null);
  assert.equal(
    streamSchema.parse({ type: "event", data: event }).type,
    "event",
  );
  for (const patch of [
    { source_type: "REAL" },
    { evidence_level: "L1_MEASURED" },
    { model: { id: "unvalidated", version: null } },
    {
      measurements: { ...event.measurements, ground_truth_positions: [[1, 1]] },
    },
    { measurements: { ...event.measurements, presence_detected: false } },
    { provenance: { ...event.provenance, upstream_source: "esp32" } },
  ])
    assert.equal(eventSchema.safeParse({ ...event, ...patch }).success, false);
  assert.equal(
    eventSchema.safeParse({
      ...event,
      measurements: {
        ...event.measurements,
        occupancy_estimate: null,
      },
    }).success,
    true,
  );
});

const fixture = (name: string): unknown =>
  JSON.parse(
    readFileSync(
      new URL(`../../../packages/contracts/${name}`, import.meta.url),
      "utf8",
    ),
  );

test("accepts every event id shape the backend UUID type accepts", () => {
  for (const name of [
    "synthetic-event.example.json",
    "ruview-event.example.json",
    "native-event.example.json",
  ]) {
    const event = eventSchema.parse(fixture(name));
    assert.equal(
      eventSchema.safeParse({
        ...event,
        event_id: "00000000-0000-0000-0000-000000000001",
      }).success,
      true,
    );
    assert.equal(
      eventSchema.safeParse({ ...event, event_id: "not-a-uuid" }).success,
      false,
    );
  }
});

test("legacy provenance keeps backend tolerance while native v2 stays strict", () => {
  const legacy = eventSchema.parse(fixture("synthetic-event.example.json"));
  assert.equal(
    eventSchema.safeParse({
      ...legacy,
      provenance: { ...legacy.provenance, dataset_id: "ds-1", seed: 2 ** 60 },
    }).success,
    true,
  );
  const native = eventSchema.parse(fixture("native-event.example.json"));
  for (const patch of [
    { dataset_id: "ds-1" },
    { seed: -1 },
    { seed: 2 ** 32 },
    { scenario: "custom" },
  ])
    assert.equal(
      eventSchema.safeParse({
        ...native,
        provenance: { ...native.provenance, ...patch },
      }).success,
      false,
    );
});

test("event union reports issues from the declared schema version only", () => {
  const native = eventSchema.parse(fixture("native-event.example.json"));
  const result = eventSchema.safeParse({
    ...native,
    measurements: { ...native.measurements, occupancy_estimate: -1 },
  });
  assert.equal(result.success, false);
  assert.deepEqual(
    result.error?.issues.map((issue) => issue.path.join(".")),
    ["measurements.occupancy_estimate"],
  );
  assert.equal(
    eventSchema.safeParse({ ...native, schema_version: "9.9.9" }).success,
    false,
  );
});

test("golden analytics fixtures exercise intervals, transitions and replay", () => {
  const report = analyticsSchema.parse(
    fixture("analytics-native-report.example.json"),
  );
  assert.deepEqual(
    [...new Set(report.intervals.items.map((item) => item.state))].sort(),
    ["absent", "present", "unknown"],
  );
  assert.ok(report.transitions.items.length > 0);
  assert.ok(report.summary.entries_estimate > 0);
  assert.ok(report.summary.unknown_count_samples > 0);
  const replay = replaySchema.parse(fixture("analytics-replay.example.json"));
  assert.deepEqual(
    [
      ...new Set(replay.items.map((item) => item.event.schema_version)),
    ].sort(),
    ["1.0.0", "1.1.0", "2.0.0"],
  );
});
