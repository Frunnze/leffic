import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { GenerationApi } from "../src/features/folder/import/generation-api";
import {
  jsonResponse,
  requestedInit,
  requestedUrl,
  stubFetch,
} from "./support";
import { pdfFile } from "./import-factories";
import { FILE_SOURCE, ORIGIN, sentBody } from "./generation-api-support";

describe("GenerationApi.uploadFile", () => {
  it("uploadFile property sends the file into the folder it names", async () => {
    await fc.assert(
      fc.asyncProperty(fc.uuid(), async (folderId) => {
        const fetching = stubFetch(jsonResponse({ file_metadata: [] }));

        await GenerationApi.uploadFile(pdfFile(), folderId);

        const form = requestedInit(fetching).body as FormData;

        expect(requestedUrl(fetching)).toContain("/api/content/upload-files");
        expect(form.get("folder_id")).toBe(folderId);
      }),
    );
  });

  it("reads every uploaded file out of the reply", async () => {
    stubFetch(
      jsonResponse({
        file_metadata: [
          { file_id: 4, name: "a.pdf", extension: "pdf", created_at: "now" },
        ],
      }),
    );

    await expect(GenerationApi.uploadFile(pdfFile(), "home")).resolves.toEqual([
      { fileId: "4", name: "a.pdf", extension: "pdf", createdAt: "now" },
    ]);
  });
});

describe("GenerationApi.toUploadedFile", () => {
  it("toUploadedFile property always names a file, even a nameless one", async () => {
    await fc.assert(
      fc.asyncProperty(fc.uuid(), async (fileId) => {
        stubFetch(jsonResponse({ file_metadata: [{ file_id: fileId }] }));

        const [uploaded] = await GenerationApi.uploadFile(pdfFile(), "home");

        expect(uploaded).toMatchObject({
          fileId,
          name: "Untitled file",
          extension: "",
        });
        expect(uploaded?.createdAt).not.toBe("");
      }),
    );
  });
});

describe("GenerationApi.extractText and GenerationApi.sourceBody", () => {
  it("extractText property hands back the text the service extracted", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string(), async (text) => {
        stubFetch(jsonResponse({ text }));

        await expect(GenerationApi.extractText(FILE_SOURCE)).resolves.toBe(
          text,
        );
      }),
    );
  });

  it("sourceBody property sends a link as link metadata", async () => {
    await fc.assert(
      fc.asyncProperty(fc.webUrl(), async (url) => {
        const fetching = stubFetch(jsonResponse({ text: "" }));

        await GenerationApi.extractText({ kind: "link", url });

        expect(sentBody(fetching)).toEqual({ link_metadata: url });
      }),
    );
  });

  it("sends a topic as topic metadata", async () => {
    const fetching = stubFetch(jsonResponse({ text: "" }));

    await GenerationApi.extractText({ kind: "topic", topic: "mitosis" });

    expect(sentBody(fetching)).toEqual({ topic_metadata: "mitosis" });
  });

  it("sends a whole file with no page range", async () => {
    const fetching = stubFetch(jsonResponse({ text: "" }));

    await GenerationApi.extractText(FILE_SOURCE);

    expect(sentBody(fetching)).toEqual({
      file_metadata: [{ file_id: "9" }],
    });
  });

  it("sends only the pages the learner asked for", async () => {
    const fetching = stubFetch(jsonResponse({ text: "" }));

    await GenerationApi.extractText({
      ...FILE_SOURCE,
      firstPage: 2,
      lastPage: 5,
    });

    expect(sentBody(fetching)).toEqual({
      file_metadata: [
        { file_id: "9", pages: { first: 2, last: 5 } },
      ],
    });
  });

  it("sends an open-ended range when only one end was given", async () => {
    const fetching = stubFetch(jsonResponse({ text: "" }));

    await GenerationApi.extractText({ ...FILE_SOURCE, firstPage: 3 });

    expect(sentBody(fetching)).toEqual({
      file_metadata: [{ file_id: "9", pages: { first: 3 } }],
    });
  });
});

describe("GenerationApi.start and GenerationApi.sourceText", () => {
  it("start property hands back every task id the service opened", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(fc.uuid(), { maxLength: 3 }),
        async (flashcardTaskIds) => {
          stubFetch(
            jsonResponse({
              flashcard_task_ids: flashcardTaskIds,
              note_task_id: null,
              test_task_ids: [],
            }),
          );

          await expect(
            GenerationApi.start(
              { kind: "topic", topic: "cells" },
              ORIGIN,
              "home",
            ),
          ).resolves.toEqual({
            flashcardsTaskIds: flashcardTaskIds,
            noteTaskId: null,
            testTaskIds: [],
          });
        },
      ),
    );
  });

  it("sourceText property sends a topic straight through without extracting", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string({ minLength: 1 }), async (topic) => {
        const fetching = stubFetch(jsonResponse({}));

        await GenerationApi.start({ kind: "topic", topic }, ORIGIN, "home");

        expect(fetching).toHaveBeenCalledTimes(1);
        expect(sentBody(fetching)).toMatchObject({ text: topic });
      }),
    );
  });

  it("extracts a file's text before starting the generation", async () => {
    const fetching = stubFetch(
      jsonResponse({ text: "extracted" }),
      jsonResponse({}),
    );

    await GenerationApi.start(FILE_SOURCE, ORIGIN, "home");

    expect(fetching).toHaveBeenCalledTimes(2);
    expect(sentBody(fetching, 1)).toMatchObject({
      text: "extracted",
      source_kind: "file",
      source_reference: "notes.pdf",
    });
  });
});
