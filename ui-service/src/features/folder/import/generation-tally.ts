import type { GeneratedKind } from "./generation-api";
import type { Unit } from "../../../shared/models/units";

export type GenerationOutcome = {
  readonly kind: GeneratedKind;
  readonly succeeded: boolean;
  readonly units: readonly Unit[];
};

export class GenerationTally {
  private readonly kind: GeneratedKind;
  private readonly report: (outcome: GenerationOutcome) => void;
  private awaited: number;
  private succeeded = true;
  private readonly units: Unit[] = [];

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
    this.units.push(...outcome.units);

    if (this.awaited > 0) return;

    this.report({
      kind: this.kind,
      succeeded: this.succeeded,
      units: this.units,
    });
  }
}
