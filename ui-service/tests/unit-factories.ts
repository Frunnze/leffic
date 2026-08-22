import fc from "fast-check";
import {
  UNIT_TYPES,
  type Unit,
  type UnitType,
} from "../src/features/folder/unit-models";

export const unitType: fc.Arbitrary<UnitType> = fc.constantFrom(...UNIT_TYPES);

export const unit: fc.Arbitrary<Unit> = fc.record({
  id: fc.uuid(),
  name: fc.string(),
  type: unitType,
  createdAt: fc
    .date({
      min: new Date("2020-01-01"),
      max: new Date("2030-01-01"),
      noInvalidDate: true,
    })
    .map((moment) => moment.toISOString()),
  extension: fc.option(fc.constantFrom("pdf", "docx"), { nil: null }),
  dueCount: fc.option(fc.integer({ min: 0, max: 99 }), { nil: null }),
  meta: fc.option(fc.string(), { nil: null }),
});

export function unitOf(overrides: Partial<Unit>): Unit {
  return {
    id: "unit-id",
    name: "Unit",
    type: "note",
    createdAt: "2024-01-01T00:00:00.000Z",
    extension: null,
    dueCount: null,
    meta: null,
    ...overrides,
  };
}
