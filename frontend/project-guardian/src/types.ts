export enum Classification {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
}

export interface Assessment {
  classification: Classification;
  reason: string;
  nextSteps: string[];
}
