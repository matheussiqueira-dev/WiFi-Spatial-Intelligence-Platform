import assert from "node:assert/strict";
import { test } from "node:test";
import { networkSampleSchema, locationSchema } from "../src/lib/network";

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
