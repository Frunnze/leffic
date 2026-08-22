import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import { FilesApi } from "../src/features/files/files-api";
import { PdfViewer } from "../src/features/files/pdf-viewer";
import { Session } from "../src/shared/api/session";
import { UnauthorizedError } from "../src/shared/api/http";
import {
  emptyResponse,
  jsonResponse,
  requestedInit,
  requestedUrl,
  stubFetch,
} from "./support";

beforeEach(() => {
  Session.store("token");
  vi.spyOn(PdfViewer, "opened").mockResolvedValue("document" as never);
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  Session.store(null);
});

describe("FilesApi.openedDocument", () => {
  it("openedDocument property asks for exactly the file it was given", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.uuid(),
        fc.constantFrom("pdf", "docx"),
        async (fileId, extension) => {
          stubFetch(jsonResponse({ page: null }));

          await FilesApi.openedDocument(fileId, extension);

          expect(PdfViewer.opened).toHaveBeenCalledWith(
            expect.stringContaining(`file_id=${encodeURIComponent(fileId)}`),
            { Authorization: "Bearer token" },
          );
        },
      ),
    );
  });

  it("refreshes the session when no token is held", async () => {
    Session.store(null);
    stubFetch(jsonResponse({ access_token: "fresh" }));

    await FilesApi.openedDocument("1", "pdf");

    expect(PdfViewer.opened).toHaveBeenCalledWith(expect.any(String), {
      Authorization: "Bearer fresh",
    });
  });

  it("refuses to open a file it cannot authorise", async () => {
    Session.store(null);
    stubFetch(emptyResponse(500));

    await expect(FilesApi.openedDocument("1", "pdf")).rejects.toThrow(
      UnauthorizedError,
    );
  });
});

describe("FilesApi.opened", () => {
  it("opened property brings the document and its bookmark back together", async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer({ min: 1, max: 500 }), async (page) => {
        stubFetch(jsonResponse({ page }));

        await expect(FilesApi.opened("1", "pdf")).resolves.toEqual({
          document: "document",
          bookmarkedPage: page,
        });
      }),
    );
  });
});

describe("FilesApi.bookmarkedPage", () => {
  it("bookmarkedPage property asks the bookmark endpoint for that file", async () => {
    await fc.assert(
      fc.asyncProperty(fc.uuid(), async (fileId) => {
        const fetching = stubFetch(jsonResponse({ page: 2 }));

        await FilesApi.bookmarkedPage(fileId);

        expect(requestedUrl(fetching)).toContain(
          `file_id=${encodeURIComponent(fileId)}`,
        );
      }),
    );
  });

  it("reports no page when the file was never bookmarked", async () => {
    stubFetch(jsonResponse({}));

    await expect(FilesApi.bookmarkedPage("1")).resolves.toBeNull();
  });
});

describe("FilesApi.rememberPage", () => {
  it("rememberPage property stores the page and reads it back", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.uuid(),
        fc.integer({ min: 1, max: 500 }),
        async (fileId, page) => {
          const fetching = stubFetch(jsonResponse({ page }));

          await expect(FilesApi.rememberPage(fileId, page)).resolves.toBe(page);
          expect(requestedInit(fetching).method).toBe("PUT");
          expect(requestedInit(fetching).body).toBe(
            JSON.stringify({ file_id: fileId, page }),
          );
        },
      ),
    );
  });

  it("reports no page when the service stored none", async () => {
    stubFetch(jsonResponse({}));

    await expect(FilesApi.rememberPage("1", 3)).resolves.toBeNull();
  });
});

describe("FilesApi.forgetPage", () => {
  it("forgetPage property deletes the bookmark for that file", async () => {
    await fc.assert(
      fc.asyncProperty(fc.uuid(), async (fileId) => {
        const fetching = stubFetch(jsonResponse({}));

        await FilesApi.forgetPage(fileId);

        expect(requestedInit(fetching).method).toBe("DELETE");
        expect(requestedUrl(fetching)).toContain(
          `file_id=${encodeURIComponent(fileId)}`,
        );
      }),
    );
  });
});
