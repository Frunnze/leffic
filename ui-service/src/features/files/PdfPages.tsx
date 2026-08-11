import { For, onCleanup, onMount, type JSX } from "solid-js";
import type { PDFDocumentProxy } from "pdfjs-dist";
import { PdfViewer } from "./pdf-viewer";

const MOSTLY_VISIBLE = 0.5;

export type PdfPagesProps = {
  readonly document: PDFDocumentProxy;
  readonly openAtPage: number | null;
  readonly onPageInView: (page: number) => void;
};

export function PdfPages(props: PdfPagesProps): JSX.Element {
  const pageNumbers = (): readonly number[] =>
    Array.from({ length: props.document.numPages }, (_, index) => index + 1);

  const canvases = new Map<number, HTMLCanvasElement>();

  const watchWhatIsOnScreen = (): IntersectionObserver => {
    const watcher = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;

          const page = Number(entry.target.getAttribute("data-page"));
          props.onPageInView(page);
        }
      },
      { threshold: MOSTLY_VISIBLE },
    );

    for (const canvas of canvases.values()) watcher.observe(canvas);

    return watcher;
  };

  onMount(() => {
    const painted = pageNumbers().map((page) => {
      const canvas = canvases.get(page);

      return canvas === undefined
        ? Promise.resolve()
        : PdfViewer.paintPage(props.document, page, canvas);
    });

    void Promise.all(painted).then(() => {
      const opened = props.openAtPage;

      if (opened !== null) canvases.get(opened)?.scrollIntoView();

      const watcher = watchWhatIsOnScreen();
      onCleanup(() => watcher.disconnect());
    });
  });

  return (
    <div class="pdf-pages">
      <For each={pageNumbers()}>
        {(page) => (
          <canvas
            class="pdf-page"
            data-page={page}
            ref={(element) => canvases.set(page, element)}
          />
        )}
      </For>
    </div>
  );
}
