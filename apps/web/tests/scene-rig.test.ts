import assert from "node:assert/strict";
import { test } from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { readFileSync } from "node:fs";
import ArticulatedScene from "../src/components/articulated-scene";
import { eventSchema } from "../src/lib/contracts";
import { avatarKind, buildRig } from "../src/lib/scene-rig";

const sample = eventSchema.parse(
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
test("visual cast only changes illustrations; positions and evidence stay untouched", () => {
  const original = JSON.stringify(sample);
  for (const cast of ["human", "dog", "cat", "mixed"] as const) {
    const html = renderToStaticMarkup(
      createElement(ArticulatedScene, {
        event: sample,
        sensors: [],
        connected: true,
        cast,
        articulate: true,
        gridId: "test-gradient",
      }),
    );
    assert.equal(
      (html.match(/data-testid="occupant"/g) ?? []).length,
      sample.measurements.ground_truth_positions.length,
    );
    assert.match(html, /Aparência selecionada, não inferida/);
    if (cast !== "mixed")
      assert.equal(
        (html.match(new RegExp(`data-avatar="${cast}"`, "g")) ?? []).length,
        sample.measurements.ground_truth_positions.length,
      );
  }
  assert.equal(JSON.stringify(sample), original);
  assert.deepEqual(
    [0, 1, 2, 3].map((index) => avatarKind("mixed", index)),
    ["human", "dog", "cat", "human"],
  );
});

test("rigs are deterministic, finite, grounded and contain no dangling bones", () => {
  for (const kind of ["human", "dog", "cat"] as const) {
    for (const phase of [0, 1, 2, 100000]) {
      const rig = buildRig(kind, phase);
      assert.deepEqual(rig, buildRig(kind, phase));
      assert.ok(
        rig.points.every(
          (point) => point.every(Number.isFinite) && point[2] >= 0,
        ),
      );
      assert.ok(
        rig.edges.every(
          ([a, b]) => a < rig.points.length && b < rig.points.length && a !== b,
        ),
      );
    }
    assert.notDeepEqual(buildRig(kind, 0).points, buildRig(kind, 1).points);
  }
  assert.equal(buildRig("human", 0).points.length, 17);
});

test("no rig is invented for unavailable RuView positions", () => {
  const event = eventSchema.parse(
    JSON.parse(
      readFileSync(
        new URL(
          "../../../packages/contracts/ruview-event.example.json",
          import.meta.url,
        ),
        "utf8",
      ),
    ),
  );
  const html = renderToStaticMarkup(
    createElement(ArticulatedScene, {
      event,
      sensors: [],
      connected: true,
      cast: "mixed",
      articulate: true,
      gridId: "test-gradient",
    }),
  );
  assert.doesNotMatch(html, /data-testid="occupant"/);
  assert.match(html, /posições indisponíveis/);
});
