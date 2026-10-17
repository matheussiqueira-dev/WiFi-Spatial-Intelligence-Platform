import assert from "node:assert/strict";
import { test } from "node:test";
import {
  locationGrade,
  locationSchema,
  networkHealthSchema,
  networkSampleSchema,
  rankLocations,
  webhookStatusSchema,
} from "../src/lib/network";

test("network contract never accepts synthetic evidence or a fabricated quality percentage", () => {
  const fixture = {
    schema_version: "1.0.0",
    data_class: "HOST_NETWORK_TELEMETRY",
    evidence_level: "L2_LIVE_UNVALIDATED",
    source: "windows-netsh",
    sample_id: "00000000-0000-4000-8000-000000000001",
    collector_id: "00000000-0000-4000-8000-000000000002",
    timestamp: "2026-01-01T00:00:00Z",
    location: "Fixture",
    link_state: "CONNECTED",
    signal_percent: 88,
    channel: 149,
    radio_type: "802.11ac",
    rx_mbps: 433.3,
    tx_mbps: 433.3,
    probe_sent: 3,
    probe_rtt_ms: [1, 2],
    probe_status: "COMPLETED",
    collector_error: null,
  };
  assert.equal(networkSampleSchema.safeParse(fixture).success, true);
  assert.equal(
    networkSampleSchema.safeParse({
      ...fixture,
      evidence_level: "L0_SYNTHETIC",
    }).success,
    false,
  );
  assert.equal(
    networkSampleSchema.safeParse({ ...fixture, signal_percent: 101 }).success,
    false,
  );
  assert.equal(locationSchema.safeParse("=SUM(A1)").success, false);
  assert.equal(locationSchema.safeParse("Escritório 2").success, true);
});

const point = (signal: number | null, loss: number | null, samples = 10) => ({
  samples,
  connected_samples: samples,
  disconnected_samples: 0,
  unavailable_samples: 0,
  connected_percent: 100,
  signal_mean_percent: signal,
  signal_min_percent: signal,
  gateway_mean_ms: 2,
  gateway_p95_ms: 3,
  gateway_loss_percent: loss,
  disconnect_events: 0,
  missing_seconds: 0,
  last_seen: "2026-10-17T12:00:00Z",
  collector_stale: false,
});

test("location grade uses signal and loss, and never grades a point without data", () => {
  assert.equal(locationGrade(point(80, 0)), "Bom");
  assert.equal(locationGrade(point(80, 10)), "Regular");
  assert.equal(locationGrade(point(50, null)), "Regular");
  assert.equal(locationGrade(point(30, 0)), "Fraco");
  assert.equal(locationGrade(point(90, 20)), "Fraco");
  assert.equal(locationGrade(point(null, 0)), "Sem dados");
  assert.equal(locationGrade(point(90, 0, 0)), "Sem dados");
});

test("ranking puts the best point first and unmeasured points last", () => {
  const ranked = rankLocations([
    { location: "Quarto", summary: point(null, null, 0) },
    { location: "Sala", summary: point(50, 0) },
    { location: "Escritório", summary: point(85, 0) },
    { location: "Cozinha", summary: point(75, 0) },
  ]);
  assert.deepEqual(
    ranked.map((item) => item.location),
    ["Escritório", "Cozinha", "Sala", "Quarto"],
  );
});

test("health contract is advisory and rejects unknown alert codes", () => {
  const body = {
    data_class: "HOST_NETWORK_TELEMETRY",
    evidence_level: "L2_LIVE_UNVALIDATED",
    mode: "ADVISORY",
    start: "2026-10-16T12:00:00Z",
    end: "2026-10-17T12:00:00Z",
    location: null,
    bucket_minutes: 60,
    buckets: [],
    recent: point(80, 0),
    baseline: point(80, 0),
    alerts: [
      {
        code: "SIGNAL_DROP",
        severity: "warning",
        metric: "signal_mean_percent",
        recent: 60,
        baseline: 80,
        threshold: 15,
        message: "Sinal caiu",
      },
    ],
    abstentions: [],
  };
  assert.ok(networkHealthSchema.safeParse(body).success);
  assert.equal(
    networkHealthSchema.safeParse({ ...body, mode: "DISPATCH" }).success,
    false,
  );
  assert.equal(
    networkHealthSchema.safeParse({
      ...body,
      alerts: [{ ...body.alerts[0], code: "INTRUDER" }],
    }).success,
    false,
  );
});

test("webhook status never needs the receiver path and rejects unknown events", () => {
  const status = {
    configured: true,
    destination: "http://192.168.1.5:8123",
    interval_seconds: 60,
    active_alerts: 1,
    cycles: 3,
    last_error: null,
    mode: "ADVISORY",
    deliveries: [
      {
        id: "00000000-0000-4000-8000-000000000009",
        created_at: "2026-10-17T12:00:00+00:00",
        event: "alert.raised",
        alert_code: "SIGNAL_DROP",
        location: "Sala",
        delivered: false,
        http_status: null,
        error: "timeout",
      },
    ],
  };
  assert.ok(webhookStatusSchema.safeParse(status).success);
  assert.equal(
    webhookStatusSchema.safeParse({
      ...status,
      deliveries: [{ ...status.deliveries[0], event: "shell.exec" }],
    }).success,
    false,
  );
});
