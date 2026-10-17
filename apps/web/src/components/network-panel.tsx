"use client";

import { useEffect, useState } from "react";
import { z } from "zod";
import { request, requestText } from "../lib/api";
import { download } from "../lib/analytics";
import {
  locationSchema,
  networkReportSchema,
  locationGrade,
  networkWarnings,
  rankLocations,
  type NetworkReport,
} from "../lib/network";
import ChannelPlanView from "./channel-plan";
import NetworkHealthView from "./network-health";
import NetworkWebhookView from "./network-webhook";

const states = {
  CONNECTED: "Conectado",
  DISCONNECTED: "Desconectado",
  UNAVAILABLE: "Leitura indisponível",
};
const metric = (value: number | null | undefined, unit = "") =>
  value == null
    ? "Indisponível"
    : `${value.toLocaleString("pt-BR", { maximumFractionDigits: 1 })}${unit}`;

export default function NetworkPanel({ token }: { token: string }) {
  const [report, setReport] = useState<NetworkReport | null>(null);
  const [hours, setHours] = useState("24");
  const [location, setLocation] = useState("");
  const [label, setLabel] = useState("");
  const [offset, setOffset] = useState(0);
  const [revision, setRevision] = useState(0);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const parameters = new URLSearchParams({
    hours,
    limit: "50",
    offset: String(offset),
    ...(location ? { location } : {}),
  }).toString();
  useEffect(() => {
    let alive = true;
    let inFlight = false;
    async function sync() {
      if (inFlight) return;
      inFlight = true;
      try {
        const next = await request(
          `/network/report?${parameters}`,
          token,
          networkReportSchema,
        );
        if (alive) {
          setReport(next);
          setError("");
        }
      } catch (e) {
        if (alive)
          setError(
            e instanceof Error
              ? e.message
              : "Falha ao consultar o diagnóstico.",
          );
      } finally {
        inFlight = false;
      }
    }
    void sync();
    const timer = setInterval(() => void sync(), 10000);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, [token, parameters, revision]);

  async function configure(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const checked = locationSchema.parse(label.trim());
      await request(
        "/network/config",
        token,
        z.object({ location: locationSchema }),
        { method: "POST", body: JSON.stringify({ location: checked }) },
      );
      setMessage(
        `Ponto definido: ${checked}. Será aplicado na próxima coleta.`,
      );
      setLabel("");
      setRevision((value) => value + 1);
    } catch (e) {
      setError(
        e instanceof z.ZodError
          ? "Use um nome de até 48 caracteres, começando com letra ou número."
          : e instanceof Error
            ? e.message
            : "Não foi possível definir o ponto.",
      );
    } finally {
      setBusy(false);
    }
  }
  async function erase() {
    const scope = location
      ? `as medições do ponto "${location}"`
      : "todo o histórico de rede";
    if (
      !window.confirm(
        `Apagar ${scope}? A exclusão é definitiva; a auditoria registra apenas o fato.`,
      )
    )
      return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const result = await request(
        `/network/history?${new URLSearchParams({
          confirm: "ERASE",
          ...(location ? { location } : {}),
        })}`,
        token,
        z.object({
          erased: z.object({
            samples: z.number().int().nonnegative(),
            surveys: z.number().int().nonnegative(),
          }),
        }),
        { method: "DELETE" },
      );
      setMessage(
        `${result.erased.samples} medições e ${result.erased.surveys} varreduras apagadas.`,
      );
      setLocation("");
      setOffset(0);
      setRevision((value) => value + 1);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Falha ao apagar o histórico.");
    } finally {
      setBusy(false);
    }
  }
  async function exportCsv() {
    setBusy(true);
    setError("");
    try {
      download(
        "network-diagnostics.csv",
        await requestText(`/network/export.csv?${parameters}`, token),
        "text/csv;charset=utf-8",
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Falha na exportação.");
    } finally {
      setBusy(false);
    }
  }
  const summary = report?.summary;
  const latest = report?.latest;
  return (
    <section
      id="network"
      className="panel network-panel"
      aria-labelledby="network-title"
    >
      <div className="panel-heading">
        <div>
          <p className="muted">Seu computador · enlace local</p>
          <h2 id="network-title">Diagnóstico Wi-Fi real</h2>
        </div>
        <span className="network-badge">Telemetria do host</span>
      </div>
      <p className="network-intro">
        Medições do Windows, separadas da cena sintética. Não detectam pessoas
        ou animais. Sondas avaliam somente a resposta do roteador, não a
        disponibilidade da Internet.
      </p>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <p role="status" className="live">
        {message}
      </p>
      {!report ? (
        <p role="status">Carregando diagnóstico…</p>
      ) : (
        <>
          {networkWarnings(report).map((warning) => (
            <p className="notice" key={warning}>
              {warning}
            </p>
          ))}
          {report.total === 0 && (
            <p className="notice">
              Nenhuma medição neste período. Inicie o coletor local no Windows;
              dados ausentes não significam rede desconectada.
            </p>
          )}
          <div className="network-metrics">
            <div>
              <span>Estado informado pelo Windows</span>
              <strong data-testid="network-link">
                {latest ? states[latest.link_state] : "Sem leitura"}
              </strong>
              <small>
                {summary?.collector_stale
                  ? "Sem atualização recente"
                  : "Coletor atualizado"}
              </small>
            </div>
            <div>
              <span>Último sinal</span>
              <strong data-testid="network-signal">
                {metric(latest?.signal_percent, "%")}
              </strong>
              <small>Qualidade em %, não RSSI em dBm</small>
            </div>
            <div>
              <span>Latência média até o roteador</span>
              <strong>{metric(summary?.gateway_mean_ms, " ms")}</strong>
              <small>p95: {metric(summary?.gateway_p95_ms, " ms")}</small>
            </div>
            <div>
              <span>Sondas sem resposta</span>
              <strong>{metric(summary?.gateway_loss_percent, "%")}</strong>
              <small>ICMP pode ser limitado pelo roteador</small>
            </div>
          </div>
          <div className="network-controls">
            <label>
              Período do diagnóstico
              <select
                value={hours}
                onChange={(e) => {
                  setHours(e.target.value);
                  setOffset(0);
                }}
              >
                <option value="0.5">Últimos 30 minutos</option>
                <option value="6">Últimas 6 horas</option>
                <option value="24">Últimas 24 horas</option>
              </select>
            </label>
            <label>
              Filtrar ponto
              <select
                value={location}
                onChange={(e) => {
                  setLocation(e.target.value);
                  setOffset(0);
                }}
              >
                <option value="">Todos os pontos</option>
                {report.locations.map((point) => (
                  <option key={point} value={point}>
                    {point}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              className="secondary"
              onClick={() => setRevision((value) => value + 1)}
            >
              Atualizar diagnóstico
            </button>
            <button
              type="button"
              className="secondary"
              disabled={busy || !report.total}
              onClick={() => void exportCsv()}
            >
              Exportar medições CSV
            </button>
            <button
              type="button"
              className="secondary"
              disabled={busy || !report.total}
              onClick={() => void erase()}
            >
              {location
                ? "Apagar medições deste ponto"
                : "Apagar histórico de rede"}
            </button>
          </div>
          <form className="network-location" onSubmit={configure}>
            <label>
              Nome do ponto atual
              <input
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                placeholder={report.configured_location}
                maxLength={48}
                required
              />
            </label>
            <button disabled={busy}>Definir ponto de medição</button>
            <p>
              Mova o computador e nomeie o ponto para comparar a conexão. Ponto
              configurado: <strong>{report.configured_location}</strong>.
            </p>
          </form>
          <p className="network-details">
            {report.total} amostras no período · Wi-Fi conectado em{" "}
            {metric(summary?.connected_percent, "%")} das leituras com estado
            conhecido · {summary?.disconnect_events ?? 0} transições observadas
            para desconectado · {metric(summary?.missing_seconds, " s")} em
            lacunas internas. Sem extrapolação fora das observações.
          </p>
          <p className="network-details">
            Canal {latest?.channel ?? "indisponível"} ·{" "}
            {latest?.radio_type ?? "Padrão indisponível"} · Taxas do enlace
            RX/TX: {metric(latest?.rx_mbps, " Mbps")} /{" "}
            {metric(latest?.tx_mbps, " Mbps")}. Não são um teste de velocidade
            da Internet.
          </p>
          {report.comparisons.length > 0 && (
            <div
              className="table-scroll"
              role="region"
              aria-label="Comparação dos pontos Wi-Fi"
              tabIndex={0}
            >
              <table>
                <thead>
                  <tr>
                    <th>Ponto</th>
                    <th>Amostras</th>
                    <th>Sinal médio</th>
                    <th>Sondas sem resposta</th>
                    <th>Avaliação</th>
                  </tr>
                </thead>
                <tbody>
                  {rankLocations(report.comparisons).map((point) => (
                    <tr key={point.location}>
                      <td>{point.location}</td>
                      <td>{point.summary.samples}</td>
                      <td>{metric(point.summary.signal_mean_percent, "%")}</td>
                      <td>{metric(point.summary.gateway_loss_percent, "%")}</td>
                      <td data-testid="location-grade">
                        {locationGrade(point.summary)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <NetworkHealthView token={token} location={location} />
          <NetworkWebhookView token={token} />
          <ChannelPlanView token={token} location={location} />
          <details>
            <summary>Histórico das medições</summary>
            <div
              className="table-scroll"
              role="region"
              aria-label="Histórico Wi-Fi real"
              tabIndex={0}
            >
              <table>
                <thead>
                  <tr>
                    <th>Horário local</th>
                    <th>Ponto</th>
                    <th>Wi-Fi</th>
                    <th>Sinal</th>
                    <th>Respostas ICMP</th>
                  </tr>
                </thead>
                <tbody>
                  {report.items.map((row) => (
                    <tr key={row.sample_id}>
                      <td>{new Date(row.timestamp).toLocaleString("pt-BR")}</td>
                      <td>{row.location}</td>
                      <td>{states[row.link_state]}</td>
                      <td>{metric(row.signal_percent, "%")}</td>
                      <td>
                        {row.probe_sent
                          ? `${row.probe_rtt_ms.length}/${row.probe_sent}`
                          : "Não executadas"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="pagination">
              <button
                className="secondary"
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - 50))}
              >
                Medições mais recentes
              </button>
              <button
                className="secondary"
                disabled={offset + 50 >= report.total}
                onClick={() => setOffset(offset + 50)}
              >
                Medições anteriores
              </button>
            </div>
          </details>
          <small className="network-details">
            L2_LIVE_UNVALIDATED · até 100.000 medições, sem expurgo automático ·
            consulta/exportação limitada a 24 h e 10.000 amostras · SSID, MAC,
            senha e conteúdo de tráfego não são enviados.
          </small>
        </>
      )}
    </section>
  );
}
