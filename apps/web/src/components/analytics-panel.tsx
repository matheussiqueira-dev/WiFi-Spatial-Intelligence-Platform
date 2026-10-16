"use client";

import { useEffect, useRef, useState } from "react";
import { z } from "zod";
import { request, requestText } from "../lib/api";
import {
  analyticsSchema,
  replaySchema,
  reportsSchema,
  download,
  type Analytics,
  type ReplayFrame,
} from "../lib/analytics";
import Observatory from "./observatory";

const localDate = (date: Date) =>
  new Date(date.getTime() - date.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 16);
const format = (value: number | null, digits = 2) =>
  value === null ? "Indisponível" : value.toFixed(digits);
const time = (value: string) => new Date(value).toLocaleString("pt-BR");

export default function AnalyticsPanel({ token }: { token: string }) {
  const [start, setStart] = useState(() =>
    localDate(new Date(Date.now() - 86400000)),
  );
  const [end, setEnd] = useState("");
  const [source, setSource] = useState("");
  const [scenario, setScenario] = useState("");
  const [segment, setSegment] = useState("");
  const [bucket, setBucket] = useState("minute");
  const [report, setReport] = useState<Analytics | null>(null);
  const [frames, setFrames] = useState<ReplayFrame[]>([]);
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [offset, setOffset] = useState(0);
  const [saved, setSaved] = useState<z.infer<typeof reportsSchema>["items"]>(
    [],
  );
  const [savedId, setSavedId] = useState("");
  const [applied, setApplied] = useState("");
  const generation = useRef(0);

  useEffect(
    () => () => {
      generation.current++;
    },
    [],
  );
  useEffect(() => {
    if (!playing || frames.length < 2 || index >= frames.length - 1) return;
    const current = frames[index].event;
    const next = frames[index + 1].event;
    const delay = Math.min(
      2000,
      Math.max(
        50,
        (Date.parse(next.timestamp) - Date.parse(current.timestamp)) / speed,
      ),
    );
    const timer = setTimeout(() => {
      setIndex(index + 1);
      if (index + 1 === frames.length - 1) setPlaying(false);
    }, delay);
    return () => clearTimeout(timer);
  }, [playing, index, speed, frames]);

  function parameters(pageOffset = 0) {
    const params = new URLSearchParams({
      start: new Date(start).toISOString(),
      end: (end ? new Date(end) : new Date()).toISOString(),
      bucket,
      room_id: "living-room",
      limit: "100",
      offset: String(pageOffset),
    });
    if (source) params.set("source_id", source);
    if (scenario) params.set("scenario", scenario);
    if (segment) params.set("segment_id", segment);
    return params;
  }

  async function load(pageOffset = 0) {
    const run = ++generation.current;
    setPlaying(false);
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const params = parameters(pageOffset);
      const next = await request(
        `/analytics?${params}`,
        token,
        analyticsSchema,
      );
      const all: ReplayFrame[] = [];
      const replayParams = new URLSearchParams(params);
      replayParams.set("limit", "200");
      for (let cursor = 0; cursor < 10000; cursor += 200) {
        replayParams.set("offset", String(cursor));
        const page = await request(
          `/analytics/replay?${replayParams}`,
          token,
          replaySchema,
        );
        if (run !== generation.current) return;
        all.push(...page.items);
        if (all.length >= page.total) break;
      }
      const list = await request("/analytics/reports", token, reportsSchema);
      if (run !== generation.current) return;
      setReport(next);
      setFrames(all);
      setIndex(0);
      setOffset(pageOffset);
      setApplied(params.toString());
      setSaved(list.items);
      setSavedId("");
    } catch (e) {
      if (run === generation.current) {
        setReport(null);
        setFrames([]);
        setError(
          e instanceof Error ? e.message : "Falha ao consultar análises.",
        );
      }
    } finally {
      if (run === generation.current) setBusy(false);
    }
  }

  async function save() {
    setBusy(true);
    setError("");
    try {
      const body = Object.fromEntries(new URLSearchParams(applied));
      const result = await request(
        "/analytics/reports",
        token,
        z.object({ id: z.uuid(), evidence_level: z.literal("L0_SYNTHETIC") }),
        { method: "POST", body: JSON.stringify(body) },
      );
      setSaved(
        (await request("/analytics/reports", token, reportsSchema)).items,
      );
      setMessage(`Relatório ${result.id} salvo no SQLite.`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Falha ao salvar.");
    } finally {
      setBusy(false);
    }
  }

  async function openSaved(identifier: string) {
    if (!identifier) return;
    setBusy(true);
    setPlaying(false);
    setError("");
    try {
      const next = await request(
        `/analytics/reports/${identifier}`,
        token,
        analyticsSchema,
      );
      setReport(next);
      setFrames([]);
      setSavedId(identifier);
      setApplied("");
      setMessage(
        "Snapshot salvo; consulte novamente para carregar o replay dos eventos retidos.",
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Falha ao abrir relatório.");
    } finally {
      setBusy(false);
    }
  }

  async function exportCsv() {
    setBusy(true);
    setError("");
    try {
      const text = await requestText(`/analytics/export.csv?${applied}`, token);
      download("synthetic-analytics.csv", text, "text/csv;charset=utf-8");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Falha na exportação.");
    } finally {
      setBusy(false);
    }
  }

  const frame = frames[index];
  const summary = report?.summary;
  return (
    <section
      id="analytics"
      className="panel analytics"
      aria-labelledby="analytics-title"
    >
      <h2 id="analytics-title">Análises históricas e replay</h2>
      <p className="notice">
        <strong>L0_SYNTHETIC · HISTÓRICO</strong> Dados do SQLite. Contagens são
        médias por amostra; entradas e saídas são variações líquidas, sem
        identificar pessoas. Lacunas e contagens desconhecidas interrompem
        transições.
      </p>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          void load();
        }}
      >
        <fieldset disabled={busy} className="analytics-filters">
          <legend>
            Filtros históricos · horário local (
            {Intl.DateTimeFormat().resolvedOptions().timeZone})
          </legend>
          <label>
            De
            <input
              type="datetime-local"
              value={start}
              onChange={(e) => setStart(e.target.value)}
              required
            />
          </label>
          <label>
            Até (vazio = agora)
            <input
              type="datetime-local"
              value={end}
              onChange={(e) => setEnd(e.target.value)}
            />
          </label>
          <label>
            Sala
            <select value="living-room" onChange={() => {}}>
              <option value="living-room">Laboratório virtual</option>
            </select>
          </label>
          <label>
            Provedor / fonte
            <select value={source} onChange={(e) => setSource(e.target.value)}>
              <option value="">Todas as fontes</option>
              <option value="native-01">Motor nativo · native-01</option>
              <option value="simulator-01">
                Simulador interno · simulator-01
              </option>
              <option value="ruview-01">RuView simulado · ruview-01</option>
            </select>
          </label>
          <label>
            Proveniência / cenário
            <select
              value={scenario}
              onChange={(e) => setScenario(e.target.value)}
            >
              <option value="">Todos os cenários</option>
              {[
                "empty",
                "stationary",
                "walking",
                "entering",
                "leaving",
                "interference",
                "packet_loss",
                "disconnect",
                "ruview-simulated",
              ].map((value) => (
                <option key={value}>{value}</option>
              ))}
            </select>
          </label>
          <label>
            Agregação
            <select value={bucket} onChange={(e) => setBucket(e.target.value)}>
              <option value="minute">Minuto</option>
              <option value="five_minutes">5 minutos</option>
              <option value="hour">Hora</option>
              <option value="day">Dia</option>
            </select>
          </label>
          <label>
            Trecho de sessão
            <input
              value={segment}
              onChange={(e) => setSegment(e.target.value)}
              placeholder="UUID opcional"
            />
          </label>
          <button type="submit">Consultar histórico</button>
        </fieldset>
      </form>
      <p>
        Limites: 31 dias e 10.000 eventos por consulta. Os seis sensores
        virtuais não produzem streams individuais; o filtro usa a fonte de
        observação disponível.
      </p>
      {busy && <p role="status">Carregando análises…</p>}
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <p role="status" aria-live="polite" aria-label="Resultado das análises">
        {message}
      </p>
      {report && summary && (
        <>
          <p data-testid="analytics-samples">
            {summary.samples} observações históricas · {summary.segments}{" "}
            trechos
          </p>
          <dl className="analytics-metrics">
            {[
              ["Entradas estimadas", summary.entries_estimate],
              ["Saídas estimadas", summary.exits_estimate],
              ["Contagens indisponíveis", summary.unknown_count_samples],
              ["Presença observada (s)", format(summary.presence_seconds)],
              ["Lacunas entre amostras (s)", format(summary.unknown_seconds)],
              ["Taxa histórica (eventos/s)", format(summary.event_rate)],
              ["Espera p50 (ms)", format(summary.queue_wait_p50_ms, 3)],
              ["Espera p95 (ms)", format(summary.queue_wait_p95_ms, 3)],
            ].map(([label, value]) => (
              <div key={label}>
                <dt>{label}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
          <div className="actions analytics-actions">
            <button disabled={busy || !applied} onClick={() => void save()}>
              Salvar relatório
            </button>
            <button
              disabled={busy}
              onClick={() =>
                download(
                  "synthetic-analytics.json",
                  JSON.stringify(report, null, 2),
                  "application/json",
                )
              }
            >
              Exportar JSON
            </button>
            <button
              disabled={busy || !applied}
              onClick={() => void exportCsv()}
            >
              Exportar CSV
            </button>
          </div>
          <label>
            Relatórios no SQLite
            <select
              value={savedId}
              disabled={busy}
              onChange={(e) => void openSaved(e.target.value)}
            >
              <option value="">Selecionar snapshot</option>
              {saved.map((item) => (
                <option key={item.id} value={item.id}>
                  {time(item.created_at)} · {item.id.slice(0, 8)}
                </option>
              ))}
            </select>
          </label>
          {summary.samples === 0 ? (
            <p>Nenhuma observação no intervalo selecionado.</p>
          ) : (
            <>
              <h3>Ocupação por período</h3>
              <p>
                Altura: média de ocupantes por amostra (0–20). Períodos sem
                observação não são sala vazia. Horários exibidos no fuso local.
              </p>
              <div
                className="analytics-chart"
                role="img"
                aria-label="Ocupação média por período; valores completos na tabela seguinte"
              >
                {report.buckets.items.map((item) => (
                  <div
                    key={`${item.timestamp}-${item.source_id}`}
                    title={`${time(item.timestamp)}: ${item.occupancy_mean ?? "indisponível"}`}
                    style={{
                      height: `${Math.max(4, ((item.occupancy_mean ?? 0) / 20) * 100)}%`,
                    }}
                  />
                ))}
              </div>
              <div
                className="table-scroll"
                role="region"
                aria-label="Agregações históricas"
                tabIndex={0}
              >
                <table>
                  <thead>
                    <tr>
                      <th>Período local</th>
                      <th>Fonte</th>
                      <th>Amostras</th>
                      <th>Média</th>
                      <th>Máximo</th>
                      <th>Presença por amostra</th>
                      <th>Entradas / saídas</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.buckets.items.map((item) => (
                      <tr key={`${item.timestamp}-${item.source_id}`}>
                        <td>{time(item.timestamp)}</td>
                        <td>{item.source_id}</td>
                        <td>{item.samples}</td>
                        <td>{format(item.occupancy_mean)}</td>
                        <td>{item.occupancy_max ?? "Indisponível"}</td>
                        <td>{(item.presence_fraction * 100).toFixed(1)}%</td>
                        <td>
                          {item.entries_estimate} / {item.exits_estimate}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="pagination">
                <span>{report.buckets.total} agregações</span>
                <button
                  disabled={busy || offset === 0 || !applied}
                  onClick={() => void load(Math.max(0, offset - 100))}
                >
                  Agregações anteriores
                </button>
                <button
                  disabled={
                    busy || offset + 100 >= report.buckets.total || !applied
                  }
                  onClick={() => void load(offset + 100)}
                >
                  Próximas agregações
                </button>
              </div>
              <h3>Transições de ocupação</h3>
              <ul>
                {report.transitions.items.map((item) => (
                  <li key={item.event_id}>
                    {time(item.timestamp)} · {item.source_id}: {item.from_count}{" "}
                    → {item.to_count} · +{item.entries_estimate} / −
                    {item.exits_estimate} (estimativas sintéticas)
                  </li>
                ))}
              </ul>
              {report.transitions.total === 0 && (
                <p>Nenhuma transição de contagem estimável.</p>
              )}
              <p>
                {report.intervals.total} intervalos entre amostras;{" "}
                {summary.excluded_transitions} comparações interrompidas por
                ausência de continuidade ou contagem.
              </p>
            </>
          )}
          <h3>Spatial Observatory · playback temporal</h3>
          <p>
            REPLAY — dados históricos sintéticos. Não controla a sessão ao vivo.
            Lacunas maiores que 2 s são comprimidas durante a reprodução; os
            timestamps originais são preservados.
          </p>
          {frame ? (
            <>
              <p data-testid="replay-time">
                {time(frame.event.timestamp)} · {frame.event.source_id} · tick{" "}
                {frame.event.provenance.tick} · trecho{" "}
                {frame.segment_id ?? "legado sem sessão"}
              </p>
              <Observatory event={frame.event} sensors={[]} connected={false} />
              <p>
                Contagem histórica:{" "}
                {frame.event.measurements.occupancy_estimate ?? "Indisponível"}.{" "}
                {frame.event.source_id === "ruview-01"
                  ? "Posições indisponíveis no laboratório legado."
                  : "Posições de verdade sintética, sem inferência de IA."}
              </p>
              <label>
                Posição no replay
                <input
                  type="range"
                  min={0}
                  max={frames.length - 1}
                  value={index}
                  onChange={(e) => {
                    setPlaying(false);
                    setIndex(Number(e.target.value));
                  }}
                />
              </label>
              <div className="actions analytics-actions">
                <button
                  disabled={playing || index >= frames.length - 1}
                  onClick={() => setPlaying(true)}
                >
                  Reproduzir histórico
                </button>
                <button disabled={!playing} onClick={() => setPlaying(false)}>
                  Pausar replay
                </button>
                <button
                  onClick={() => {
                    setPlaying(false);
                    setIndex(0);
                  }}
                >
                  Voltar ao início
                </button>
                <label>
                  Velocidade do replay
                  <select
                    value={speed}
                    onChange={(e) => setSpeed(Number(e.target.value))}
                  >
                    {[0.25, 0.5, 1, 2, 4].map((value) => (
                      <option key={value} value={value}>
                        {value}×
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            </>
          ) : (
            <p>Nenhum frame de replay carregado.</p>
          )}
          <details>
            <summary>Limitações e critérios de interpretação</summary>
            <ul>
              {report.limitations.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </details>
        </>
      )}
    </section>
  );
}
