"use client";

import { useEffect, useState } from "react";
import { request } from "../lib/api";
import { networkHealthSchema, type NetworkHealth } from "../lib/network";

const value = (number: number | null | undefined, unit = "") =>
  number == null
    ? "—"
    : `${number.toLocaleString("pt-BR", { maximumFractionDigits: 1 })}${unit}`;
const hour = (iso: string) =>
  new Date(iso).toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });

export default function NetworkHealthView({
  token,
  location,
}: {
  token: string;
  location: string;
}) {
  const [health, setHealth] = useState<NetworkHealth | null>(null);
  const [error, setError] = useState("");
  const parameters = new URLSearchParams({
    hours: "24",
    bucket_minutes: "60",
    ...(location ? { location } : {}),
  }).toString();
  useEffect(() => {
    let alive = true;
    async function sync() {
      try {
        const next = await request(
          `/network/health?${parameters}`,
          token,
          networkHealthSchema,
        );
        if (alive) {
          setHealth(next);
          setError("");
        }
      } catch (e) {
        if (alive)
          setError(
            e instanceof Error ? e.message : "Falha ao consultar a tendência.",
          );
      }
    }
    void sync();
    const timer = setInterval(() => void sync(), 60000);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, [token, parameters]);
  const measured = health?.buckets.filter((bucket) => bucket.summary.samples);
  return (
    <section className="network-health" aria-labelledby="network-health-title">
      <h3 id="network-health-title">Tendência e alertas (24 h)</h3>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {!health ? (
        !error && <p>Carregando tendência…</p>
      ) : (
        <>
          <div role="status" data-testid="network-alerts">
            {health.alerts.length === 0 ? (
              <p>Nenhum alerta: a última hora segue a linha de base.</p>
            ) : (
              <ul>
                {health.alerts.map((alert) => (
                  <li key={alert.code} className={`alert-${alert.severity}`}>
                    {alert.message}
                  </li>
                ))}
              </ul>
            )}
          </div>
          {health.abstentions.length > 0 && (
            <p className="muted">
              Sem comparação para:{" "}
              {health.abstentions.map((item) => item.split(":")[0]).join(", ")}{" "}
              (dados insuficientes; nada é inferido).
            </p>
          )}
          {measured && measured.length > 0 && (
            <div
              className="table-scroll"
              role="region"
              aria-label="Tendência horária do enlace"
              tabIndex={0}
            >
              <table>
                <thead>
                  <tr>
                    <th>Hora local</th>
                    <th>Amostras</th>
                    <th>Sinal médio</th>
                    <th>Latência p95</th>
                    <th>Sondas sem resposta</th>
                    <th>Desconexões</th>
                  </tr>
                </thead>
                <tbody>
                  {measured.map((bucket) => (
                    <tr key={bucket.start}>
                      <td>
                        {hour(bucket.start)}–{hour(bucket.end)}
                      </td>
                      <td>{bucket.summary.samples}</td>
                      <td>{value(bucket.summary.signal_mean_percent, "%")}</td>
                      <td>{value(bucket.summary.gateway_p95_ms, " ms")}</td>
                      <td>{value(bucket.summary.gateway_loss_percent, "%")}</td>
                      <td>{bucket.summary.disconnect_events}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <small className="network-details">
            Consultivo: compara a última hora com as horas anteriores do mesmo
            filtro. Nenhuma ação é disparada e nenhuma causa é presumida.
          </small>
        </>
      )}
    </section>
  );
}
