"use client";

import { useEffect, useState } from "react";
import { z } from "zod";
import { request } from "../lib/api";
import {
  roleLabels,
  roles,
  tokenCreatedSchema,
  tokenListSchema,
  type Role,
} from "../lib/access";

const when = (timestamp: string | null) =>
  timestamp ? new Date(timestamp).toLocaleString("pt-BR") : "nunca";

/** Admin-only: issue, list and revoke personal tokens. Values never leave React state. */
export default function AccessPanel({ token }: { token: string }) {
  const [list, setList] = useState<z.infer<typeof tokenListSchema> | null>(
    null,
  );
  const [label, setLabel] = useState("");
  const [role, setRole] = useState<Role>("viewer");
  // The new token is shown once; cleared on dismiss, logout or the next creation.
  const [issued, setIssued] = useState<{ label: string; token: string } | null>(
    null,
  );
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState("");

  useEffect(() => {
    let cancelled = false;
    request("/access/tokens", token, tokenListSchema)
      .then((next) => {
        if (!cancelled) setList(next);
      })
      .catch((e) => {
        if (!cancelled)
          setError(e instanceof Error ? e.message : "Erro ao carregar tokens");
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  async function perform(action: () => Promise<void>) {
    setBusy(true);
    setError("");
    try {
      await action();
      setList(await request("/access/tokens", token, tokenListSchema));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro na gestão de tokens");
    } finally {
      setBusy(false);
    }
  }

  function create(event: React.FormEvent) {
    event.preventDefault();
    setCopied("");
    setIssued(null);
    void perform(async () => {
      const created = await request(
        "/access/tokens",
        token,
        tokenCreatedSchema,
        {
          method: "POST",
          body: JSON.stringify({ label: label.trim(), role }),
        },
      );
      setIssued({ label: created.label, token: created.token });
      setLabel("");
    });
  }

  async function copy() {
    if (!issued) return;
    try {
      await navigator.clipboard.writeText(issued.token);
      setCopied("Token copiado para a área de transferência.");
    } catch {
      setCopied(
        "Não foi possível copiar; selecione o campo e copie manualmente.",
      );
    }
  }

  return (
    <section
      id="access"
      className="panel analytics"
      aria-labelledby="access-title"
      data-testid="access-panel"
    >
      <h2 id="access-title">Perfis de acesso</h2>
      <p>
        Emita um token por pessoa. Leitura só consulta; Operação controla a
        simulação, o ponto de medição e as regras; Administração gerencia tokens
        e apaga históricos. Somente o hash do token fica no banco: o valor
        aparece uma única vez.
      </p>
      <form className="network-location" onSubmit={create}>
        <label>
          Nome da pessoa ou dispositivo
          <input
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            maxLength={48}
            required
          />
        </label>
        <label>
          Papel
          <select
            value={role}
            onChange={(e) => setRole(e.target.value as Role)}
          >
            {roles.map((value) => (
              <option key={value} value={value}>
                {roleLabels[value]}
              </option>
            ))}
          </select>
        </label>
        <button disabled={busy || !label.trim()}>Emitir token</button>
      </form>
      {issued && (
        <div className="notice" data-testid="issued-token">
          <label>
            Token de {issued.label} (exibido somente agora)
            <input
              type="text"
              readOnly
              autoComplete="off"
              spellCheck={false}
              value={issued.token}
              onFocus={(e) => e.target.select()}
            />
          </label>
          <div className="toolbar">
            <button type="button" onClick={() => void copy()}>
              Copiar token
            </button>
            <button
              type="button"
              className="secondary"
              onClick={() => {
                setIssued(null);
                setCopied("");
              }}
            >
              Já guardei, ocultar
            </button>
          </div>
          <p role="status">{copied}</p>
        </div>
      )}
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {list === null ? (
        <p>Carregando tokens…</p>
      ) : list.items.length === 0 ? (
        <p>
          Nenhum token pessoal emitido. O SPATIAL_TOKEN do .env continua como
          administrador de bootstrap.
        </p>
      ) : (
        <div
          className="table-scroll"
          role="region"
          aria-label="Tokens de acesso emitidos"
          tabIndex={0}
        >
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Papel</th>
                <th>Criado</th>
                <th>Último uso</th>
                <th>Situação</th>
              </tr>
            </thead>
            <tbody>
              {list.items.map((item) => (
                <tr key={item.id} data-token-id={item.id}>
                  <td>{item.label}</td>
                  <td>{roleLabels[item.role]}</td>
                  <td>{when(item.created_at)}</td>
                  <td>{when(item.last_used_at)}</td>
                  <td>
                    {item.active ? (
                      <button
                        className="secondary"
                        disabled={busy}
                        onClick={() => {
                          if (
                            window.confirm(
                              `Revogar o token de ${item.label}? O acesso termina imediatamente.`,
                            )
                          )
                            void perform(async () => {
                              await request(
                                `/access/tokens/${item.id}/revoke`,
                                token,
                                z.object({ revoked: z.literal(true) }),
                                { method: "POST" },
                              );
                            });
                        }}
                      >
                        Revogar {item.label}
                      </button>
                    ) : (
                      `Revogado ${when(item.revoked_at)}`
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <small>
        Até {list?.maximum_active ?? 50} tokens ativos. Revogados permanecem
        listados para auditoria.
      </small>
    </section>
  );
}
