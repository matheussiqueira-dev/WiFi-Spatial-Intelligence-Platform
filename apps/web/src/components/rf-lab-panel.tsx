"use client";

import { useEffect, useState } from "react";
import { request } from "../lib/api";
import {
  commercialUse,
  evaluationRows,
  fingerprintEvaluationSchema,
  modelRegistrySchema,
  type FingerprintEvaluation,
  type ModelRegistry,
} from "../lib/rf-lab";
import { useAllows } from "./role-context";

const integrity = {
  VERIFIED: "Íntegro",
  MISMATCH: "Checksum divergente",
  UNREADABLE: "Ilegível",
};

export default function RfLabPanel({
  token,
  fingerprint,
  registry,
}: {
  token: string;
  fingerprint: boolean;
  registry: boolean;
}) {
  const canOperate = useAllows("operator");
  const [seed, setSeed] = useState(42);
  const [result, setResult] = useState<FingerprintEvaluation | null>(null);
  const [models, setModels] = useState<ModelRegistry | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    if (!registry) return;
    let alive = true;
    request("/model-lab/models", token, modelRegistrySchema)
      .then((next) => {
        if (alive) setModels(next);
      })
      .catch((e) => {
        if (alive)
          setError(
            e instanceof Error ? e.message : "Falha ao carregar o registro.",
          );
      });
    return () => {
      alive = false;
    };
  }, [token, registry, result]);
  async function run() {
    setBusy(true);
    setError("");
    try {
      setResult(
        await request(
          "/model-lab/rf-fingerprint/evaluations",
          token,
          fingerprintEvaluationSchema,
          { method: "POST", body: JSON.stringify({ seed }) },
        ),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Falha na avaliação.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <section
      id="rf-lab"
      className="panel analytics"
      aria-labelledby="rf-lab-title"
    >
      <h2 id="rf-lab-title">Impressão RF do ambiente e registro de modelos</h2>
      <p className="muted">
        L0_SYNTHETIC · quadros SWF1 simulados, autenticados e recebidos como os
        de um sensor pareado. Indica só que o canal mudou em relação à
        referência; não identifica objeto, pessoa nem causa.
      </p>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {fingerprint && (
        <section aria-labelledby="rf-fingerprint-title">
          <h3 id="rf-fingerprint-title">Avaliação sintética</h3>
          <div className="network-controls">
            <label>
              Semente
              <input
                type="number"
                min={0}
                max={100000}
                value={seed}
                onChange={(e) => setSeed(Number(e.target.value))}
              />
            </label>
            <button
              type="button"
              hidden={!canOperate}
              disabled={
                busy || !Number.isInteger(seed) || seed < 0 || seed > 100000
              }
              onClick={() => void run()}
            >
              {busy ? "Avaliando…" : "Avaliar impressão RF"}
            </button>
          </div>
          <div role="status" className="live">
            {result
              ? `Avaliação concluída com ${result.frames_received} quadros sintéticos.`
              : ""}
          </div>
          {result && (
            <>
              <dl className="rf-results" data-testid="rf-results">
                {evaluationRows(result).map((row) => (
                  <div key={row.label}>
                    <dt>{row.label}</dt>
                    <dd>{row.value}</dd>
                  </div>
                ))}
              </dl>
              <ul>
                {result.limitations.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </>
          )}
        </section>
      )}
      {registry && models && (
        <section aria-labelledby="registry-title">
          <h3 id="registry-title">Registro de modelos</h3>
          {models.project.length === 0 && models.third_party.length === 0 ? (
            <p>Nenhum modelo registrado. Rode um experimento acima.</p>
          ) : (
            <div
              className="table-scroll"
              role="region"
              aria-label="Modelos registrados"
              tabIndex={0}
            >
              <table>
                <thead>
                  <tr>
                    <th>Modelo</th>
                    <th>Origem</th>
                    <th>Licença</th>
                    <th>SHA-256</th>
                    <th>Situação</th>
                  </tr>
                </thead>
                <tbody>
                  {models.project.map((item) => (
                    <tr key={item.sha256}>
                      <td>
                        {item.id} {item.version}
                      </td>
                      <td>Projeto (L0)</td>
                      <td>{item.license}</td>
                      <td>
                        <code>{item.sha256.slice(0, 12)}…</code>
                      </td>
                      <td data-testid="model-integrity">
                        {integrity[item.integrity]}
                      </td>
                    </tr>
                  ))}
                  {models.third_party.map((item) => (
                    <tr key={item.id}>
                      <td>
                        {item.name} {item.version}
                      </td>
                      <td>Terceiro (ficha, não carregado)</td>
                      <td>{item.license}</td>
                      <td>
                        <code>{item.sha256.slice(0, 12)}…</code>
                      </td>
                      <td>{commercialUse[item.commercial_use]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </section>
  );
}
