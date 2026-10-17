"use client";

import { memo, useEffect, useEffectEvent, useRef, useState } from "react";
import { z } from "zod";
import dynamic from "next/dynamic";
import {
  apiBase,
  request,
  STREAM_CONTRACT_CLOSE,
  controlBody,
  dismissResolved,
  mergeHistory,
  mergeStatus,
  streamCloseOutcome,
} from "../lib/api";
import {
  historySchema,
  sensorSchema,
  statusSchema,
  streamSchema,
  type SensingEvent,
  type Sensor,
  type SimulationConfig,
  type Status,
} from "../lib/contracts";
import { scenarioLabel, scenarioLabels as scenarios } from "../lib/scenarios";
import Observatory from "./observatory";
import {
  capabilityCatalogSchema,
  enabledCapabilities,
} from "../lib/capabilities";
import {
  allows,
  identityLabel,
  identitySchema,
  type Identity,
} from "../lib/access";
import { RoleContext } from "./role-context";
// memo: the only prop is the stable token, so live stream packets do not re-render panels.
const AnalyticsPanel = memo(
  dynamic(() => import("./analytics-panel"), {
    loading: () => <p role="status">Carregando análises…</p>,
  }),
);
const NetworkPanel = memo(
  dynamic(() => import("./network-panel"), {
    loading: () => <p role="status">Carregando diagnóstico Wi-Fi…</p>,
  }),
);
const ModelLabPanel = memo(
  dynamic(() => import("./model-lab-panel"), {
    loading: () => <p role="status">Carregando laboratório…</p>,
  }),
);
const CapabilitiesPanel = memo(
  dynamic(() => import("./capabilities-panel"), {
    loading: () => <p role="status">Carregando catálogo…</p>,
  }),
);
const AutomationPanel = memo(
  dynamic(() => import("./automation-panel"), {
    loading: () => <p role="status">Carregando regras…</p>,
  }),
);
const AccessPanel = memo(
  dynamic(() => import("./access-panel"), {
    loading: () => <p role="status">Carregando perfis de acesso…</p>,
  }),
);

const states = { running: "Em execução", paused: "Pausada", stopped: "Parada" };
const services = {
  stopped: "Parado",
  connecting: "Conectando",
  waiting: "Aguardando dados",
  receiving: "Recebendo fluxo",
  reconnecting: "Reconectando",
};
const time = (timestamp: string) =>
  new Date(timestamp).toLocaleTimeString("pt-BR");

