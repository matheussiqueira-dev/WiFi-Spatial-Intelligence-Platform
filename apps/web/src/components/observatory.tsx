"use client";

import { useId, useRef, useState, useSyncExternalStore } from "react";
import type { Sensor, SensingEvent } from "../lib/contracts";
import type { Cast } from "../lib/scene-rig";
import ArticulatedScene from "./articulated-scene";

function subscribeMotion(onChange: () => void) {
  const media = window.matchMedia("(prefers-reduced-motion: reduce)");
  media.addEventListener("change", onChange);
  return () => media.removeEventListener("change", onChange);
}
const reducedMotion = () =>
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export default function Observatory({
  event,
  sensors,
  connected,
}: {
  event: SensingEvent | null;
  sensors: Sensor[];
  connected: boolean;
}) {
  const id = useId();
  const [view, setView] = useState("structure");
  const [cast, setCast] = useState<Cast>("human");
  const [articulate, setArticulate] = useState(true);
  const [volume, setVolume] = useState(true);
  const [expandError, setExpandError] = useState("");
  const viewer = useRef<HTMLDivElement>(null);
  async function expandScene() {
    try {
      setExpandError("");
      if (document.fullscreenElement === viewer.current)
        await document.exitFullscreen();
      else await viewer.current?.requestFullscreen();
    } catch {
      setExpandError(
        "Seu navegador não permitiu tela cheia. A cena continua disponível abaixo.",
      );
    }
  }
  const reduce = useSyncExternalStore(
    subscribeMotion,
    reducedMotion,
    () => true,
  );
  return (
    <div className="scene-viewer" ref={viewer}>
      <div className="scene-toolbar">
        <div className="scene-control">
          <label htmlFor={`${id}-view`}>Visualização</label>
          <select
            id={`${id}-view`}
            value={view}
            onChange={(e) => setView(e.target.value)}
          >
            <option value="structure">Estruturas articuladas</option>
            <option value="plan">Planta 2D</option>
          </select>
        </div>
        <div className="scene-control">
          <label htmlFor={`${id}-cast`}>Avatares da cena</label>
          <select
            id={`${id}-cast`}
            value={cast}
            disabled={view === "plan" || event?.source_id === "ruview-01"}
            onChange={(e) => setCast(e.target.value as Cast)}
          >
            <option value="human">Pessoas</option>
            <option value="dog">Cães</option>
            <option value="cat">Gatos</option>
            <option value="mixed">Pessoas e pets</option>
          </select>
        </div>
        <label className="scene-motion" htmlFor={`${id}-motion`}>
          <input
            id={`${id}-motion`}
            type="checkbox"
            checked={articulate && !reduce}
            disabled={reduce || view === "plan"}
            onChange={(e) => setArticulate(e.target.checked)}
          />
          Articular avatares
        </label>
        <label className="scene-motion" htmlFor={`${id}-volume`}>
          <input
            id={`${id}-volume`}
            type="checkbox"
            checked={volume}
            disabled={view === "plan"}
            onChange={(e) => setVolume(e.target.checked)}
          />
          Volume dos corpos
        </label>
        <button
          type="button"
          className="secondary scene-expand"
          onClick={() => void expandScene()}
        >
          Ampliar / reduzir cena
        </button>
      </div>
      {expandError && (
        <p role="alert" className="scene-explanation">
          {expandError}
        </p>
      )}
      {view === "structure" ? (
        <ArticulatedScene
          event={event}
          sensors={sensors}
          connected={connected}
          cast={cast}
          articulate={articulate && !reduce}
          gridId={`${id}-scene`}
          volume={volume}
        />
      ) : (
        <svg
          viewBox="-0.8 -0.75 9.6 7.5"
          role="img"
          aria-label={
            event?.source_id === "ruview-01"
              ? `RuView simulado, presença ${event.measurements.presence_detected ? "detectada" : "ausente"}, ${event.measurements.occupancy_estimate === null ? "contagem indisponível" : `${event.measurements.occupancy_estimate} ocupantes estimados em sinais sintéticos`}, posições indisponíveis`
              : `Laboratório virtual de 8 por 6 metros, ${sensors.length} sensores virtuais, ${event ? `${event.measurements.occupancy_estimate} ocupantes sintéticos` : "sem observação"}`
          }
          className="observatory"
        >
          <defs>
            <pattern
              id={`${id}-grid`}
              width="1"
              height="1"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 1 0 L 0 0 0 1"
                fill="none"
                stroke="#d4e1ed"
                strokeWidth=".018"
              />
            </pattern>
          </defs>
          <rect
            width="8"
            height="6"
            rx=".08"
            fill="#f0f6fb"
            stroke="#9db3c8"
            strokeWidth=".025"
          />
          <rect width="8" height="6" fill={`url(#${id}-grid)`} />
          <text x="4" y="-.38" textAnchor="middle" className="map-label">
            8 m
          </text>
          <text x="8.5" y="3" textAnchor="middle" className="map-label">
            6 m
          </text>
          {sensors.map((sensor, i) => (
            <g
              key={sensor.id}
              data-testid="virtual-sensor"
              transform={`translate(${sensor.position_m[0]} ${sensor.position_m[1]})`}
            >
              <title>
                {sensor.id} — sensor virtual{" "}
                {connected ? "conectado" : "desconectado"}
              </title>
              <circle
                r=".26"
                fill={connected ? "#e1f0fc" : "#e7ebef"}
                stroke={connected ? "#2178b5" : "#75899b"}
                strokeWidth=".025"
              />
              <rect
                x="-.07"
                y="-.07"
                width=".14"
                height=".14"
                rx=".02"
                fill={connected ? "#2178b5" : "#75899b"}
              />
              <text
                y={sensor.position_m[1] === 0 ? ".55" : "-.4"}
                textAnchor="middle"
                className="map-label"
              >
                V{i + 1}
              </text>
            </g>
          ))}
          {event?.measurements.ground_truth_positions.map(([x, y], i) => (
            <g
              data-testid="occupant"
              key={i}
              transform={`translate(${x} ${y})`}
            >
              <title>
                Ocupante sintético {i + 1}: {x} m, {y} m
              </title>
              <circle r=".3" fill="#d6ece5" />
              <circle r=".11" fill="#127864" />
              <text y=".55" textAnchor="middle" className="map-label">
                P{i + 1}
              </text>
            </g>
          ))}
        </svg>
      )}
      <p className="scene-explanation">
        <strong>Pose procedural.</strong> A aparência escolhida não altera os
        dados de ocupação. Pessoas e animais são avatares ilustrativos; espécies
        e articulações não são reconhecidas por Wi-Fi.
        {reduce &&
          " Articulação desativada pela preferência de movimento reduzido."}
      </p>
    </div>
  );
}
