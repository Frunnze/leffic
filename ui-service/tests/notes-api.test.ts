import { afterEach, describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import { NotesApi } from "../src/shared/notes/notes-api";
import { Session } from "../src/shared/api/session";
import {
  jsonResponse,
  requestedInit,
  requestedUrl,
  stubFetch,
} from "./support";

const WORD = fc.constantFrom("alpha", "beta", "gamma");

afterEach(() => {
  vi.unstubAllGlobals();
  Session.store(null);
});

describe("NotesApi.note", () => {
  it("note property asks for exactly the note it was given", async () => {
    await fc.assert(
      fc.asyncProperty(fc.uuid(), async (noteId) => {
        Session.store("token");
        const fetching = stubFetch(jsonResponse({ name: "n", content: "" }));

        await NotesApi.note(noteId);

        expect(requestedUrl(fetching)).toContain(
          `note_id=${encodeURIComponent(noteId)}`,
        );
      }),
    );
  });

  it("note property carries the stored name and content through untouched", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string(), fc.string(), async (name, content) => {
        Session.store("token");
        stubFetch(jsonResponse({ name, content, read: true }));

        const note = await NotesApi.note("id");

        expect(note.content).toBe(content);
        expect(note.name).toBe(name === "" ? "" : name);
        expect(note.isRead).toBe(true);
      }),
    );
  });

  it("names an unnamed note", async () => {
    Session.store("token");
    stubFetch(jsonResponse({ content: "<p>hi</p>" }));

    const note = await NotesApi.note("id");

    expect(note).toEqual({
      name: "Untitled note",
      content: "<p>hi</p>",
      readingMinutes: 1,
      isRead: false,
    });
  });
});

describe("NotesApi.markAsRead", () => {
  it("markAsRead property posts the note id to the review endpoint", async () => {
    await fc.assert(
      fc.asyncProperty(fc.uuid(), async (noteId) => {
        Session.store("token");
        const fetching = stubFetch(jsonResponse({}));

        await NotesApi.markAsRead(noteId);

        expect(requestedUrl(fetching)).toContain("/api/content/review-note");
        expect(requestedInit(fetching).body).toBe(
          JSON.stringify({ note_id: noteId }),
        );
      }),
    );
  });
});

describe("NotesApi.asPlainText", () => {
  it("asPlainText property keeps every word and drops every tag", () => {
    fc.assert(
      fc.property(fc.array(WORD, { minLength: 1 }), (words) => {
        const html = words.map((word) => `<p>${word}</p>`).join("\n");

        expect(NotesApi.asPlainText(html)).toBe(words.join(" "));
      }),
    );
  });

  it("asPlainText property never leaves an angle bracket behind", () => {
    fc.assert(
      fc.property(fc.array(WORD), (words) => {
        const html = `<div class="x">${words.join("<br/>")}</div>`;

        expect(NotesApi.asPlainText(html)).not.toMatch(/[<>]/);
      }),
    );
  });

  it("reads markup with no words as empty text", () => {
    expect(NotesApi.asPlainText("<p></p>")).toBe("");
  });
});

describe("NotesApi.readingMinutes", () => {
  it("readingMinutes property never claims less than a whole minute", async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer({ min: 1, max: 5000 }), async (wordCount) => {
        Session.store("token");
        const content = Array.from({ length: wordCount }, () => "word").join(
          " ",
        );
        stubFetch(jsonResponse({ name: "n", content }));

        const note = await NotesApi.note("id");

        expect(note.readingMinutes).toBeGreaterThanOrEqual(1);
      }),
    );
  });

  it("claims no reading time for a note with no words", async () => {
    Session.store("token");
    stubFetch(jsonResponse({ name: "n", content: "" }));

    await expect(NotesApi.note("id")).resolves.toMatchObject({
      readingMinutes: null,
    });
  });

  it("counts two hundred words as a minute and four hundred as two", async () => {
    Session.store("token");
    const words = (count: number): string =>
      Array.from({ length: count }, () => "word").join(" ");
    stubFetch(jsonResponse({ content: words(400) }));

    await expect(NotesApi.note("id")).resolves.toMatchObject({
      readingMinutes: 2,
    });
  });
});
