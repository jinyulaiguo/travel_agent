export const ConfidenceLevel = {
  L1: "L1",
  L2: "L2",
  L3: "L3",
  L4: "L4",
  L5: "L5",
} as const;

export type ConfidenceLevelType = typeof ConfidenceLevel[keyof typeof ConfidenceLevel];

export interface ConfidenceWrapper<T> {
  value: T;
  confidence_level: ConfidenceLevelType;
  snapshot_time?: string;
  note?: string;
}
