import { z } from "zod";
import { configSchema, type SensingEvent, type Status } from "./contracts";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number | null = null,
    public retryAfter: number | null = null,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export const STREAM_CONTRACT_CLOSE = 4002;
export const isClientCloseCode = (code: number) =>
  code === 1000 || (code >= 3000 && code <= 4999);
export function streamCloseOutcome(code: number) {
  if (code === STREAM_CONTRACT_CLOSE)
    return { label: "Dados incompatíveis", reconnect: false };
  if (code === 1008) return { label: "Acesso recusado", reconnect: false };
  return { label: "Reconectando", reconnect: true };
}

export function statusMessage(status: number, retryAfter: string | null) {
  if (status === 401)
    return "Token inválido. Confira o SPATIAL_TOKEN do arquivo .env.";
  if (status === 409)
    return "A operação conflita com o estado atual. Atualize e tente novamente.";
  if (status === 422)
    return "Confira os parâmetros informados e seus limites antes de tentar novamente.";
  if (status === 429)
    return `Limite de solicitações atingido.${retryAfter && /^\d{1,6}$/.test(retryAfter) ? ` Tente novamente em ${retryAfter} s.` : " Aguarde antes de tentar novamente."}`;
  if (status === 503)
    return "Serviço indisponível temporariamente. Aguarde e tente novamente.";
  return `A API respondeu com erro ${status}. Verifique o backend.`;
}

export function dismissResolved(current: string, resolved: string) {
  return current === resolved ? "" : current;
}

export function controlBody(action: string, provider: string, config: unknown) {
  if (action !== "start") return undefined;
  return provider === "RUVIEW_STREAM"
    ? "{}"
    : JSON.stringify(configSchema.parse(config));
}

export function mergeStatus(current: Status | null, incoming: Status): Status {
  const latest = current?.latest;
  if (
    latest &&
    incoming.latest &&
    latest.source_id === incoming.latest.source_id &&
    Date.parse(latest.timestamp) > Date.parse(incoming.latest.timestamp)
  ) {
    return { ...incoming, latest };
  }
  return incoming;
}

export function mergeHistory(
  current: SensingEvent[],
  incoming: SensingEvent[],
) {
  if (!incoming.length) return [];
  const floor = Math.min(
    ...incoming.map((event) => Date.parse(event.timestamp)),
  );
  const merged = new Map(incoming.map((event) => [event.event_id, event]));
  for (const event of current) {
    if (Date.parse(event.timestamp) >= floor && !merged.has(event.event_id))
      merged.set(event.event_id, event);
  }
  return [...merged.values()]
    .sort((a, b) => Date.parse(b.timestamp) - Date.parse(a.timestamp))
    .slice(0, 20);
}

// Public endpoint only. The bearer token is entered by the operator and kept in memory.
export const apiBase =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
async function responseFor(
  path: string,
  token: string,
  init?: RequestInit,
): Promise<Response> {
  let response: Response;
  try {
    response = await fetch(`${apiBase}/api/v1${path}`, {
      ...init,
      cache: "no-store",
      signal: AbortSignal.timeout(8000),
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
  } catch {
    throw new ApiError(
      "Não foi possível acessar a API. Confira se o backend está em execução e tente novamente.",
    );
  }
  if (!response.ok) {
    const retry = response.headers.get("Retry-After");
    throw new ApiError(
      statusMessage(response.status, retry),
      response.status,
      retry && /^\d{1,6}$/.test(retry) ? Number(retry) : null,
    );
  }
  return response;
}

export async function requestText(
  path: string,
  token: string,
): Promise<string> {
  const response = await responseFor(path, token);
  try {
    return await response.text();
  } catch {
    throw new ApiError("A API respondeu com conteúdo ilegível.");
  }
}

export async function request<T>(
  path: string,
  token: string,
  schema: z.ZodType<T>,
  init?: RequestInit,
): Promise<T> {
  const response = await responseFor(path, token, init);
  let body: unknown;
  try {
    body = await response.json();
  } catch {
    throw new ApiError("A API respondeu com conteúdo ilegível.");
  }
  const parsed = schema.safeParse(body);
  if (!parsed.success)
    throw new ApiError(
      "A API respondeu com dados incompatíveis com o contrato sintético.",
    );
  return parsed.data;
}
