import { describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import { GenerationSourceHandlers } from "../src/features/folder/import/generation-source-handlers";

describe("GenerationSourceHandlers properties", () => {
  it("body property preserves every link as link metadata", () => {
    fc.assert(
      fc.property(fc.webUrl(), (url) => {
        expect(
          GenerationSourceHandlers.body({ kind: "link", url }),
        ).toEqual({ link_metadata: url });
      }),
    );
  });

  it("text property returns every topic without extraction", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string(), async (topic) => {
        const extract = (): Promise<string> =>
          Promise.reject(new Error("Topics need no extraction"));

        await expect(
          GenerationSourceHandlers.text({ kind: "topic", topic }, extract),
        ).resolves.toBe(topic);
      }),
    );
  });

  it("extracts the text for every link", async () => {
    await fc.assert(
      fc.asyncProperty(fc.webUrl(), async (url) => {
        const extract = vi.fn(() => Promise.resolve(url));
        const source = { kind: "link", url } as const;

        await expect(
          GenerationSourceHandlers.text(source, extract),
        ).resolves.toBe(url);
        expect(extract).toHaveBeenCalledWith(source);
      }),
    );
  });
});
