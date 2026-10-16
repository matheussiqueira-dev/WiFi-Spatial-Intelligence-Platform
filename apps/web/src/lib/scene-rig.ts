// Original procedural illustration. These joints are never measured or inferred.
export type Point3 = readonly [number, number, number];
export type AvatarKind = "human" | "dog" | "cat";
export type Cast = AvatarKind | "mixed";
export type Rig = {
  points: Point3[];
  edges: readonly (readonly [number, number])[];
};

export function avatarKind(cast: Cast, index: number): AvatarKind {
  if (cast !== "mixed") return cast;
  return (["human", "dog", "cat"] as const)[index % 3];
}

export function project([x, y, z]: Point3): readonly [number, number] {
  return [280 + x * 60 - y * 36, 80 + x * 25 + y * 30 - z * 60];
}

export function buildRig(kind: AvatarKind, phase: number): Rig {
  const stride = Math.sin(phase) * 0.16;
  if (kind === "human") {
    // Face (5), shoulders/elbows/wrists (6), hips/knees/ankles (6).
    return {
      points: [
        [0, 0, 1.68],
        [-0.055, 0, 1.72],
        [0.055, 0, 1.72],
        [-0.11, 0, 1.68],
        [0.11, 0, 1.68],
        [-0.22, 0, 1.43],
        [0.22, 0, 1.43],
        [-0.29, stride, 1.13],
        [0.29, -stride, 1.13],
        [-0.25, stride * 1.5, 0.88],
        [0.25, -stride * 1.5, 0.88],
        [-0.13, 0, 0.88],
        [0.13, 0, 0.88],
        [-0.14, -stride, 0.45],
        [0.14, stride, 0.45],
        [-0.15, -stride * 1.7, 0.04],
        [0.15, stride * 1.7, 0.04],
      ],
      edges: [
        [0, 1],
        [0, 2],
        [1, 3],
        [2, 4],
        [5, 6],
        [5, 7],
        [7, 9],
        [6, 8],
        [8, 10],
        [5, 11],
        [6, 12],
        [11, 12],
        [11, 13],
        [13, 15],
        [12, 14],
        [14, 16],
      ],
    };
  }
  const scale = kind === "cat" ? 0.7 : 1;
  const points: Point3[] = [
    [0.46, 0, 0.7],
    [0.62, 0, 0.64],
    [0.28, 0, 0.55],
    [-0.32, 0, 0.5],
    [0.28, -0.13, 0.5],
    [0.27 + stride, -0.13, 0.25],
    [0.29 + stride, -0.13, 0.03],
    [0.28, 0.13, 0.5],
    [0.27 - stride, 0.13, 0.25],
    [0.29 - stride, 0.13, 0.03],
    [-0.32, -0.13, 0.48],
    [-0.35 - stride, -0.13, 0.23],
    [-0.36 - stride, -0.13, 0.03],
    [-0.32, 0.13, 0.48],
    [-0.35 + stride, 0.13, 0.23],
    [-0.36 + stride, 0.13, 0.03],
    [-0.58, 0, kind === "cat" ? 0.95 : 0.62],
    [-0.73, 0, kind === "cat" ? 1.05 : 0.72],
    [0.4, -0.1, kind === "cat" ? 0.94 : 0.83],
    [0.4, 0.1, kind === "cat" ? 0.94 : 0.83],
  ];
  return {
    points: points.map(([x, y, z]) => [x * scale, y * scale, z * scale]),
    edges: [
      [0, 1],
      [0, 2],
      [2, 3],
      [2, 4],
      [4, 5],
      [5, 6],
      [2, 7],
      [7, 8],
      [8, 9],
      [3, 10],
      [10, 11],
      [11, 12],
      [3, 13],
      [13, 14],
      [14, 15],
      [3, 16],
      [16, 17],
      [0, 18],
      [0, 19],
    ],
  };
}
