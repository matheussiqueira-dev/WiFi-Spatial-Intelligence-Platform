import type { SimulationConfig } from "./contracts";

export const scenarioLabels: Record<SimulationConfig["scenario"], string> = {
  empty: "Sala vazia",
  stationary: "Presença estacionária",
  walking: "Movimento",
  entering: "Entrada gradual",
  leaving: "Saída gradual",
  interference: "Perturbação sintética",
  packet_loss: "Perda de pacotes",
  disconnect: "Desconexão virtual",
};

/** Historical provenance values, including the opt-in legacy laboratory. */
export const historicalScenarios: Record<string, string> = {
  ...scenarioLabels,
  "ruview-simulated": "RuView simulado (laboratório legado)",
};

export function scenarioLabel(scenario: string) {
  return historicalScenarios[scenario] ?? scenario;
}
