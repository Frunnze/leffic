import { GlobalWorkerOptions, getDocument } from "pdfjs-dist";
import type { PDFDocumentProxy } from "pdfjs-dist";
import PdfWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";

const RENDER_SCALE = 1.4;

GlobalWorkerOptions.workerSrc = PdfWorker;

export class PdfViewer {
  static async opened(url: string): Promise<PDFDocumentProxy> {
    return getDocument(url).promise;
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

    canvas.width = viewport.width;
    canvas.height = viewport.height;

    await page.render({ canvasContext: context, viewport }).promise;
  }
}