export default function Dashboard() {
  const [inputToken, setInputToken] = useState("");
  const [token, setToken] = useState("");
  const [status, setStatus] = useState<Status | null>(null);
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [history, setHistory] = useState<SensingEvent[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [connection, setConnection] = useState("Desconectado");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  // Profile-enabled capabilities, loaded at login; null while disconnected.
  const [allowed, setAllowed] = useState<Set<string> | null>(null);
  const spatial = allowed?.has("spatial.presence") ?? false;
  // Role of the signed-in token (GET /access/me); hides controls the API would refuse.
  const [identity, setIdentity] = useState<Identity | null>(null);
  const role = identity?.role ?? null;
  const canOperate = allows(role, "operator");
  const isAdmin = allows(role, "admin");
  const [config, setConfig] = useState<SimulationConfig>({
    scenario: "walking",
    seed: 42,
    occupants: 2,
    speed: 1,
  });
  const wsRef = useRef<WebSocket | null>(null);
  const pageHeading = useRef<HTMLHeadingElement>(null);
  const workspaceHeading = useRef<HTMLHeadingElement>(null);
  const tokenInput = useRef<HTMLInputElement>(null);
  const pendingFocus = useRef<"workspace" | "login" | null>(null);

  // Login and logout unmount the focused control; move focus to the new context.
  useEffect(() => {
    if (pendingFocus.current === "workspace") workspaceHeading.current?.focus();
    if (pendingFocus.current === "login") tokenInput.current?.focus();
    pendingFocus.current = null;
  }, [token]);

  // Reads the current page without reconnecting the stream whenever it changes.
  const onStreamEvent = useEffectEvent((event: SensingEvent) => {
    setStatus((previous) =>
      previous ? { ...previous, latest: event } : previous,
    );
    if (offset === 0)
      setHistory((previous) =>
        [
          event,
          ...previous.filter((item) => item.event_id !== event.event_id),
        ].slice(0, 20),
      );
  });

  useEffect(() => {
    if (!token || !spatial) return;
    let alive = true;
    let reconnect: ReturnType<typeof setTimeout> | undefined;
    let retries = 0;
    function connect() {
      if (!alive) return;
      setConnection("Conectando");
      const url = new URL(`${apiBase}/api/v1/stream`);
      url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
      const ws = new WebSocket(url);
      wsRef.current = ws;
      const deadline = setTimeout(() => ws.close(), 7000);
      ws.onopen = () => ws.send(JSON.stringify({ token }));
      ws.onmessage = (message) => {
        if (!alive) return;
        try {
          const packet = streamSchema.parse(JSON.parse(message.data));
          clearTimeout(deadline);
          retries = 0;
          setConnection("Ao vivo");
          if (packet.type === "status")
            setStatus((previous) => mergeStatus(previous, packet.data));
          else onStreamEvent(packet.data);
        } catch {
          setError(
            "A API enviou dados incompatíveis com o contrato sintético.",
          );
          ws.close(STREAM_CONTRACT_CLOSE);
        }
      };
      ws.onclose = (event) => {
        clearTimeout(deadline);
        if (!alive) return;
        const outcome = streamCloseOutcome(event.code);
        setConnection(outcome.label);
        if (outcome.reconnect)
          reconnect = setTimeout(
            connect,
            Math.min(1000 * 2 ** retries++, 10000),
          );
      };
      ws.onerror = () => {
        if (alive) setConnection("Reconectando");
      };
    }
    connect();
    return () => {
      alive = false;
      clearTimeout(reconnect);
      wsRef.current?.close();
    };
  }, [token, spatial]);

  useEffect(() => {
    if (!token) return;
    let alive = true;
    let inFlight = false;
    let syncWarning = "";
    async function sync() {
      if (inFlight) return;
      inFlight = true;
      try {
        // Spatial endpoints answer 403 when the profile disables group B.
        const [state, sensorList, events] = await Promise.all([
          request("/system/status", token, statusSchema),
          spatial
            ? request("/sensors", token, z.array(sensorSchema))
            : Promise.resolve(null),
          spatial
            ? request(`/events?limit=20&offset=${offset}`, token, historySchema)
            : Promise.resolve(null),
        ]);
        if (alive) {
          setStatus((previous) => mergeStatus(previous, state));
          if (sensorList) setSensors(sensorList);
          if (events) {
            setHistory((previous) =>
              offset === 0
                ? mergeHistory(previous, events.items)
                : events.items,
            );
            setTotal(events.total);
          }
          const resolvedWarning = syncWarning;
          setError((previous) => dismissResolved(previous, resolvedWarning));
          syncWarning = "";
        }
      } catch (e) {
        if (alive) {
          syncWarning =
            e instanceof Error
              ? e.message
              : "API indisponível. Confira se o backend está em execução.";
          setError(syncWarning);
        }
      } finally {
        inFlight = false;
      }
    }
    void sync();
    const interval = setInterval(() => void sync(), 2000);
    return () => {
      alive = false;
      clearInterval(interval);
    };
  }, [token, offset, spatial]);

  function resetSession() {
    pendingFocus.current = "login";
    setToken("");
    setStatus(null);
    setHistory([]);
    setSensors([]);
    setTotal(0);
    setOffset(0);
    setError("");
    setConnection("Desconectado");
    setAllowed(null);
    setIdentity(null);
  }

  async function authenticate(event: React.FormEvent) {
    event.preventDefault();
    // Text typed before hydration is in the field but never reached onChange; the
    // field (no name attribute, so never serialized into a URL) is the source of truth.
    const submitted = tokenInput.current?.value ?? inputToken;
    setBusy(true);
    setError("");
    try {
      const [next, catalog, me] = await Promise.all([
        request("/system/status", submitted, statusSchema),
        request("/capabilities", submitted, capabilityCatalogSchema),
        request("/access/me", submitted, identitySchema),
      ]);
      setStatus(next);
      setAllowed(enabledCapabilities(catalog));
      setIdentity(me);
      pendingFocus.current = "workspace";
      setToken(submitted);
      setInputToken("");
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Não foi possível conectar à API.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function control(
    action: "start" | "pause" | "resume" | "stop" | "reset",
  ) {
    setBusy(true);
    setError("");
    try {
      const body = controlBody(
        action,
        status?.provider ?? "synthetic-native",
        config,
      );
      const next = await request(`/simulation/${action}`, token, statusSchema, {
        method: "POST",
        ...(body === undefined ? {} : { body }),
      });
      setStatus(next);
    } catch (e) {
      setError(
        e instanceof z.ZodError
          ? "Confira os limites de ocupantes, semente e velocidade."
          : e instanceof Error
            ? e.message
            : "Falha no controle da simulação.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function clearHistory() {
    if (
      !window.confirm(
        "Apagar todos os eventos sintéticos? O registro de auditoria será preservado.",
      )
    )
      return;
    setBusy(true);
    setError("");
    try {
      await request(
        "/events/synthetic",
        token,
        z.object({
          deleted: z.literal("L0_SYNTHETIC"),
          audit_preserved: z.literal(true),
        }),
        { method: "DELETE" },
      );
      setOffset(0);
      setHistory([]);
      setTotal(0);
      setStatus(await request("/system/status", token, statusSchema));
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Não foi possível apagar o histórico.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function selectSource(source: "synthetic-native" | "RUVIEW_STREAM") {
    setBusy(true);
    setError("");
    try {
      setStatus(
        await request("/sources/select", token, statusSchema, {
          method: "POST",
          body: JSON.stringify({ source }),
        }),
      );
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Não foi possível selecionar a fonte.",
      );
    } finally {
      setBusy(false);
    }
  }

  const latest = status?.latest ?? null;
  const ruview = status?.provider === "RUVIEW_STREAM";
  const diagnostics = status?.source_diagnostics;
  const disconnected = connection !== "Ao vivo";
  return (
    <div className="shell">
      <aside className="sidebar">
        {/* In-page anchor: a full navigation would drop the in-memory token. */}
        <a className="brand" href="#main">
          <span className="brand-symbol" aria-hidden="true">
            ◈
          </span>
          <span>
            WiFi Spatial<small>Intelligence Platform</small>
          </span>
        </a>
        <nav aria-label="Navegação principal">
          <a href="#network">Diagnóstico Wi-Fi</a>
          {spatial && (
            <>
              <a href="#observatory">Observatório</a>
              <a href="#simulation">Simulação</a>
              <a href="#history">Histórico</a>
            </>
          )}
          {allowed?.has("spatial.occupancy_analytics") && (
            <a href="#analytics">Análises e replay</a>
          )}
          <a href="#capabilities">Capacidades</a>
          {isAdmin && <a href="#access">Perfis de acesso</a>}
          <a href="#governance">Evidência e privacidade</a>
        </nav>
        <div className="sidebar-note">
          <span className="evidence">L0_SYNTHETIC</span>
          <p>
            Laboratório virtual
            <br />
            Diagnóstico de enlace separado
          </p>
          <small>MVP · v0.1.0</small>
        </div>
      </aside>
      <main id="main">
        <header className="page-header">
          <div>
            <p className="muted">Laboratório espacial</p>
            <h1 ref={pageHeading} tabIndex={-1}>
              Spatial Observatory
            </h1>
            <p>Explore presença e movimento em um ambiente virtual.</p>
          </div>
          <div className="connection">
            <span className={`dot ${disconnected ? "offline" : ""}`} />
            <span role="status">{connection}</span>
            {identity && (
              <span className="evidence role-badge" data-testid="role">
                {identityLabel(identity)}
              </span>
            )}
            {token && (
              <button className="text-button" onClick={resetSession}>
                Sair
              </button>
            )}
          </div>
        </header>
        <div className="notice">
          <strong>L0_SYNTHETIC</strong>
          <span>
            {ruview
              ? "Laboratório legado: estimativas sobre sinais sintéticos externos."
              : "Motor sintético nativo: ambiente e ocupantes virtuais."}{" "}
            A cena não representa sensoriamento Wi-Fi ou inferência de IA. O
            diagnóstico do computador é um módulo separado.
          </span>
        </div>
        {error && (
          <div className="error" role="alert">
            {error}
            <button
              className="text-button"
              onClick={() => {
                setError("");
                pageHeading.current?.focus();
              }}
            >
              Fechar aviso
            </button>
          </div>
        )}
        {!token ? (
          <section className="login panel">
            <div>
              <h2>Conecte seu laboratório</h2>
              <p>
                Inicie a API e informe seu token pessoal ou, como administrador,
                o <code>SPATIAL_TOKEN</code> do arquivo <code>.env</code>. O
                token fica apenas na memória desta página.
              </p>
            </div>
            <form onSubmit={authenticate}>
              <label htmlFor="token">Token de acesso local</label>
              <input
                id="token"
                ref={tokenInput}
                type="password"
                autoComplete="off"
                value={inputToken}
                onChange={(e) => setInputToken(e.target.value)}
                required
                minLength={32}
              />
              <button disabled={busy}>
                {busy ? "Conectando…" : "Conectar"}
              </button>
            </form>
          </section>
        ) : (
          <RoleContext value={role}>
            <NetworkPanel token={token} />
            {!spatial ? (
              <section
                className="panel notice"
                aria-labelledby="profile-title"
                data-testid="spatial-disabled"
              >
                <h2 id="profile-title">Módulos espaciais desativados</h2>
                <p>
                  O perfil de capacidades ativo não habilita presença, ocupação,
                  analytics espaciais, laboratório de modelos nem automações
                  (grupo B). Somente o diagnóstico de rede (grupo A) está
                  disponível. Veja o enquadramento em Capacidades.
                </p>
              </section>
            ) : (
              <>
                <div className="workspace">
                  <section id="observatory" className="panel spatial-panel">
                    <div className="panel-heading">
                      <div>
                        <h2 ref={workspaceHeading} tabIndex={-1}>
                          Laboratório virtual
                        </h2>
                        <p>
                          {ruview
                            ? "RuView · fluxo simulado externo"
                            : "8 × 6 m · seis sensores virtuais"}
                        </p>
                      </div>
                      <span className={`state ${status?.state}`}>
                        {status ? states[status.state] : "Carregando"}
                      </span>
                    </div>
                    <Observatory
                      event={latest}
                      sensors={ruview ? [] : sensors}
                      connected={status?.connected ?? false}
                    />
                    {ruview && (
                      <p className="notice">
                        RuView fornece presença e contagem estimadas sobre
                        sinais sintéticos. Posições de verdade indisponíveis;
                        nenhum ocupante é desenhado no mapa.
                      </p>
                    )}
                    <div className="map-legend">
                      <span>
                        <i className="sensor-key" />
                        Sensor virtual
                      </span>
                      <span>
                        <i className="person-key" />
                        Ocupante sintético
                      </span>
                      <span>Grade: 1 m</span>
                    </div>
                    <div className="metrics">
                      <div>
                        <span>
                          {ruview
                            ? "Presença em sinal sintético"
                            : "Presença sintética"}
                        </span>
                        <strong data-testid="presence">
                          {!latest
                            ? "Sem observação"
                            : latest.measurements.presence_detected
                              ? "Detectada"
                              : "Ausente"}
                        </strong>
                      </div>
                      <div>
                        <span>
                          {ruview
                            ? "Contagem em sinal sintético"
                            : "Ocupação sintética"}
                        </span>
                        <strong data-testid="occupancy">
                          {latest?.measurements.occupancy_estimate ?? "—"}
                          <small>ocupantes</small>
                        </strong>
                      </div>
                      <div>
                        <span>Última observação</span>
                        <strong className="time">
                          {latest ? time(latest.timestamp) : "—"}
                        </strong>
                        <small>
                          {disconnected || (ruview && diagnostics?.stale)
                            ? "Conexão interrompida; dados podem estar desatualizados"
                            : status?.state === "running"
                              ? "Atualização em tempo real"
                              : "Simulação sem produzir eventos"}
                        </small>
                      </div>
                    </div>
                  </section>
                  <section id="simulation" className="panel controls">
                    <h2>Simulação</h2>
                    {!canOperate && (
                      <p data-testid="read-only">
                        Seu papel permite acompanhar a simulação; iniciar,
                        pausar e trocar a fonte exigem o papel Operação.
                      </p>
                    )}
                    {canOperate && (
                      <>
                        <label htmlFor="source">Fonte de dados</label>
                        <select
                          id="source"
                          value={status?.provider ?? "synthetic-native"}
                          disabled={busy || status?.state !== "stopped"}
                          onChange={(e) =>
                            void selectSource(
                              e.target.value as
                                "synthetic-native" | "RUVIEW_STREAM",
                            )
                          }
                        >
                          <option value="synthetic-native">
                            Motor sintético nativo
                          </option>
                          <option
                            value="RUVIEW_STREAM"
                            disabled={!status?.legacy_lab_enabled}
                          >
                            Laboratório legado · RuView simulado
                          </option>
                        </select>
                        <p>
                          {ruview
                            ? "Inicie o serviço RuView em modo simulated. Cenário, semente e cadência são definidos pelo serviço externo."
                            : "Configure uma cena reproduzível."}
                        </p>
                        {!ruview && (
                          <>
                            <fieldset
                              disabled={busy || status?.state !== "stopped"}
                            >
                              <label htmlFor="scenario">Cenário</label>
                              <select
                                id="scenario"
                                value={config.scenario}
                                onChange={(e) =>
                                  setConfig({
                                    ...config,
                                    scenario: e.target
                                      .value as SimulationConfig["scenario"],
                                  })
                                }
                              >
                                {Object.entries(scenarios).map(
                                  ([value, label]) => (
                                    <option key={value} value={value}>
                                      {label}
                                    </option>
                                  ),
                                )}
                              </select>
                              <div className="form-grid">
                                <div>
                                  <label htmlFor="occupants">Ocupantes</label>
                                  <input
                                    id="occupants"
                                    type="number"
                                    min={0}
                                    max={20}
                                    value={config.occupants}
                                    onChange={(e) =>
                                      setConfig({
                                        ...config,
                                        occupants: Number(e.target.value),
                                      })
                                    }
                                  />
                                </div>
                                <div>
                                  <label htmlFor="seed">Semente</label>
                                  <input
                                    id="seed"
                                    type="number"
                                    min={0}
                                    max={4294967295}
                                    value={config.seed}
                                    onChange={(e) =>
                                      setConfig({
                                        ...config,
                                        seed: Number(e.target.value),
                                      })
                                    }
                                  />
                                </div>
                              </div>
                              <label htmlFor="speed">Velocidade</label>
                              <select
                                id="speed"
                                value={config.speed}
                                onChange={(e) =>
                                  setConfig({
                                    ...config,
                                    speed: Number(e.target.value),
                                  })
                                }
                              >
                                {[0.25, 0.5, 1, 2, 4].map((n) => (
                                  <option key={n} value={n}>
                                    {n}×
                                  </option>
                                ))}
                              </select>
                            </fieldset>
                          </>
                        )}
                        <div className="actions">
                          <button
                            disabled={
                              busy || !status || status.state !== "stopped"
                            }
                            onClick={() => void control("start")}
                          >
                            Iniciar simulação
                          </button>
                          <button
                            className="secondary"
                            disabled={busy || status?.state !== "running"}
                            onClick={() => void control("pause")}
                          >
                            Pausar
                          </button>
                          <button
                            className="secondary"
                            disabled={busy || status?.state !== "paused"}
                            onClick={() => void control("resume")}
                          >
                            Continuar
                          </button>
                          <button
                            className="secondary"
                            disabled={
                              busy || !status || status.state === "stopped"
                            }
                            onClick={() => void control("stop")}
                          >
                            Parar
                          </button>
                          <button
                            className="secondary"
                            disabled={
                              busy || !status || status.state !== "stopped"
                            }
                            onClick={() => void control("reset")}
                          >
                            Reiniciar estado
                          </button>
                        </div>
                      </>
                    )}
                    <dl className="telemetry">
                      <div>
                        <dt>Taxa medida (janela até 60 s)</dt>
                        <dd>
                          {status?.metrics?.event_rate.toFixed(2) ?? "—"}{" "}
                          eventos/s
                        </dd>
                      </div>
                      <div>
                        <dt>Espera p95 medida</dt>
                        <dd>
                          {status?.metrics?.queue_wait_p95_ms?.toFixed(3) ??
                            "—"}{" "}
                          ms
                        </dd>
                      </div>
                      <div>
                        <dt>Descarte de visualização</dt>
                        <dd>
                          {status?.metrics?.visualization_drop_rate == null
                            ? "—"
                            : `${(status.metrics.visualization_drop_rate * 100).toFixed(2)}%`}
                        </dd>
                      </div>
                      <div>
                        <dt>Eventos nesta sessão</dt>
                        <dd>{status?.produced_events ?? 0}</dd>
                      </div>
                      <div>
                        <dt>Fila de processamento</dt>
                        <dd>{status?.queue_depth ?? 0}</dd>
                      </div>
                      <div>
                        <dt>Descartes na transmissão</dt>
                        <dd>{status?.dropped_visualization_events ?? 0}</dd>
                      </div>
                      <div>
                        <dt>Espera na fila</dt>
                        <dd>
                          {latest?.processing_latency_ms?.toFixed(1) ?? "—"} ms
                        </dd>
                      </div>
                    </dl>
                    {ruview && diagnostics && (
                      <section
                        aria-label="Diagnósticos RuView"
                        data-testid="ruview-diagnostics"
                      >
                        <h3>Diagnósticos RuView</h3>
                        <dl className="telemetry">
                          <div>
                            <dt>Serviço</dt>
                            <dd>{services[diagnostics.service_status]}</dd>
                          </div>
                          <div>
                            <dt>Frames aceitos</dt>
                            <dd>{diagnostics.received_frames}</dd>
                          </div>
                          <div>
                            <dt>Frames rejeitados</dt>
                            <dd>{diagnostics.rejected_frames}</dd>
                          </div>
                          <div>
                            <dt>Frames ignorados / duplicados</dt>
                            <dd>
                              {diagnostics.ignored_frames} /{" "}
                              {diagnostics.duplicate_frames}
                            </dd>
                          </div>
                          <div>
                            <dt>Reconexões</dt>
                            <dd>{diagnostics.reconnections}</dd>
                          </div>
                          <div>
                            <dt>Idade do dado</dt>
                            <dd>
                              {diagnostics.last_event_age_seconds?.toFixed(1) ??
                                "—"}{" "}
                              s
                            </dd>
                          </div>
                          <div>
                            <dt>Qualidade</dt>
                            <dd>
                              {diagnostics.stale
                                ? "Sem dados recentes"
                                : "Fluxo sintético recente"}
                            </dd>
                          </div>
                        </dl>
                        <p>
                          Origem: RuView / simulated · L0_SYNTHETIC. Sem
                          confiança medida, posições de verdade ou validação
                          científica.
                        </p>
                        {diagnostics.last_error && (
                          <p className="error" role="alert">
                            Diagnóstico do serviço (inglês):{" "}
                            <span lang="en">{diagnostics.last_error}</span>
                          </p>
                        )}
                      </section>
                    )}
                    {status?.error && (
                      <p className="error" role="alert">
                        Mensagem da API (inglês):{" "}
                        <span lang="en">{status.error}</span>
                      </p>
                    )}
                  </section>
                </div>
                <section id="history" className="panel history">
                  <div className="panel-heading">
                    <div>
                      <h2>Histórico de eventos</h2>
                      <p>{total} eventos persistidos localmente em SQLite</p>
                    </div>
                    {isAdmin && (
                      <button
                        className="text-button"
                        disabled={
                          busy || status?.state !== "stopped" || total === 0
                        }
                        onClick={() => void clearHistory()}
                      >
                        Apagar eventos sintéticos
                      </button>
                    )}
                  </div>
                  {history.length ? (
                    <div
                      className="table-scroll"
                      role="region"
                      aria-label="Tabela de eventos com rolagem horizontal"
                      tabIndex={0}
                    >
                      <table>
                        <thead>
                          <tr>
                            <th>Horário local</th>
                            <th>Cenário</th>
                            <th>Origem</th>
                            <th>Ocupação</th>
                            <th>Presença</th>
                            <th>Evidência</th>
                            <th>Tick</th>
                          </tr>
                        </thead>
                        <tbody>
                          {history.map((event) => (
                            <tr key={event.event_id}>
                              <td>
                                <time dateTime={event.timestamp}>
                                  {new Date(event.timestamp).toLocaleString(
                                    "pt-BR",
                                  )}
                                </time>
                              </td>
                              <td>
                                {event.provenance.scenario ===
                                "ruview-simulated"
                                  ? "Simulação RuView"
                                  : scenarioLabel(event.provenance.scenario)}
                              </td>
                              <td>
                                {event.source_id === "ruview-01"
                                  ? "RuView / simulated"
                                  : "Simulador interno"}
                              </td>
                              <td>
                                {event.measurements.occupancy_estimate ??
                                  "Indisponível"}
                              </td>
                              <td>
                                {event.measurements.presence_detected
                                  ? "Detectada"
                                  : "Ausente"}
                              </td>
                              <td>
                                <span className="evidence">
                                  {event.evidence_level}
                                </span>
                              </td>
                              <td>{event.provenance.tick}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="empty">
                      <h3>Nenhum evento nesta página</h3>
                      <p>
                        Inicie uma simulação para registrar observações
                        sintéticas.
                      </p>
                    </div>
                  )}
                  <div className="pagination">
                    <span>
                      {total
                        ? `${offset + 1}–${Math.min(offset + 20, total)} de ${total}`
                        : "0 eventos"}
                    </span>
                    <button
                      className="secondary"
                      disabled={offset === 0}
                      onClick={() => setOffset(Math.max(0, offset - 20))}
                    >
                      Anterior
                    </button>
                    <button
                      className="secondary"
                      disabled={offset + 20 >= total}
                      onClick={() => setOffset(offset + 20)}
                    >
                      Próxima
                    </button>
                  </div>
                </section>
              </>
            )}
            {allowed?.has("spatial.occupancy_analytics") && (
              <AnalyticsPanel token={token} />
            )}
            {allowed?.has("spatial.activity_baseline") && (
              <ModelLabPanel token={token} />
            )}
            {allowed?.has("automation.dry_run_rules") && (
              <AutomationPanel token={token} />
            )}
            <CapabilitiesPanel token={token} />
            {isAdmin && <AccessPanel token={token} />}
          </RoleContext>
        )}
        <footer id="governance">
          <div>
            <h2>Evidência e privacidade</h2>
            <p>
              Fonte: {ruview ? "RuView simulado" : "simulador local"}. Nível:{" "}
              <strong>L0_SYNTHETIC</strong>. Nenhum sinal CSI, dado biométrico,
              câmera ou microfone é coletado. Baseline geométrico sintético
              separado, sem modelo RF ou validação real. O diagnóstico Wi-Fi
              registra telemetria de enlace do computador em módulo próprio, sem
              CSI.
            </p>
          </div>
          <p>
            Retenção padrão: 10.000 eventos. Exclusão disponível com a simulação
            parada; a auditoria de controles é preservada.
          </p>
        </footer>
      </main>
    </div>
  );
}
