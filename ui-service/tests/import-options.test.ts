import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { ImportOptions } from "../src/features/folder/import/import-options";

const TYPE_ID = fc.constantFrom("basic", "cloze", "list", "feynman");
const COUNT = fc.integer({ min: 1, max: 200 });

describe("ImportOptions.emptyChoice", () => {
  it("emptyChoice property always starts unchosen and uncounted", () => {
    fc.assert(
      fc.property(fc.integer(), () => {
        expect(ImportOptions.emptyChoice()).toEqual({
          isChosen: false,
          counts: {},
          chosenTypes: [],
        });
      }),
    );
  });
});

describe("ImportOptions.startingChoice", () => {
  it("startingChoice property chooses exactly the one type it names", () => {
    fc.assert(
      fc.property(TYPE_ID, (typeId) => {
        expect(ImportOptions.startingChoice(typeId)).toEqual({
          isChosen: true,
          counts: {},
          chosenTypes: [typeId],
        });
      }),
    );
  });
});

describe("ImportOptions.withType", () => {
  it("withType property adds a type that was not chosen yet", () => {
    fc.assert(
      fc.property(TYPE_ID, (typeId) => {
        const chosen = ImportOptions.withType(
          ImportOptions.emptyChoice(),
          typeId,
        );

        expect(chosen.chosenTypes).toEqual([typeId]);
      }),
    );
  });

  it("withType property twice over leaves the choice as it started", () => {
    fc.assert(
      fc.property(TYPE_ID, (typeId) => {
        const once = ImportOptions.withType(
          ImportOptions.emptyChoice(),
          typeId,
        );
        const twice = ImportOptions.withType(once, typeId);

        expect(twice.chosenTypes).toEqual([]);
      }),
    );
  });

  it("withType property never chooses the same type twice", () => {
    fc.assert(
      fc.property(fc.uniqueArray(TYPE_ID, { minLength: 1 }), (typeIds) => {
        let choice = ImportOptions.emptyChoice();

        for (const typeId of typeIds)
          choice = ImportOptions.withType(choice, typeId);

        expect(new Set(choice.chosenTypes).size).toBe(
          choice.chosenTypes.length,
        );
      }),
    );
  });
});

describe("ImportOptions.withCount", () => {
  it("withCount property remembers the count against its type", () => {
    fc.assert(
      fc.property(TYPE_ID, COUNT, (typeId, count) => {
        const counted = ImportOptions.withCount(
          ImportOptions.startingChoice(typeId),
          typeId,
          count,
        );

        expect(counted.counts[typeId]).toBe(count);
      }),
    );
  });

  it("withCount property leaves the chosen types alone", () => {
    fc.assert(
      fc.property(TYPE_ID, COUNT, (typeId, count) => {
        const started = ImportOptions.startingChoice(typeId);
        const counted = ImportOptions.withCount(started, typeId, count);

        expect(counted.chosenTypes).toEqual(started.chosenTypes);
      }),
    );
  });
});

describe("ImportOptions.totalCount", () => {
  it("totalCount property adds up every counted type", () => {
    fc.assert(
      fc.property(
        fc.uniqueArray(TYPE_ID, { minLength: 1 }),
        COUNT,
        (typeIds, count) => {
          let choice = ImportOptions.emptyChoice();

          for (const typeId of typeIds) {
            choice = ImportOptions.withCount(
              ImportOptions.withType(choice, typeId),
              typeId,
              count,
            );
          }

          expect(ImportOptions.totalCount(choice)).toBe(count * typeIds.length);
        },
      ),
    );
  });

  it("counts nothing when no type carries a count", () => {
    expect(
      ImportOptions.totalCount(ImportOptions.startingChoice("basic")),
    ).toBeNull();
  });

  it("ignores a count for a type that is no longer chosen", () => {
    const counted = ImportOptions.withCount(
      ImportOptions.emptyChoice(),
      "basic",
      10,
    );

    expect(ImportOptions.totalCount(counted)).toBeNull();
  });

  it("skips a type whose count was cleared", () => {
    const chosen = ImportOptions.withType(ImportOptions.emptyChoice(), "basic");
    const cleared = ImportOptions.withCount(chosen, "basic", null);

    expect(ImportOptions.totalCount(cleared)).toBeNull();
  });
});
