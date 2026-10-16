"use client";

import { useEffect, useState } from "react";
import { request } from "../lib/api";
import {
  channelAdvice,
  channelPlanSchema,
  type ChannelPlan,
} from "../lib/network";

const score = (value: number | null) =>
  value == null
    ? "—"
    : value.toLocaleString("pt-BR", { maximumFractionDigits: 2 });

export default function ChannelPlanView({
  token,
  location,
}: {
  token: string;
  location: string;
}) {
  const [plan, setPlan] = useState<ChannelPlan | null>(null);
  const [error, setError] = useState("");
  const parameters = new URLSearchParams({
    hours: "1",
    ...(location ? { location } : {}),
  }).toString();
  useEffect(() => {
    let alive = true;
    async function sync() {
      try {
        const next = await request(
          `/network/channel-plan?${parameters}`,
          token,
          channelPlanSchema,
        );
        if (alive) {
          setPlan(next);
          setError("");
        }
      } catch (e) {
        if (alive)
          setError(
            e instanceof Error ? e.message : "Falha ao consultar os canais.",
          );
      }
    }
    void sync();
    const timer = setInterval(() => void sync(), 30000);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, [token, parameters]);
  return (
    <section className="channel-plan" aria-labelledby="channel-plan-title">
      <h3 id="channel-plan-title">Ocupação de canais (última hora)</h3>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {!plan ? (
        !error && <p role="status">Carregando canais…</p>
      ) : plan.surveys === 0 ? (
        <p className="notice" data-testid="channel-plan-empty">
          Nenhuma varredura no período. Inicie o coletor com{" "}
          <code>-ChannelSurvey</code> para enviar, a cada minuto, só agregados
          por canal das redes que o Windows já listou.
          {plan.failed_surveys > 0 &&
            ` ${plan.failed_surveys} leitura(s) falharam.`}
        </p>
      ) : (
        <>
          <p className="network-details">
            {plan.surveys} varreduras · última em{" "}
            {plan.last_survey_at
              ? new Date(plan.last_survey_at).toLocaleTimeString("pt-BR")
              : "—"}
            {plan.failed_surveys > 0 &&
              ` · ${plan.failed_surveys} leitura(s) com falha`}
          </p>
          {plan.bands.map((band) => (
            <div key={band.band} className="channel-band">
              <h4>{band.band.replace(".", ",")}</h4>
              <p
                className={
                  band.advice === "CONSIDER_CHANGE"
                    ? "notice"
                    : "network-details"
                }
                data-testid={`channel-advice-${band.band}`}
              >
                {channelAdvice(band)}
              </p>
              {band.candidates.length > 0 && (
                <div
                  className="table-scroll"
                  role="region"
                  aria-label={`Canais candidatos em ${band.band}`}
                  tabIndex={0}
                >
                  <table>
                    <thead>
                      <tr>
                        <th>Canal</th>
                        <th>Redes vizinhas (média)</th>
                        <th>Índice de interferência</th>
                      </tr>
                    </thead>
                    <tbody>
                      {band.candidates.map((row) => (
                        <tr
                          key={row.channel}
                          aria-current={
                            row.channel === band.current_channel
                              ? "true"
                              : undefined
                          }
                        >
                          <td>
                            {row.channel}
                            {row.channel === band.current_channel && " (atual)"}
                          </td>
                          <td>{score(row.observed_ap_count)}</td>
                          <td>{score(row.interference_score)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ))}
          <details>
            <summary>Como interpretar</summary>
            <ul className="network-details">
              {plan.limitations.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </details>
        </>
      )}
    </section>
  );
}
