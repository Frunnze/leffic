import type { GeneratedKind } from "./generation-api";
import type { Unit } from "../unit-models";

export type GenerationOutcome = {
  readonly kind: GeneratedKind;
  readonly succeeded: boolean;
  readonly unit: Unit | null;
};

export class GenerationTally {
  private readonly kind: GeneratedKind;
  private readonly report: (outcome: GenerationOutcome) => void;
  private awaited: number;
  private succeeded = true;
  private unit: Unit | null = null;

  constructor(
    kind: GeneratedKind,
    jobCount: number,
    report: (outcome: GenerationOutcome) => void,
  ) {
    this.kind = kind;
    this.awaited = jobCount;
    this.report = report;
  }

  record(outcome: GenerationOutcome): void {
    this.awaited -= 1;

    if (!outcome.succeeded) this.succeeded = false;
    if (outcome.unit !== null) this.unit = outcome.unit;

    if (this.awaited > 0) return;

    this.report({
      kind: this.kind,
      succeeded: this.succeeded,
      unit: this.unit,
    });
  }
}
