import { beforeEach, describe, expect, it, vi, type Mock } from "vitest";
import fc from "fast-check";
import type { PDFDocumentProxy } from "pdfjs-dist";

const getDocument = vi.fn();
const renderTextLayer = vi.fn();

vi.mock("pdfjs-dist/build/pdf.worker.min.mjs?url", () => ({
  default: "/pdf.worker.js",
}));

vi.mock("pdfjs-dist", () => ({
  GlobalWorkerOptions: { workerSrc: "" },
  getDocument,
  TextLayer: class {
    render = renderTextLayer;
  },
}));

const { PdfViewer } = await import("../src/features/files/pdf-viewer");
const { GlobalWorkerOptions } = await import("pdfjs-dist");

type FakePage = {
  getViewport: (options: { scale: number }) => {
    width: number;
    height: number;
  };
  render: (options: unknown) => { promise: Promise<void> };
  streamTextContent: () => unknown;
};

type FakeDocument = { getPage: Mock };

function documentOf(page: FakePage): FakeDocument {
  return { getPage: vi.fn().mockResolvedValue(page) };
}

function asDocument(fake: FakeDocument): PDFDocumentProxy {
  return fake as unknown as PDFDocumentProxy;
}

function pageOf(width: number, height: number): FakePage {
  return {
    getViewport: ({ scale }) => ({
      width: width * scale,
      height: height * scale,
    }),
    render: () => ({ promise: Promise.resolve() }),
    streamTextContent: () => ({}),
  };
}

beforeEach(() => {
  getDocument.mockReturnValue({ promise: Promise.resolve("document") });
  renderTextLayer.mockResolvedValue(undefined);
});

describe("PdfViewer.opened", () => {
  it("opened property fetches the url with the headers it was given", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.webUrl(),
        fc.string({ minLength: 1 }),
        async (url, token) => {
          await PdfViewer.opened(url, { Authorization: token });

          expect(getDocument).toHaveBeenCalledWith({
            url,
            httpHeaders: { Authorization: token },
          });
        },
      ),
    );
  });

  it("names the worker the bundle ships", () => {
    expect(GlobalWorkerOptions.workerSrc).toBe("/pdf.worker.js");
  });
});

describe("PdfViewer.pageShape", () => {
  it("pageShape property keeps the page's own aspect ratio", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 1, max: 2000 }),
        fc.integer({ min: 1, max: 2000 }),
        async (width, height) => {
          const shape = await PdfViewer.pageShape(
            asDocument(documentOf(pageOf(width, height))),
          );

          expect(shape.ratio).toBeCloseTo(width / height, 6);
        },
      ),
    );
  });

  it("pageShape property reports the width before any scaling", async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer({ min: 1, max: 2000 }), async (width) => {
        const shape = await PdfViewer.pageShape(
          asDocument(documentOf(pageOf(width, 100))),
        );

        expect(shape.unscaledWidth).toBeCloseTo(width, 6);
        expect(shape.width).toBeCloseTo(width * 1.4, 6);
      }),
    );
  });
});

describe("PdfViewer.paintPage", () => {
  it("paintPage property paints the page it was asked for", async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer({ min: 1, max: 20 }), async (pageNumber) => {
        const document = documentOf(pageOf(100, 200));
        const canvas = window.document.createElement("canvas");
        vi.spyOn(canvas, "getContext").mockReturnValue({} as never);

        await PdfViewer.paintPage(asDocument(document), pageNumber, canvas);

        expect(document.getPage).toHaveBeenCalledWith(pageNumber);
      }),
    );
  });

  it("sizes the canvas to the painted page", async () => {
    const canvas = window.document.createElement("canvas");
    vi.spyOn(canvas, "getContext").mockReturnValue({} as never);
    vi.stubGlobal("devicePixelRatio", 2);

    await PdfViewer.paintPage(
      asDocument(documentOf(pageOf(100, 200))),
      1,
      canvas,
    );

    expect(canvas.width).toBe(Math.floor(100 * 1.4 * 2));
    expect(canvas.height).toBe(Math.floor(200 * 1.4 * 2));
    vi.unstubAllGlobals();
  });

  it("falls back to a single pixel per point", async () => {
    const canvas = window.document.createElement("canvas");
    vi.spyOn(canvas, "getContext").mockReturnValue({} as never);
    vi.stubGlobal("devicePixelRatio", 0);

    await PdfViewer.paintPage(
      asDocument(documentOf(pageOf(100, 200))),
      1,
      canvas,
    );

    expect(canvas.width).toBe(Math.floor(100 * 1.4));
    vi.unstubAllGlobals();
  });

  it("paints nothing onto a canvas with no drawing context", async () => {
    const canvas = window.document.createElement("canvas");
    vi.spyOn(canvas, "getContext").mockReturnValue(null);

    await PdfViewer.paintPage(
      asDocument(documentOf(pageOf(100, 200))),
      1,
      canvas,
    );

    expect(canvas.width).toBe(300);
  });
});

