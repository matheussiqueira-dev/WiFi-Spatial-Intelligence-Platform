import assert from "node:assert/strict";
import { test } from "node:test";
import {
  evaluationRows,
  fingerprintEvaluationSchema,
  modelRegistrySchema,
} from "../src/lib/rf-lab";

const evaluation = {
  method: "rf-fingerprint-zscore-v1",
  evidence_level: "L0_SYNTHETIC",
  transport: "SWF1",
  seed: 42,
  fingerprint_sha256: "c".repeat(64),
  reference_frames: 400,
  window_frames: 20,
  min_frames: 12,
  subcarriers: 64,
  threshold: 1.5,
  reference_scores_max: 1,
  normal_windows: 40,
  false_positives: 0,
  false_positive_rate: 0,
  changed_windows: 40,
  detections: 40,
  detection_rate: 1,
  subtle_windows: 40,
  subtle_detection_rate: 0,
  other_environment_windows: 10,
  other_environment_detection_rate: 1,
  sparse_windows: 10,
  abstained: 10,
  frames_received: 2700,
  limitations: ["Canal sintético"],
};

test("fingerprint evaluation is L0 only and always carries limitations", () => {
  assert.ok(fingerprintEvaluationSchema.safeParse(evaluation).success);
  for (const changed of [
    { evidence_level: "L2_LIVE_UNVALIDATED" },
    { limitations: [] },
    { detection_rate: 1.2 },
  ])
    assert.equal(
      fingerprintEvaluationSchema.safeParse({ ...evaluation, ...changed })
        .success,
      false,
    );
});

test("evaluation rows keep the subtle-change blind spot visible", () => {
  const rows = evaluationRows(fingerprintEvaluationSchema.parse(evaluation));
  assert.equal(rows.length, 5);
  assert.deepEqual(
    rows.find((row) => row.label === "Mudanças sutis detectadas")?.value,
    "0% de 40 janelas",
  );
});

test("registry never accepts a loaded third-party model or non-https source", () => {
  const card = {
    id: "00000000-0000-4000-8000-000000000001",
    created_at: "2026-10-21T00:00:00+00:00",
    origin: "third_party",
    name: "x",
    version: "1",
    license: "MIT",
    source_url: "https://example.org/x",
    sha256: "a".repeat(64),
    intended_use: "teste",
    commercial_use: "ALLOWED",
    status: "NOT_LOADED",
    evidence_level: "UNVERIFIED",
  };
  const registry = {
    project: [],
    third_party: [card],
    maximum_third_party: 50,
  };
  assert.ok(modelRegistrySchema.safeParse(registry).success);
  for (const changed of [{ status: "LOADED" }, { source_url: "http://x" }])
    assert.equal(
      modelRegistrySchema.safeParse({
        ...registry,
        third_party: [{ ...card, ...changed }],
      }).success,
      false,
    );
});
