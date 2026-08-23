import { describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import { extractedSource } from "../src/features/folder/import/source-extraction";
import { importRequest } from "./import-factories";

describe("source extraction properties", () => {
  it("extractedSource property preserves every extracted text", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string(), async (text) => {
        const extractText = vi.fn().mockResolvedValue(text);
        const request = importRequest({
          kind: "link",
          link: "https://example.test",
        });
        const source = { kind: "link" as const, url: request.link };

        await expect(
          extractedSource.call(
            { source: vi.fn().mockResolvedValue(source) },
            request,
            {
              extractText,
              uploadIntoFolder: vi.fn(),
              writeNote: vi.fn(),
            },
          ),
        ).resolves.toEqual({ text, isNoteAlreadyMade: false });
        expect(extractText).toHaveBeenCalledWith(source);
      }),
    );
  });
});
