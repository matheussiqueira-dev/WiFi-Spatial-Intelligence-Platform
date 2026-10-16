import assert from "node:assert/strict";
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import Observatory from "../src/components/observatory";
import { eventSchema } from "../src/lib/contracts";

const sample: unknown = JSON.parse(
  readFileSync(
    new URL(
      "../../../packages/contracts/ruview-event.example.json",
      import.meta.url,
    ),
    "utf8",
  ),
);

test("RuView accessible map preserves unknown counts and unavailable positions", () => {
  const event = eventSchema.parse(sample);
  const unknown = eventSchema.parse({
    ...event,
    measurements: { ...event.measurements, occupancy_estimate: null },
  });
  const html = renderToStaticMarkup(
    createElement(Observatory, {
      event: unknown,
      sensors: [],
      connected: true,
    }),
  );
  assert.match(html, /contagem indisponível/);
  assert.match(html, /posições indisponíveis/);
  assert.doesNotMatch(html, /0 ocupantes|data-testid="occupant"/);
});

test("accessible map distinguishes missing observation from an empty scene", () => {
  const html = renderToStaticMarkup(
    createElement(Observatory, { event: null, sensors: [], connected: false }),
  );
  assert.match(html, /sem observação/);
  assert.doesNotMatch(html, /0 ocupantes/);
});

test("RuView accessible count remains an estimate over synthetic signals", () => {
  const html = renderToStaticMarkup(
    createElement(Observatory, {
      event: eventSchema.parse(sample),
      sensors: [],
      connected: true,
    }),
  );
  assert.match(html, /ocupantes estimados em sinais sintéticos/);
  assert.match(html, /posições indisponíveis/);
  assert.doesNotMatch(html, /data-testid="occupant"/);
});

test("native observations render human rigs without changing the number of occupants", () => {
  const event = eventSchema.parse(
    JSON.parse(
      readFileSync(
        new URL(
          "../../../packages/contracts/native-event.example.json",
          import.meta.url,
        ),
        "utf8",
      ),
    ),
  );
  const html = renderToStaticMarkup(
    createElement(Observatory, { event, sensors: [], connected: true }),
  );
  assert.equal(
    (html.match(/data-testid="occupant"/g) ?? []).length,
    event.measurements.ground_truth_positions.length,
  );
  assert.equal(
    (html.match(/data-joint=/g) ?? []).length,
    event.measurements.ground_truth_positions.length * 17,
  );
  assert.match(html, /Pose procedural/);
  assert.match(html, /Avatares da cena/);
  assert.match(html, /não altera os dados/);
  assert.doesNotMatch(html, /L3_REFERENCE_VALIDATED/);
});
