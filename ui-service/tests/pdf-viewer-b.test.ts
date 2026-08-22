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

describe("PdfViewer.paintSelectableText", () => {
  it("paintSelectableText property renders the text of the page it names", async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer({ min: 1, max: 20 }), async (pageNumber) => {
        const document = documentOf(pageOf(100, 200));
        const host = window.document.createElement("div");

        await PdfViewer.paintSelectableText(
          asDocument(document),
          pageNumber,
          host,
        );

        expect(document.getPage).toHaveBeenCalledWith(pageNumber);
        expect(renderTextLayer).toHaveBeenCalled();
      }),
    );
  });
});

describe("PdfViewer.matchPaintedWidth", () => {
  it("matchPaintedWidth property scales the text to the painted width", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 2000 }), (unscaledWidth) => {
        const host = window.document.createElement("div");
        Object.defineProperty(host, "clientWidth", { value: 700 });

        PdfViewer.matchPaintedWidth(host, unscaledWidth);

        expect(host.style.getPropertyValue("--scale-factor")).toBe(
          String(700 / unscaledWidth),
        );
      }),
    );
  });

  it("leaves the text alone before the page has been measured", () => {
    const host = window.document.createElement("div");

    PdfViewer.matchPaintedWidth(host, 0);

    expect(host.style.getPropertyValue("--scale-factor")).toBe("");
  });
});
