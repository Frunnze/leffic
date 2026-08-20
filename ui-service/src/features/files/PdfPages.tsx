import { For, onCleanup, onMount, type JSX } from "solid-js";
import type { PDFDocumentProxy } from "pdfjs-dist";
import { PdfViewer } from "./pdf-viewer";

const MOSTLY_VISIBLE = 0.5;
const NEARBY_MARGIN = "150% 0px";

export type PdfPagesProps = {
  readonly document: PDFDocumentProxy;
  readonly openAtPage: number | null;
  readonly onPageInView: (page: number) => void;
};

export function PdfPages(props: PdfPagesProps): JSX.Element {
  const pageNumbers = (): readonly number[] =>
    Array.from({ length: props.document.numPages }, (_, index) => index + 1);

  const frames = new Map<number, HTMLElement>();
  const canvases = new Map<number, HTMLCanvasElement>();
  const textHosts = new Map<number, HTMLElement>();
  const paintedPages = new Set<number>();
  const nearbyPages = new Set<number>();
  let stage: HTMLDivElement | undefined;
  let unscaledPageWidth = 0;

  const paintPage = async (page: number): Promise<void> => {
    const canvas = canvases.get(page);
    const textHost = textHosts.get(page);

    if (canvas === undefined || textHost === undefined) return;
    if (paintedPages.has(page)) return;

    paintedPages.add(page);

    await PdfViewer.paintPage(props.document, page, canvas);
    await PdfViewer.paintSelectableText(props.document, page, textHost);
    PdfViewer.matchPaintedWidth(textHost, unscaledPageWidth);

    if (!nearbyPages.has(page)) forgetPage(page);
  };

  const forgetPage = (page: number): void => {
    const canvas = canvases.get(page);
    const textHost = textHosts.get(page);

    if (canvas === undefined || textHost === undefined) return;
    if (!paintedPages.has(page)) return;

    paintedPages.delete(page);
    canvas.width = 0;
    canvas.height = 0;
    textHost.replaceChildren();
  };

  const scrollStageToPage = (page: number): void => {
    const frame = frames.get(page);

    if (frame === undefined || stage === undefined) return;

    stage.scrollTop = frame.offsetTop - stage.offsetTop;
  };

  const alignTextToPaintedWidth = (): void => {
    for (const page of paintedPages) {
      const textHost = textHosts.get(page);

      if (textHost !== undefined) {
        PdfViewer.matchPaintedWidth(textHost, unscaledPageWidth);
      }
    }
  };

  const watchWhatIsNearby = (): IntersectionObserver => {
    const watcher = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          const page = Number(entry.target.getAttribute("data-page"));

          if (entry.isIntersecting) {
            nearbyPages.add(page);
            void paintPage(page);
          } else {
            nearbyPages.delete(page);
            forgetPage(page);
          }
        }
      },
      { rootMargin: NEARBY_MARGIN },
    );

    for (const frame of frames.values()) watcher.observe(frame);

    return watcher;
  };

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

    for (const frame of frames.values()) watcher.observe(frame);

    return watcher;
  };

  const watchHowWideThePagesAre = (): ResizeObserver => {
    const watcher = new ResizeObserver(() => alignTextToPaintedWidth());

    for (const frame of frames.values()) watcher.observe(frame);

    return watcher;
  };

  onMount(() => {
    void PdfViewer.pageShape(props.document).then((shape) => {
      unscaledPageWidth = shape.unscaledWidth;
      stage?.style.setProperty("--pdf-page-width", `${shape.width}px`);
      stage?.style.setProperty("--pdf-page-ratio", String(shape.ratio));

      const opened = props.openAtPage;

      if (opened !== null) scrollStageToPage(opened);

      const nearby = watchWhatIsNearby();
      const onScreen = watchWhatIsOnScreen();
      const widths = watchHowWideThePagesAre();

      onCleanup(() => {
        nearby.disconnect();
        onScreen.disconnect();
        widths.disconnect();
      });
    });
  });

  return (
    <div class="pdf-pages" ref={stage}>
      <For each={pageNumbers()}>
        {(page) => (
          <div
            class="pdf-page"
            data-page={page}
            ref={(element) => frames.set(page, element)}
          >
            <canvas
              class="pdf-page-canvas"
              ref={(element) => canvases.set(page, element)}
            />
            <div
              class="textLayer"
              ref={(element) => textHosts.set(page, element)}
            />
          </div>
        )}
      </For>
    </div>
  );
}
