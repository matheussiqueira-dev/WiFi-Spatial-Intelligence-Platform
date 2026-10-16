"use client";

import { useEffect, useState } from "react";
import { request } from "../lib/api";
import {
  capabilityCatalogSchema,
  groupLabels,
  regulatoryLabels,
  type CapabilityCatalog,
} from "../lib/capabilities";

export default function CapabilitiesPanel({ token }: { token: string }) {
  const [data, setData] = useState<CapabilityCatalog | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let alive = true;
    request("/capabilities", token, capabilityCatalogSchema)
      .then((next) => {
        if (alive) setData(next);
      })
      .catch((e: unknown) => {
        if (alive)
          setError(
            e instanceof Error ? e.message : "Falha ao consultar o catálogo.",
          );
      });
    return () => {
      alive = false;
    };
  }, [token]);
  return (
    <section
      id="capabilities"
      className="panel capabilities-panel"
      aria-labelledby="capabilities-title"
    >
      <div className="panel-heading">
        <div>
          <p className="muted">Catálogo de capacidades</p>
          <h2 id="capabilities-title">Capacidades e enquadramento</h2>
        </div>
        {data && (
          <span className="network-badge" data-testid="capability-profile">
            Perfil: {data.profile}
          </span>
        )}
      </div>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {!data ? (
        !error && <p role="status">Carregando catálogo…</p>
      ) : (
        <>
          <p className="network-details">{data.disclaimer}</p>
          <div
            className="table-scroll"
            role="region"
            aria-label="Catálogo de capacidades"
            tabIndex={0}
          >
            <table>
              <thead>
                <tr>
                  <th>Grupo</th>
                  <th>Capacidade</th>
                  <th>Status</th>
                  <th>Evidência máxima</th>
                  <th>Enquadramento</th>
                  <th>Neste perfil</th>
                </tr>
              </thead>
              <tbody>
                {data.capabilities.map((item) => (
                  <tr key={item.id}>
                    <td>{groupLabels[item.group]}</td>
                    <td>
                      {item.name}
                      <small className="capability-note">{item.note}</small>
                    </td>
                    <td>{item.status}</td>
                    <td>{item.evidence_ceiling ?? "—"}</td>
                    <td>
                      {item.regulatory
                        .map((tag) => regulatoryLabels[tag])
                        .join("; ")}
                      {item.requires_consent && " · exige consentimento"}
                      {item.requires_hardware && " · exige hardware"}
                    </td>
                    <td>{item.enabled ? "Ligada" : "Desligada"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
}
