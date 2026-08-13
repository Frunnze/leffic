import { GlobalWorkerOptions, TextLayer, getDocument } from "pdfjs-dist";
import type { PDFDocumentProxy } from "pdfjs-dist";
import PdfWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";

const RENDER_SCALE = 1.4;
const SCALE_PROPERTY = "--scale-factor";

GlobalWorkerOptions.workerSrc = PdfWorker;

export type PageShape = {
  readonly width: number;
  readonly ratio: number;
  readonly unscaledWidth: number;
};

export class PdfViewer {
  static async opened(
    url: string,
    httpHeaders: Readonly<Record<string, string>>,
  ): Promise<PDFDocumentProxy> {
    return getDocument({ url, httpHeaders }).promise;
  }

  static async pageShape(document: PDFDocumentProxy): Promise<PageShape> {
    const page = await document.getPage(1);
    const viewport = page.getViewport({ scale: RENDER_SCALE });

    return {
      width: viewport.width,
      ratio: viewport.width / viewport.height,
      unscaledWidth: viewport.width / RENDER_SCALE,
    };
  }

  static async paintPage(
    document: PDFDocumentProxy,
    pageNumber: number,
    canvas: HTMLCanvasElement,
  ): Promise<void> {
    const page = await document.getPage(pageNumber);
    const viewport = page.getViewport({ scale: RENDER_SCALE });
    const context = canvas.getContext("2d");

    if (context === null) return;

    const pixelRatio = window.devicePixelRatio || 1;

    canvas.width = Math.floor(viewport.width * pixelRatio);
    canvas.height = Math.floor(viewport.height * pixelRatio);

    await page.render({
      canvasContext: context,
      viewport,
      transform: [pixelRatio, 0, 0, pixelRatio, 0, 0],
    }).promise;
  }

  static async paintSelectableText(
    document: PDFDocumentProxy,
    pageNumber: number,
    textHost: HTMLElement,
  ): Promise<void> {
    const page = await document.getPage(pageNumber);
    const textLayer = new TextLayer({
      textContentSource: page.streamTextContent(),
      container: textHost,
      viewport: page.getViewport({ scale: RENDER_SCALE }),
    });

    await textLayer.render();
  }

  static matchPaintedWidth(
    textHost: HTMLElement,
    unscaledWidth: number,
  ): void {
    if (unscaledWidth === 0) return;

    const paintedScale = textHost.clientWidth / unscaledWidth;

    textHost.style.setProperty(SCALE_PROPERTY, String(paintedScale));
  }
}
