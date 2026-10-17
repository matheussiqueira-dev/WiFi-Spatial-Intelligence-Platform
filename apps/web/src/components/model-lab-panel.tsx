"use client";

import { useState, useEffect } from "react";
import { z } from "zod";
import { request } from "../lib/api";
import { useAllows } from "./role-context";
import {
  experimentSchema,
  experimentListSchema,
  type Experiment,
  jobSchema,
} from "../lib/model-lab";
import { download } from "../lib/analytics";

export default function ModelLabPanel({ token }: { token: string }) {
  const canOperate = useAllows("operator");
  const [seed, setSeed] = useState(42);
  const [result, setResult] = useState<Experiment | null>(null);
  const [items, setItems] = useState<{ id: string; created_at: string }[]>([]);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [job, setJob] = useState<z.infer<typeof jobSchema> | null>(null);
  const jobActive =
    job &&
    ["queued", "preparing", "training", "persisting"].includes(job.state);
  const jobId = job?.id;
  // Persisted history is shown on mount instead of a misleading "0 experiments".
  useEffect(() => {
    let cancelled = false;
    request(`/model-lab/runs?limit=5&offset=0`, token, experimentListSchema)
      .then((data) => {
        if (cancelled) return;
        setItems(data.items);
        setTotal(data.total);
        setOffset(0);
      })
      .catch((e) => {
        if (!cancelled)
          setError(e instanceof Error ? e.message : "Falha no histórico");
      });
    return () => {
      cancelled = true;
    };
  }, [token]);
  useEffect(() => {
    if (!jobActive || !jobId) return;
    let cancelled = false;
    let pending = false;
    const identifier = jobId;
    const timer = setInterval(async () => {
      if (pending) return;
      pending = true;
      try {
        const next = await request(
          `/model-lab/jobs/${identifier}`,
          token,
          jobSchema,
        );
        if (cancelled) return;
        if (next.state === "completed" && next.run_id) {
          const [run, list] = await Promise.all([
            request(`/model-lab/runs/${next.run_id}`, token, experimentSchema),
            request(
              `/model-lab/runs?limit=5&offset=0`,
              token,
              experimentListSchema,
            ),
          ]);
          if (!cancelled) {
            setResult(run);
            setItems(list.items);
            setTotal(list.total);
            setOffset(0);
          }
        }
        if (!cancelled) setJob(next);
      } catch (e) {
        if (!cancelled)
          setError(e instanceof Error ? e.message : "Erro no job");
      } finally {
        pending = false;
      }
    }, 500);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [jobId, jobActive, token]);
  async function execute(action: () => Promise<void>) {
    setBusy(true);
    setError("");
    try {
      await action();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Falha no laboratório");
    } finally {
      setBusy(false);
    }
  }
  async function history(nextOffset = 0) {
    const data = await request(
      `/model-lab/runs?limit=5&offset=${nextOffset}`,
      token,
      experimentListSchema,
    );
    setItems(data.items);
    setTotal(data.total);
    setOffset(nextOffset);
  }
  const percent = (n: number | null) =>
    n === null ? "indisponível" : `${(n * 100).toFixed(1)}%`;
  return (
    <section className="panel analytics" aria-labelledby="model-lab-title">
      <h2 id="model-lab-title">Laboratório de movimento sintético</h2>
      <p>
        Baseline sobre geometria de um ponto virtual. L0_SYNTHETIC. Não
        reconhece atividade humana nem mede RF. A cena ao vivo permanece
        independente. Os períodos das janelas são segundos relativos virtuais,
        não horários de captura.
      </p>
      <label>
        Semente do experimento
        <input
          type="number"
          min={0}
          max={100000}
          value={seed}
          onChange={(e) => setSeed(Number(e.target.value))}
        />
      </label>
      <div className="toolbar">
        <button
          hidden={!canOperate}
          disabled={
            busy ||
            !!jobActive ||
            !Number.isInteger(seed) ||
            seed < 0 ||
            seed > 100000
          }
          onClick={() =>
            execute(async () => {
              setJob(
                await request("/model-lab/jobs", token, jobSchema, {
                  method: "POST",
                  body: JSON.stringify({ seed }),
                }),
              );
            })
          }
        >
          Enfileirar baseline
        </button>
        <button
          className="secondary"
          hidden={!canOperate}
          disabled={busy || !jobActive}
          onClick={() =>
            execute(async () => {
              if (job)
                await request(
                  `/model-lab/jobs/${job.id}/cancel`,
                  token,
                  z.object({ cancel_requested: z.literal(true) }),
                  { method: "POST" },
                );
            })
          }
        >
          Cancelar experimento enfileirado
        </button>
        <button
          hidden={!canOperate}
          disabled={
            busy || !Number.isInteger(seed) || seed < 0 || seed > 100000
          }
          onClick={() =>
            execute(async () => {
              setResult(
                await request("/model-lab/runs", token, experimentSchema, {
                  method: "POST",
                  body: JSON.stringify({ seed }),
                }),
              );
              await history();
            })
          }
        >
          Treinar e avaliar baseline
        </button>
        <button
          className="secondary"
          disabled={busy}
          onClick={() => execute(() => history())}
        >
          Consultar experimentos
        </button>
      </div>
      {/* Live regions stay mounted so screen readers announce later changes. */}
      <p role="status" aria-label="Estado do job" className="live">
        {job && (
          <>
            Job {job.state} · etapa {job.progress}% · L0_SYNTHETIC
            {job.error ? (
              <>
                {" "}
                · <span lang="en">{job.error}</span>
              </>
            ) : (
              ""
            )}
            . Cancelamento cooperativo antes da persistência.
          </>
        )}
      </p>
      <p role="status" className="live">
        {busy ? "Executando experimento limitado na CPU local…" : ""}
      </p>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {!result && (
        <p>
          Nenhum experimento aberto. Execute ou consulte o histórico persistido.
        </p>
      )}
      {result && (
        <section aria-labelledby="model-lab-result-title">
          <h3 id="model-lab-result-title">Resultado do experimento</h3>
          <p>
            <strong>L0_SYNTHETIC</strong> · {result.model.id} ·{" "}
            {result.model.version}
          </p>
          <p>
            Executado em {new Date(result.created_at).toLocaleString("pt-BR")} ·{" "}
            {result.duration_ms.toFixed(1)} ms · semente {result.seed}
          </p>
          <p>
            Dataset {result.dataset_version} · {result.evaluation.samples}{" "}
            janelas de teste; sessões separadas em treino/validação/teste.
          </p>
          <p>
            Acurácia sintética entre aceitos:{" "}
            {percent(result.evaluation.accuracy_accepted)}. Rejeição:{" "}
            {percent(result.evaluation.rejection_rate)}. Falso positivo:{" "}
            {percent(result.evaluation.false_positive_rate)}.
          </p>
          <p>
            Sem suporte: {result.unsupported.join(", ")}. Esses resultados não
            estimam desempenho real.
          </p>
          <details>
            <summary>Identificadores e parâmetros reproduzíveis</summary>
            <p className="lab-hash">Modelo SHA-256: {result.model.sha256}</p>
            <p className="lab-hash">Dataset SHA-256: {result.dataset_sha256}</p>
            <p>
              Limiar treinado: {result.model.threshold_m_per_s.toFixed(4)} m/s
              virtual. Sem confiança científica atribuída.
            </p>
          </details>
          <div
            className="table-scroll"
            role="region"
            aria-label="Matriz de confusão sintética"
            tabIndex={0}
          >
            <table>
              <caption>
                Referência por linha; predição por coluna, incluindo rejeição
                unknown
              </caption>
              <thead>
                <tr>
                  <th>Referência / suporte</th>
                  {result.evaluation.classes.map((c) => (
                    <th key={c}>{c}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.evaluation.classes.map((c, i) => (
                  <tr key={c}>
                    <th>
                      {c} / {result.evaluation.support[c]}
                    </th>
                    {result.evaluation.confusion_matrix[i].map((n, j) => (
                      <td key={j}>{n}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div
            className="table-scroll"
            role="region"
            aria-label="Predições por janela sintética"
            tabIndex={0}
          >
            <table>
              <thead>
                <tr>
                  <th>Sessão / janela</th>
                  <th>Predição</th>
                  <th>Referência</th>
                  <th>Qualidade geométrica</th>
                  <th>Período virtual (s)</th>
                </tr>
              </thead>
              <tbody>
                {result.evaluation.predictions.map((p) => (
                  <tr key={`${p.session_id}-${p.window}`}>
                    <td>
                      {p.session_id} / {p.window}
                    </td>
                    <td>{p.prediction}</td>
                    <td>{p.reference}</td>
                    <td>{p.quality}</td>
                    <td>
                      {p.start_seconds.toFixed(1)}–{p.end_seconds.toFixed(1)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <button
            className="secondary"
            onClick={() =>
              download(
                "synthetic-experiment.json",
                JSON.stringify(result, null, 2),
                "application/json",
              )
            }
          >
            Exportar experimento JSON
          </button>
        </section>
      )}
      <ul>
        {items.map((item) => (
          <li key={item.id}>
            <button
              className="secondary"
              disabled={busy}
              onClick={() =>
                execute(async () =>
                  setResult(
                    await request(
                      `/model-lab/runs/${item.id}`,
                      token,
                      experimentSchema,
                    ),
                  ),
                )
              }
            >
              Abrir experimento{" "}
              {new Date(item.created_at).toLocaleString("pt-BR")}
            </button>
          </li>
        ))}
      </ul>
      <div className="pagination">
        <span>
          {total === null
            ? "Histórico ainda não consultado"
            : `${total} experimentos persistidos`}
        </span>
        <button
          className="secondary"
          disabled={busy || offset === 0}
          onClick={() => execute(() => history(offset - 5))}
        >
          Experimentos anteriores
        </button>
        <button
          className="secondary"
          disabled={busy || total === null || offset + 5 >= total}
          onClick={() => execute(() => history(offset + 5))}
        >
          Mais experimentos
        </button>
      </div>
    </section>
  );
}
