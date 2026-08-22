import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const ENTRY = "../src/index";

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
});

afterEach(() => {
  document.body.innerHTML = "";
  vi.unstubAllGlobals();
  vi.resetModules();
});

describe("the browser entry point", () => {
  it("mounts the app into the root element", async () => {
    const root = document.createElement("div");
    root.id = "root";
    document.body.append(root);

    await import(ENTRY);

    expect(root.innerHTML.length).toBeGreaterThan(0);
  });

  it("refuses to start without a root element", async () => {
    await expect(import(ENTRY)).rejects.toThrow(
      "Root element #root is missing from index.html",
    );
  });
});
