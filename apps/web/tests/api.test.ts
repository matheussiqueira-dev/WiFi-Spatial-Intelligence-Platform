import assert from "node:assert/strict";
import { afterEach, test } from "node:test";
import { readFileSync } from "node:fs";
import { z } from "zod";
import {
  ApiError,
  STREAM_CONTRACT_CLOSE,
  controlBody,
  dismissResolved,
  isClientCloseCode,
  mergeHistory,
  mergeStatus,
  request,
  requestText,
  statusMessage,
  streamCloseOutcome,
} from "../src/lib/api";
import { eventSchema, type SensingEvent, type Status } from "../src/lib/contracts";

const realFetch = globalThis.fetch;
afterEach(() => {
  globalThis.fetch = realFetch;
});
function respond(body: BodyInit | null, init: ResponseInit) {
  globalThis.fetch = async () => new Response(body, init);
}
const base: SensingEvent = eventSchema.parse(
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
function event(id: number, timestamp: string): SensingEvent {
  return {
    ...base,
    event_id: `00000000-0000-4000-8000-${String(id).padStart(12, "0")}`,
    timestamp,
  };
}

test("client-initiated contract close uses a code browsers accept", () => {
  assert.equal(isClientCloseCode(1008), false);
  assert.equal(isClientCloseCode(1000), true);
  assert.equal(isClientCloseCode(STREAM_CONTRACT_CLOSE), true);
  assert.deepEqual(streamCloseOutcome(STREAM_CONTRACT_CLOSE), {
    label: "Dados incompatíveis",
    reconnect: false,
  });
  assert.deepEqual(streamCloseOutcome(1008), {
    label: "Acesso recusado",
    reconnect: false,
  });
  for (const code of [1005, 1006, 1013])
    assert.equal(streamCloseOutcome(code).reconnect, true);
});

test("validation, rate limit and unavailability map to actionable pt-BR text", () => {
  assert.match(statusMessage(422, null), /parâmetros/i);
  assert.doesNotMatch(statusMessage(422, null), /Verifique o backend/);
  assert.match(statusMessage(429, "12"), /12 s/);
  assert.match(statusMessage(429, null), /Limite/);
  assert.match(statusMessage(503, null), /indisponível/);
  assert.match(statusMessage(401, null), /Token inválido/);
  assert.match(statusMessage(500, null), /erro 500/);
});

test("request exposes typed errors and never leaks raw body parse failures", async () => {
  respond(JSON.stringify({ detail: "x" }), {
    status: 429,
    headers: { "Retry-After": "7" },
  });
  await assert.rejects(request("/events", "t", z.unknown()), (error) => {
    assert.ok(error instanceof ApiError);
    assert.equal(error.status, 429);
    assert.equal(error.retryAfter, 7);
    assert.match(error.message, /7 s/);
    return true;
  });
  respond("<html>proxy</html>", { status: 200 });
  await assert.rejects(request("/events", "t", z.unknown()), (error) => {
    assert.ok(error instanceof ApiError);
    assert.doesNotMatch(error.message, /JSON|Unexpected token/);
    assert.match(error.message, /ilegível/);
    return true;
  });
  globalThis.fetch = async () => {
    throw new TypeError("Failed to fetch");
  };
  await assert.rejects(requestText("/analytics/export.csv", "t"), (error) => {
    assert.ok(error instanceof ApiError);
    assert.match(error.message, /Não foi possível acessar a API/);
    return true;
  });
  respond("a,b\n", { status: 422 });
  await assert.rejects(requestText("/analytics/export.csv", "t"), /parâmetros/i);
  respond("a,b\n", { status: 200 });
  assert.equal(await requestText("/analytics/export.csv", "t"), "a,b\n");
});

test("a REST snapshot never rolls back a newer live frame or drops streamed rows", () => {
  const older = event(1, "2026-10-15T10:00:00.000Z");
  const newer = event(2, "2026-10-15T10:00:00.125Z");
  const current = { latest: newer, state: "running" } as unknown as Status;
  const snapshot = { latest: older, state: "paused" } as unknown as Status;
  const merged = mergeStatus(current, snapshot);
  assert.equal(merged.latest?.event_id, newer.event_id);
  assert.equal(merged.state, "paused");
  const cleared = { latest: null, state: "stopped" } as unknown as Status;
  assert.equal(mergeStatus(current, cleared).latest, null);
  assert.deepEqual(
    mergeHistory([newer, older], [older]).map((e) => e.event_id),
    [newer.event_id, older.event_id],
  );
  assert.deepEqual(mergeHistory([newer, older], []), []);
  const page = Array.from({ length: 20 }, (_, i) =>
    event(100 + i, new Date(Date.UTC(2026, 9, 15, 9, 0, 20 - i)).toISOString()),
  );
  assert.equal(mergeHistory([newer], page).length, 20);
  assert.equal(mergeHistory([newer], page)[0].event_id, newer.event_id);
});

test("only the stale sync warning is dismissed when the API recovers", () => {
  assert.equal(dismissResolved("API fora", "API fora"), "");
  assert.equal(dismissResolved("Token inválido", "API fora"), "Token inválido");
  assert.equal(dismissResolved("", "API fora"), "");
});

test("simulation controls validate the form only when starting the native engine", () => {
  const invalid = { scenario: "walking", seed: 42, occupants: 25, speed: 1 } as const;
  for (const action of ["pause", "resume", "stop", "reset"] as const)
    assert.equal(controlBody(action, "synthetic-native", invalid), undefined);
  assert.equal(controlBody("start", "RUVIEW_STREAM", invalid), "{}");
  assert.throws(() => controlBody("start", "synthetic-native", invalid), z.ZodError);
  assert.deepEqual(
    JSON.parse(
      controlBody("start", "synthetic-native", { ...invalid, occupants: 3 }) ??
        "",
    ),
    { ...invalid, occupants: 3 },
  );
});
