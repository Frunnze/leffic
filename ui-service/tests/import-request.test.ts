import { describe, expect, it } from "vitest";
import fc from "fast-check";
import {
  ImportRequestReading,
} from "../src/features/folder/import/import-request";
import { ImportOptions } from "../src/features/folder/import/import-options";
import { importRequest, pdfFile, sourceKind } from "./import-factories";

describe("ImportRequestReading.chosenPage", () => {
  it("chosenPage property reads back any whole number written out", () => {
    fc.assert(
      fc.property(fc.integer({ min: -500, max: 500 }), (page) => {
        expect(ImportRequestReading.chosenPage(String(page))).toBe(page);
      }),
    );
  });

  it("chosenPage property reads anything unnumbered as no page", () => {
    fc.assert(
      fc.property(fc.stringMatching(/^[a-z ]*$/), (typed) => {
        expect(ImportRequestReading.chosenPage(typed)).toBeNull();
      }),
    );
  });
});

describe("ImportRequestReading.missingSource", () => {
  it("missingSource property always complains about an empty request", () => {
    fc.assert(
      fc.property(sourceKind, (kind) => {
        expect(
          ImportRequestReading.missingSource(importRequest({ kind })),
        ).toEqual(expect.any(String));
      }),
    );
  });

  it.each([
    [importRequest({ kind: "file", file: pdfFile() })],
    [importRequest({ kind: "link", link: "https://example.test" })],
    [importRequest({ kind: "topic", topic: "mitosis" })],
    [importRequest({ kind: "text", text: "some notes" })],
  ])("stays silent once the source is there", (request) => {
    expect(ImportRequestReading.missingSource(request)).toBeNull();
  });

  it.each([
    ["file", "Choose a file first."],
    ["link", "Paste a link first."],
    ["topic", "Name a topic first."],
    ["text", "Paste some text first."],
  ] as const)("asks for the missing %s", (kind, message) => {
    expect(ImportRequestReading.missingSource(importRequest({ kind }))).toBe(
      message,
    );
  });
});

describe("ImportRequestReading.sourceName", () => {
  it("sourceName property names the link the learner pasted", () => {
    fc.assert(
      fc.property(fc.string({ minLength: 1 }), (link) => {
        expect(
          ImportRequestReading.sourceName(
            importRequest({ kind: "link", link }),
          ),
        ).toBe(link);
      }),
    );
  });

  it("sourceName property names the topic the learner asked for", () => {
    fc.assert(
      fc.property(fc.string({ minLength: 1 }), (topic) => {
        expect(
          ImportRequestReading.sourceName(
            importRequest({ kind: "topic", topic }),
          ),
        ).toBe(topic);
      }),
    );
  });

  it("names the chosen file", () => {
    const request = importRequest({
      kind: "file",
      file: pdfFile("biology.pdf"),
    });

    expect(ImportRequestReading.sourceName(request)).toBe("biology.pdf");
  });

  it("names nothing when no file was chosen", () => {
    expect(
      ImportRequestReading.sourceName(importRequest({ kind: "file" })),
    ).toBe("");
  });

  it("calls pasted text what it is", () => {
    expect(
      ImportRequestReading.sourceName(importRequest({ kind: "text" })),
    ).toBe("your text");
  });
});

describe("ImportRequestReading.nothingChosen", () => {
  it("nothingChosen property is false once any one kind is chosen", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("flashcards", "test", "note" as const),
        (field) => {
          const request = importRequest({
            [field]: ImportOptions.startingChoice("basic"),
          });

          expect(ImportRequestReading.nothingChosen(request)).toBe(false);
        },
      ),
    );
  });

  it("is true when the learner chose nothing to generate", () => {
    expect(ImportRequestReading.nothingChosen(importRequest())).toBe(true);
  });
});
