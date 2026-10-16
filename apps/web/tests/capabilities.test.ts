import assert from "node:assert/strict";
import { test } from "node:test";
import { readFileSync } from "node:fs";
import {
  capabilityCatalogSchema,
  enabledCapabilities,
} from "../src/lib/capabilities";
import { channelAdvice, channelPlanSchema } from "../src/lib/network";

test("capability catalog fixture parses and keeps blocked identity disabled", () => {
  const fixture = JSON.parse(
    readFileSync(
      new URL(
        "../../../packages/contracts/capability-catalog.example.json",
        import.meta.url,
      ),
      "utf8",
    ),
  );
  const catalog = capabilityCatalogSchema.parse(fixture);
  assert.equal(catalog.profile, "lab");
  const identity = catalog.capabilities.find(
    (item) => item.id === "identity.rf_reidentification",
  );
  assert.equal(identity?.status, "BLOCKED");
  assert.equal(identity?.enabled, false);
  assert.ok(
    catalog.capabilities.some((item) => item.group === "A" && item.enabled),
  );
  assert.equal(
    capabilityCatalogSchema.safeParse({
      ...catalog,
      capabilities: [{ ...catalog.capabilities[0], regulatory: ["FDA"] }],
    }).success,
    false,
  );
});

test("channel plan schema and advice text", () => {
  const band = {
    band: "5GHz" as const,
    observed: [],
    candidates: [
      { channel: 36, observed_ap_count: 0, interference_score: 0 },
      { channel: 149, observed_ap_count: 3, interference_score: 2.1 },
    ],
    current_channel: 149,
    current_score: 2.1,
    recommended_channel: 36,
    advice: "CONSIDER_CHANGE" as const,
  };
  const plan = channelPlanSchema.parse({
    data_class: "HOST_NETWORK_TELEMETRY",
    evidence_level: "L2_LIVE_UNVALIDATED",
    start: "2026-10-15T00:00:00Z",
    end: "2026-10-15T01:00:00Z",
    location: null,
    surveys: 1,
    failed_surveys: 0,
    last_survey_at: "2026-10-15T00:59:00Z",
    bands: [band],
    limitations: [],
  });
  assert.match(channelAdvice(plan.bands[0]), /canal 36/);
  assert.match(
    channelAdvice({ ...band, advice: "KEEP", recommended_channel: 149 }),
    /Manter o canal 149/,
  );
  assert.match(
    channelAdvice({ ...band, advice: "NO_CURRENT", recommended_channel: null }),
    /Sem varreduras/,
  );
  assert.equal(
    channelPlanSchema.safeParse({
      ...plan,
      evidence_level: "L3_REFERENCE_VALIDATED",
    }).success,
    false,
  );
});

test("enabled set follows the profile and never contains blocked identity", () => {
  const catalog = capabilityCatalogSchema.parse(
    JSON.parse(
      readFileSync(
        new URL(
          "../../../packages/contracts/capability-catalog.example.json",
          import.meta.url,
        ),
        "utf8",
      ),
    ),
  );
  const enabled = enabledCapabilities(catalog);
  assert.equal(enabled.has("network.link_diagnostics"), true);
  assert.equal(enabled.has("identity.rf_reidentification"), false);
  const commercial = enabledCapabilities({
    ...catalog,
    profile: "commercial-br",
    capabilities: catalog.capabilities.map((item) => ({
      ...item,
      enabled: item.enabled && item.profiles.includes("commercial-br"),
    })),
  });
  assert.equal(commercial.has("spatial.presence"), false);
  assert.equal(commercial.has("network.channel_plan"), true);
});
