"use client";

import { useState } from "react";
import { z } from "zod";
import { request } from "../lib/api";
import { ruleSchema, rulesSchema, decisionsSchema } from "../lib/automation";

export default function AutomationPanel({ token }: { token: string }) {
  const [rules, setRules] = useState<z.infer<typeof rulesSchema> | null>(null);
  const [decisions, setDecisions] = useState<z.infer<
    typeof decisionsSchema
  > | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [threshold, setThreshold] = useState(1);
  async function refresh(offset = 0) {
    const [r, d] = await Promise.all([
      request("/automation/rules", token, rulesSchema),
      request(
        `/automation/decisions?limit=10&offset=${offset}`,
        token,
        decisionsSchema,
      ),
    ]);
    setRules(r);
    setDecisions(d);
  }
  async function perform(action: () => Promise<void>) {
    setBusy(true);
    setError("");
    try {
      await action();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro na regra");
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="panel analytics" aria-labelledby="automation-title">
      <h2 id="automation-title">Regras locais em dry-run</h2>
      <p>
        Somente decisões sobre eventos L0_SYNTHETIC. Nenhuma ação, webhook ou
        dispositivo é acionado. Até 20 regras e 1.000 decisões; capacidade cheia
        interrompe novos registros, sem apagar histórico.
      </p>
      <label>
        Ocupação mínima para regra
        <input
          type="number"
          min={0}
          max={20}
          value={threshold}
          onChange={(e) => setThreshold(Number(e.target.value))}
        />
      </label>
      <div className="toolbar">
        <button
          disabled={
            busy ||
            !Number.isInteger(threshold) ||
            threshold < 0 ||
            threshold > 20
          }
          onClick={() =>
            perform(async () => {
              await request("/automation/rules", token, ruleSchema, {
                method: "POST",
                body: JSON.stringify({
                  name: `Ocupação virtual ≥ ${threshold}`,
                  field: "occupancy",
                  threshold,
                }),
              });
              await refresh();
            })
          }
        >
          Criar regra dry-run
        </button>
        <button
          className="secondary"
          disabled={busy}
          onClick={() => perform(() => refresh())}
        >
          Atualizar regras e decisões
        </button>
      </div>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {busy && <p role="status">Atualizando regras locais…</p>}
      {rules?.decision_capacity_reached && (
        <p role="alert">
          Capacidade de decisões atingida. Revisão offline necessária.
        </p>
      )}
      <ul>
        {rules?.items.map((rule) => (
          <li key={rule.id} data-rule-id={rule.id}>
            {rule.name} · {rule.active ? "Ativa" : "Revogada"} · DRY_RUN{" "}
            <button
              className="secondary"
              disabled={busy || !rule.active}
              onClick={() =>
                perform(async () => {
                  await request(
                    `/automation/rules/${rule.id}/revoke`,
                    token,
                    z.object({
                      revoked: z.literal(true),
                      mode: z.literal("DRY_RUN"),
                    }),
                    { method: "POST" },
                  );
                  await refresh();
                })
              }
            >
              Revogar {rule.name}
            </button>
          </li>
        ))}
      </ul>
      {decisions && (
        <>
          <p role="status" aria-label="Total de decisões">
            {decisions.total} decisões sintéticas registradas
          </p>
          <div
            className="table-scroll"
            role="region"
            aria-label="Decisões dry-run"
            tabIndex={0}
          >
            <table>
              <thead>
                <tr>
                  <th>Horário</th>
                  <th>Regra / evento</th>
                  <th>Resultado</th>
                </tr>
              </thead>
              <tbody>
                {decisions.items.map((d) => (
                  <tr key={d.id}>
                    <td>{new Date(d.created_at).toLocaleString("pt-BR")}</td>
                    <td className="lab-hash">
                      {d.rule_id} / {d.event_id}
                    </td>
                    <td>
                      {d.matched
                        ? "Condição satisfeita"
                        : "Condição não satisfeita"}{" "}
                      · DRY_RUN · L0_SYNTHETIC · sem despacho
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="pagination">
            <button
              className="secondary"
              disabled={busy || decisions.offset === 0}
              onClick={() => perform(() => refresh(decisions.offset - 10))}
            >
              Decisões anteriores
            </button>
            <button
              className="secondary"
              disabled={busy || decisions.offset + 10 >= decisions.total}
              onClick={() => perform(() => refresh(decisions.offset + 10))}
            >
              Mais decisões
            </button>
          </div>
        </>
      )}
    </section>
  );
}
