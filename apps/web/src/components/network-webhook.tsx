"use client";

import { useEffect, useState } from "react";
import { z } from "zod";
import { request } from "../lib/api";
import { webhookStatusSchema, type WebhookStatus } from "../lib/network";

const events = {
  "alert.raised": "Alerta enviado",
  "alert.cleared": "Alerta encerrado",
  "webhook.test": "Teste",
};

export default function NetworkWebhookView({ token }: { token: string }) {
  const [status, setStatus] = useState<WebhookStatus | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    let alive = true;
    async function sync() {
      try {
        const next = await request(
          "/network/webhook",
          token,
          webhookStatusSchema,
        );
        if (alive) {
          setStatus(next);
          setError("");
        }
      } catch (e) {
        if (alive)
          setError(
            e instanceof Error ? e.message : "Falha ao consultar o webhook.",
          );
      }
    }
    void sync();
    return () => {
      alive = false;
    };
  }, [token, revision]);
  async function sendTest() {
    setBusy(true);
    setMessage("");
    try {
      const result = await request(
        "/network/webhook/test",
        token,
        z.object({ delivered: z.boolean() }).loose(),
        { method: "POST" },
      );
      setMessage(
        result.delivered
          ? "Teste entregue ao receptor local."
          : "O receptor não confirmou o teste; veja o histórico abaixo.",
      );
      setRevision((value) => value + 1);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Falha ao enviar o teste.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <section
      className="network-webhook"
      aria-labelledby="network-webhook-title"
    >
      <h3 id="network-webhook-title">Notificação local de alertas</h3>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <p role="status" className="live">
        {message}
      </p>
      {status &&
        (status.configured ? (
          <>
            <p data-testid="webhook-state">
              Enviando para <strong>{status.destination}</strong> a cada{" "}
              {status.interval_seconds} s · {status.active_alerts} alerta(s)
              ativo(s). Assinatura HMAC-SHA256; só notifica, não age na rede.
            </p>
            <button
              type="button"
              className="secondary"
              disabled={busy}
              onClick={() => void sendTest()}
            >
              Enviar teste
            </button>
            {status.deliveries.length > 0 && (
              <ul className="webhook-deliveries">
                {status.deliveries.slice(0, 5).map((item) => (
                  <li key={item.id}>
                    {new Date(item.created_at).toLocaleString("pt-BR")} ·{" "}
                    {events[item.event]}
                    {item.alert_code ? ` (${item.alert_code})` : ""} ·{" "}
                    {item.delivered
                      ? "entregue"
                      : `falhou${item.error ? `: ${item.error}` : ""}`}
                  </li>
                ))}
              </ul>
            )}
          </>
        ) : (
          <p data-testid="webhook-state">
            Não configurado. Defina SPATIAL_ALERT_WEBHOOK_URL (IP local ou de
            rede privada) e SPATIAL_ALERT_WEBHOOK_SECRET no .env do servidor.
          </p>
        ))}
    </section>
  );
}
