import type { Sensor, SensingEvent } from "../lib/contracts";
import {
  avatarKind,
  buildRig,
  project,
  type Cast,
  type Point3,
} from "../lib/scene-rig";

const colors = { human: "#64e5c3", dog: "#ffbf76", cat: "#b6b0ff" };
const names = { human: "Pessoa", dog: "Cão", cat: "Gato" };
const coordinates = (points: Point3[]) =>
  points.map((point) => project(point).join(",")).join(" ");

export default function ArticulatedScene({
  event,
  sensors,
  connected,
  cast,
  articulate,
  gridId,
  volume = true,
}: {
  event: SensingEvent | null;
  sensors: Sensor[];
  connected: boolean;
  cast: Cast;
  articulate: boolean;
  gridId: string;
  volume?: boolean;
}) {
  const positions =
    event?.source_id === "ruview-01"
      ? []
      : (event?.measurements.ground_truth_positions ?? []);
  const actors = positions
    .map(([x, y], index) => ({ x, y, index }))
    .sort((a, b) => a.x + a.y - b.x - b.y);
  const moving =
    event &&
    ["walking", "entering", "leaving"].includes(event.provenance.scenario);
  const ground: Point3[] = [
    [0, 0, 0],
    [8, 0, 0],
    [8, 6, 0],
    [0, 6, 0],
  ];
  return (
    <svg
      viewBox="0 -75 840 640"
      role="img"
      className="observatory articulated-scene"
      aria-label={
        event?.source_id === "ruview-01"
          ? `RuView simulado, ${event.measurements.occupancy_estimate === null ? "contagem indisponível" : `${event.measurements.occupancy_estimate} ocupantes estimados em sinais sintéticos`}, posições indisponíveis`
          : `Cena articulada sintética, ${event ? `${positions.length} ocupantes sintéticos` : "sem observação"}, ${sensors.length} sensores virtuais. Avatares escolhidos pelo operador; sem reconhecimento de espécies ou pose por RF.`
      }
    >
      <defs>
        <filter
          id={`${gridId}-glow`}
          x="-70%"
          y="-70%"
          width="240%"
          height="240%"
        >
          <feGaussianBlur stdDeviation="3" />
        </filter>
        <linearGradient id={gridId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#142d40" />
          <stop offset="1" stopColor="#0c1d2c" />
        </linearGradient>
      </defs>
      <rect x="0" y="-75" width="840" height="640" rx="18" fill="#081623" />
      <text x="32" y="-36" className="scene-eyebrow">
        CENA VIRTUAL / L0_SYNTHETIC
      </text>
      <text x="808" y="-36" textAnchor="end" className="scene-subtitle">
        POSE PROCEDURAL
      </text>
      <polygon
        points={coordinates([
          [0, 0, 0],
          [8, 0, 0],
          [8, 0, 1.8],
          [0, 0, 1.8],
        ])}
        fill="#173449"
        opacity=".3"
      />
      <polygon
        points={coordinates([
          [0, 0, 0],
          [0, 6, 0],
          [0, 6, 1.8],
          [0, 0, 1.8],
        ])}
        fill="#214354"
        opacity=".2"
      />
      <polygon
        points={coordinates(ground)}
        fill={`url(#${gridId})`}
        stroke="#426979"
        strokeWidth="1.5"
      />
      {Array.from({ length: 9 }, (_, x) => (
        <polyline
          key={`x${x}`}
          points={coordinates([
            [x, 0, 0],
            [x, 6, 0],
          ])}
          fill="none"
          stroke="#294b5e"
          strokeWidth="1"
        />
      ))}
      {Array.from({ length: 7 }, (_, y) => (
        <polyline
          key={`y${y}`}
          points={coordinates([
            [0, y, 0],
            [8, y, 0],
          ])}
          fill="none"
          stroke="#294b5e"
          strokeWidth="1"
        />
      ))}
      {sensors.map((sensor, i) => {
        const [x, y] = project([sensor.position_m[0], sensor.position_m[1], 0]);
        return (
          <g
            key={sensor.id}
            data-testid="virtual-sensor"
            transform={`translate(${x} ${y})`}
          >
            <title>
              {sensor.id} — sensor virtual{" "}
              {connected ? "conectado" : "desconectado"}
            </title>
            <ellipse
              rx="16"
              ry="8"
              fill="#16394c"
              stroke={connected ? "#57bcf5" : "#7a94a5"}
            />
            <path
              d="M-5 -5 L0 -10 L5 -5 L0 0 Z"
              fill={connected ? "#57bcf5" : "#7a94a5"}
            />
            <text y="24" textAnchor="middle" className="scene-label">
              V{i + 1}
            </text>
          </g>
        );
      })}
      {actors.map(({ x, y, index }) => {
        const kind = avatarKind(cast, index);
        const rig = buildRig(
          kind,
          articulate && moving ? event.provenance.tick * 0.55 + index : 0,
        );
        const points = rig.points.map(([dx, dy, z]) =>
          project([x + dx, y + dy, z]),
        );
        const [baseX, baseY] = project([x, y, 0]);
        return (
          <g data-testid="occupant" data-avatar={kind} key={index}>
            <title>{`${names[kind]} ilustrativo ${index + 1}, ocupante sintético em ${x.toFixed(2)} m, ${y.toFixed(2)} m. Aparência selecionada, não inferida.`}</title>
            <ellipse
              cx={baseX}
              cy={baseY}
              rx={kind === "human" ? 19 : 26}
              ry="9"
              fill={colors[kind]}
              opacity=".12"
            />
            {volume && (
              <g data-testid="avatar-volume" aria-hidden="true">
                <g filter={`url(#${gridId}-glow)`} opacity=".35">
                  {rig.edges
                    .slice(kind === "human" ? 4 : 0)
                    .map(([from, to]) => (
                      <line
                        key={`${from}-${to}`}
                        x1={points[from][0]}
                        y1={points[from][1]}
                        x2={points[to][0]}
                        y2={points[to][1]}
                        stroke={colors[kind]}
                        strokeWidth={kind === "human" ? 16 : 12}
                        strokeLinecap="round"
                      />
                    ))}
                </g>
                {kind === "human" ? (
                  <>
                    <polygon
                      points={[5, 6, 12, 11]
                        .map((joint) => points[joint].join(","))
                        .join(" ")}
                      fill={colors[kind]}
                      opacity=".25"
                    />
                    <ellipse
                      cx={points[0][0]}
                      cy={points[0][1] - 2}
                      rx="11"
                      ry="14"
                      fill={colors[kind]}
                      opacity=".45"
                    />
                  </>
                ) : (
                  <>
                    <line
                      x1={points[2][0]}
                      y1={points[2][1]}
                      x2={points[3][0]}
                      y2={points[3][1]}
                      stroke={colors[kind]}
                      strokeWidth={kind === "cat" ? 14 : 19}
                      strokeLinecap="round"
                      opacity=".4"
                    />
                    <ellipse
                      cx={points[0][0]}
                      cy={points[0][1]}
                      rx={kind === "cat" ? 7 : 10}
                      ry={kind === "cat" ? 6 : 8}
                      fill={colors[kind]}
                      opacity=".5"
                    />
                  </>
                )}
                {rig.edges.slice(4).map(([from, to]) => (
                  <line
                    key={`${from}-${to}`}
                    x1={points[from][0]}
                    y1={points[from][1]}
                    x2={points[to][0]}
                    y2={points[to][1]}
                    stroke={colors[kind]}
                    strokeWidth={kind === "human" ? 9 : 6}
                    strokeLinecap="round"
                    opacity=".22"
                  />
                ))}
              </g>
            )}
            {rig.edges.map(([from, to]) => (
              <line
                key={`${from}-${to}`}
                x1={points[from][0]}
                y1={points[from][1]}
                x2={points[to][0]}
                y2={points[to][1]}
                stroke={colors[kind]}
                strokeWidth="3"
                strokeLinecap="round"
              />
            ))}
            {points.map(([cx, cy], joint) => (
              <circle
                data-joint={joint}
                key={joint}
                cx={cx}
                cy={cy}
                r={joint === 0 ? 4.5 : 2.8}
                fill="#0d2232"
                stroke={colors[kind]}
                strokeWidth="1.6"
              />
            ))}
            <text
              x={baseX}
              y={baseY + 24}
              textAnchor="middle"
              className="scene-label"
            >
              {names[kind]} {index + 1}
            </text>
          </g>
        );
      })}
      <text x="405" y="505" textAnchor="middle" className="scene-label">
        8 × 6 m · grade de 1 m · perspectiva ilustrativa
      </text>
      {!event && (
        <text x="420" y="540" textAnchor="middle" className="scene-label">
          Aguardando observação sintética
        </text>
      )}
      {event && !positions.length && (
        <text x="420" y="540" textAnchor="middle" className="scene-label">
          {event.source_id === "ruview-01"
            ? "Sem posições compatíveis para desenhar avatares"
            : "Cena sem ocupantes"}
        </text>
      )}
    </svg>
  );
}
