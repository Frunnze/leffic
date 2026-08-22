import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { UnitPresentation } from "../src/features/folder/unit-presentation";
import { unit, unitOf } from "./unit-factories";

describe("UnitPresentation.moveDestinations", () => {
  it("moveDestinations property always offers Home first", () => {
    fc.assert(
      fc.property(fc.array(unit), unit, (units, moving) => {
        expect(UnitPresentation.moveDestinations(units, moving)[0]).toEqual({
          id: "home",
          name: "Home",
        });
      }),
    );
  });

  it("moveDestinations property never offers a unit its own folder", () => {
    fc.assert(
      fc.property(fc.array(unit), unit, (units, moving) => {
        const destinations = UnitPresentation.moveDestinations(units, moving);

        expect(destinations.map((entry) => entry.id)).not.toContain(moving.id);
      }),
    );
  });

  it("moveDestinations property offers only folders beside Home", () => {
    fc.assert(
      fc.property(fc.array(unit), (units) => {
        const moving = unitOf({ id: "moving", type: "note" });
        const destinations = UnitPresentation.moveDestinations(units, moving);
        const folderIds = units
          .filter((entry) => entry.type === "folder")
          .map((entry) => entry.id);

        expect(destinations.slice(1).map((entry) => entry.id)).toEqual(
          folderIds,
        );
      }),
    );
  });
});

describe("UnitPresentation.icon", () => {
  it("icon property names an icon for every unit", () => {
    fc.assert(
      fc.property(unit, (given) => {
        expect(UnitPresentation.icon(given)).toEqual(expect.any(String));
      }),
    );
  });
});

describe("UnitPresentation.href", () => {
  it("href property always leads somewhere inside the app", () => {
    fc.assert(
      fc.property(unit, (given) => {
        expect(UnitPresentation.href(given).startsWith("/")).toBe(true);
      }),
    );
  });

  it.each([
    [unitOf({ id: "1", type: "folder" }), "/folder/1"],
    [unitOf({ id: "2", type: "file", extension: "pdf" }), "/file/2/pdf"],
    [unitOf({ id: "3", type: "file", extension: null }), "/file/3/"],
    [unitOf({ id: "4", type: "flashcard_deck" }), "/flashcard_deck/4"],
    [unitOf({ id: "5", type: "note" }), "/note/5"],
    [unitOf({ id: "6", type: "test" }), "/test/6"],
  ])("links a %s to its own page", (given, href) => {
    expect(UnitPresentation.href(given)).toBe(href);
  });
});

describe("UnitPresentation.meta", () => {
  it("meta property prefers whatever the unit already says about itself", () => {
    fc.assert(
      fc.property(fc.string({ minLength: 1 }), (meta) => {
        expect(UnitPresentation.meta(unitOf({ meta }))).toBe(meta);
      }),
    );
  });

  it("shows a file's extension in capitals when it says nothing else", () => {
    expect(
      UnitPresentation.meta(unitOf({ type: "file", extension: "pdf" })),
    ).toBe("PDF");
  });

  it("shows nothing for a file with no extension", () => {
    expect(UnitPresentation.meta(unitOf({ type: "file" }))).toBeNull();
  });

  it("shows nothing for a unit that carries no detail", () => {
    expect(UnitPresentation.meta(unitOf({ type: "note" }))).toBeNull();
  });
});

describe("UnitPresentation.badge", () => {
  it("badge property counts everything that is due", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 999 }), (dueCount) => {
        expect(UnitPresentation.badge(unitOf({ dueCount }))).toBe(
          `${dueCount} due`,
        );
      }),
    );
  });

  it("badge property stays silent when nothing is due", () => {
    fc.assert(
      fc.property(fc.integer({ min: -50, max: 0 }), (dueCount) => {
        expect(UnitPresentation.badge(unitOf({ dueCount }))).toBeNull();
      }),
    );
  });

  it("stays silent when the unit does not count due work", () => {
    expect(UnitPresentation.badge(unitOf({ dueCount: null }))).toBeNull();
  });
});

describe("UnitPresentation.countLabel", () => {
  it("countLabel property pluralises everything but one", () => {
    fc.assert(
      fc.property(fc.integer({ min: 2, max: 500 }), (total) => {
        expect(UnitPresentation.countLabel(total)).toBe(`${total} items`);
      }),
    );
  });

  it("counts a single item in the singular", () => {
    expect(UnitPresentation.countLabel(1)).toBe("1 item");
  });
});
