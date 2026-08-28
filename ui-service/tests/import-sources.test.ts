import { describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import { ImportSources } from "../src/features/folder/import/import-sources";
import { ImportOptions } from "../src/features/folder/import/import-options";
import { importRequest, pdfFile, sourceKind } from "./import-factories";

const UPLOADED = {
  fileId: "7",
  name: "notes.pdf",
  extension: "pdf",
  createdAt: "now",
};

describe("ImportSources.originOf", () => {
  it("originOf property always names the kind the request carried", () => {
    fc.assert(
      fc.property(sourceKind, (kind) => {
        expect(ImportSources.originOf(importRequest({ kind })).kind).toBe(kind);
      }),
    );
  });

  it.each([
    [importRequest({ kind: "file", file: pdfFile("a.pdf") }), "a.pdf"],
    [importRequest({ kind: "file" }), ""],
    [importRequest({ kind: "link", link: "https://x.test" }), "https://x.test"],
    [importRequest({ kind: "topic", topic: "cells" }), "cells"],
    [importRequest({ kind: "text", text: "words" }), ""],
  ])("refers to the source it came from", (request, reference) => {
    expect(ImportSources.originOf(request).reference).toBe(reference);
  });
});

describe("ImportSources.labelFor", () => {
  it("labelFor property calls a link by its address", () => {
    fc.assert(
      fc.property(fc.string({ minLength: 1 }), (link) => {
        expect(
          ImportSources.labelFor(importRequest({ kind: "link", link })),
        ).toBe(link);
      }),
    );
  });

  it("labelFor property calls a topic by its name", () => {
    fc.assert(
      fc.property(fc.string({ minLength: 1 }), (topic) => {
        expect(
          ImportSources.labelFor(importRequest({ kind: "topic", topic })),
        ).toBe(topic);
      }),
    );
  });

  it("calls a chosen file by its filename", () => {
    const request = importRequest({ kind: "file", file: pdfFile("b.pdf") });

    expect(ImportSources.labelFor(request)).toBe("b.pdf");
  });

  it("calls an unchosen file just a file", () => {
    expect(ImportSources.labelFor(importRequest({ kind: "file" }))).toBe(
      "your file",
    );
  });

  it("calls pasted text what it is", () => {
    expect(ImportSources.labelFor(importRequest({ kind: "text" }))).toBe(
      "your text",
    );
  });
});

describe("ImportSources.wishFrom", () => {
  it("wishFrom property asks for a note exactly when one was chosen", () => {
    fc.assert(
      fc.property(fc.boolean(), (wantsNote) => {
        const request = importRequest({
          note: wantsNote
            ? ImportOptions.startingChoice("note")
            : ImportOptions.emptyChoice(),
        });

        expect(ImportSources.wishFrom(request).note).toBe(wantsNote);
      }),
    );
  });

  it("asks for nothing when nothing was chosen", () => {
    expect(ImportSources.wishFrom(importRequest())).toEqual({
      flashcardTypes: [],
      flashcardAmount: null,
      testTypes: [],
      testAmount: undefined,
      note: false,
    });
  });

  it("asks for the chosen flashcard and test types", () => {
    const request = importRequest({
      flashcards: ImportOptions.withCount(
        ImportOptions.startingChoice("cloze"),
        "cloze",
        4,
      ),
      test: ImportOptions.startingChoice("true_or_false"),
    });

    expect(ImportSources.wishFrom(request)).toMatchObject({
      flashcardTypes: ["cloze"],
      flashcardAmount: 4,
      testTypes: ["true_or_false"],
      testAmount: null,
    });
  });
});

describe("ImportSources.sourceFrom", () => {
  it("sourceFrom property turns a link into a link source", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string({ minLength: 1 }), async (link) => {
        const upload = vi.fn();

        await expect(
          ImportSources.sourceFrom(
            importRequest({ kind: "link", link }),
            upload,
          ),
        ).resolves.toEqual({ kind: "link", url: link });
        expect(upload).not.toHaveBeenCalled();
      }),
    );
  });

  it("sourceFrom property treats pasted text as a topic of its own", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string({ minLength: 1 }), async (text) => {
        await expect(
          ImportSources.sourceFrom(
            importRequest({ kind: "text", text }),
            vi.fn(),
          ),
        ).resolves.toEqual({ kind: "topic", topic: text });
      }),
    );
  });

  it("turns a topic into a topic source", async () => {
    await expect(
      ImportSources.sourceFrom(
        importRequest({ kind: "topic", topic: "cells" }),
        vi.fn(),
      ),
    ).resolves.toEqual({ kind: "topic", topic: "cells" });
  });

  it("uploads a chosen file and points at what came back", async () => {
    const upload = vi.fn().mockResolvedValue([UPLOADED]);
    const request = importRequest({
      kind: "file",
      file: pdfFile(),
      firstPage: 1,
      lastPage: 3,
    });

    await expect(ImportSources.sourceFrom(request, upload)).resolves.toEqual({
      kind: "file",
      fileId: "7",
      firstPage: 1,
      lastPage: 3,
    });
  });

  it("builds a file source that carries no extension", async () => {
    const upload = vi.fn().mockResolvedValue([UPLOADED]);
    const request = importRequest({ kind: "file", file: pdfFile() });

    const source = await ImportSources.sourceFrom(request, upload);

    expect(source).not.toHaveProperty("extension");
  });

  it("points nowhere when no file was chosen", async () => {
    const upload = vi.fn();

    await expect(
      ImportSources.sourceFrom(importRequest({ kind: "file" }), upload),
    ).resolves.toBeNull();
    expect(upload).not.toHaveBeenCalled();
  });

  it("points nowhere when the upload stored nothing", async () => {
    const upload = vi.fn().mockResolvedValue([]);
    const request = importRequest({ kind: "file", file: pdfFile() });

    await expect(ImportSources.sourceFrom(request, upload)).resolves.toBeNull();
  });
});
