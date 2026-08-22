import { describe, expect, it, vi } from "vitest";
import { render, waitFor } from "@solidjs/testing-library";
import { PdfPages } from "../src/features/files/PdfPages";
import { PdfViewer } from "../src/features/files/pdf-viewer";
import { entryFor, stubObservers } from "./observer-support";
import { SHAPE, documentOf } from "./file-views-support";

describe("PdfPages", () => {
  function renderPages(
    numPages = 2,
    openAtPage: number | null = null,
    onPageInView = vi.fn(),
  ): ReturnType<typeof render> {
    return render(() => (
      <PdfPages
        document={documentOf(numPages)}
        openAtPage={openAtPage}
        onPageInView={onPageInView}
      />
    ));
  }

  it("lays out one frame per page", async () => {
    stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockResolvedValue(SHAPE);
    renderPages(3);

    await waitFor(() =>
      expect(document.querySelectorAll(".pdf-page")).toHaveLength(3),
    );
  });

  it("sizes the stage to the first page", async () => {
    stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockResolvedValue(SHAPE);
    renderPages();

    await waitFor(() =>
      expect(
        (
          document.querySelector(".pdf-pages") as HTMLElement
        ).style.getPropertyValue("--pdf-page-width"),
      ).toBe("700px"),
    );
  });

  it("scrolls to the bookmarked page", async () => {
    stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockResolvedValue(SHAPE);
    renderPages(3, 2);
    const stage = document.querySelector(".pdf-pages") as HTMLElement;

    await waitFor(() => expect(stage.scrollTop).toBe(0));
  });

  it("ignores a bookmark on a page the document does not have", async () => {
    stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockResolvedValue(SHAPE);
    renderPages(1, 9);

    await waitFor(() =>
      expect(document.querySelectorAll(".pdf-page")).toHaveLength(1),
    );
  });

  it("paints a page once it comes near the viewport", async () => {
    const observers = stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockResolvedValue(SHAPE);
    const painting = vi
      .spyOn(PdfViewer, "paintPage")
      .mockResolvedValue(undefined);
    vi.spyOn(PdfViewer, "paintSelectableText").mockResolvedValue(undefined);
    vi.spyOn(PdfViewer, "matchPaintedWidth").mockReturnValue(undefined);
    renderPages(2);

    await waitFor(() => expect(observers.intersections).toHaveLength(2));
    observers.intersections[0]?.([entryFor(1, true)]);

    await waitFor(() => expect(painting).toHaveBeenCalledTimes(1));
  });

  it("paints a page only once however often it comes near", async () => {
    const observers = stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockResolvedValue(SHAPE);
    const painting = vi
      .spyOn(PdfViewer, "paintPage")
      .mockResolvedValue(undefined);
    vi.spyOn(PdfViewer, "paintSelectableText").mockResolvedValue(undefined);
    vi.spyOn(PdfViewer, "matchPaintedWidth").mockReturnValue(undefined);
    renderPages(2);

    await waitFor(() => expect(observers.intersections).toHaveLength(2));
    observers.intersections[0]?.([entryFor(1, true)]);
    observers.intersections[0]?.([entryFor(1, true)]);

    await waitFor(() => expect(painting).toHaveBeenCalledTimes(1));
  });

  it("forgets a page once it leaves the viewport", async () => {
    const observers = stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockResolvedValue(SHAPE);
    vi.spyOn(PdfViewer, "paintPage").mockResolvedValue(undefined);
    vi.spyOn(PdfViewer, "paintSelectableText").mockResolvedValue(undefined);
    vi.spyOn(PdfViewer, "matchPaintedWidth").mockReturnValue(undefined);
    renderPages(2);

    await waitFor(() => expect(observers.intersections).toHaveLength(2));
    observers.intersections[0]?.([entryFor(1, true)]);
    await waitFor(() => expect(PdfViewer.paintPage).toHaveBeenCalledTimes(1));
    observers.intersections[0]?.([entryFor(1, false)]);

    const canvas = document.querySelector(
      ".pdf-page-canvas",
    ) as HTMLCanvasElement;

    expect(canvas.width).toBe(0);
  });

  it("forgets a page that was painted after it left", async () => {
    const observers = stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockResolvedValue(SHAPE);
    vi.spyOn(PdfViewer, "paintPage").mockResolvedValue(undefined);
    vi.spyOn(PdfViewer, "paintSelectableText").mockResolvedValue(undefined);
    vi.spyOn(PdfViewer, "matchPaintedWidth").mockReturnValue(undefined);
    renderPages(2);

    await waitFor(() => expect(observers.intersections).toHaveLength(2));
    observers.intersections[0]?.([entryFor(1, true), entryFor(1, false)]);

    await waitFor(() => expect(PdfViewer.paintPage).toHaveBeenCalledTimes(1));
  });

  it("ignores an entry for a page it never laid out", async () => {
    const observers = stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockResolvedValue(SHAPE);
    const painting = vi
      .spyOn(PdfViewer, "paintPage")
      .mockResolvedValue(undefined);
    renderPages(1);

    await waitFor(() => expect(observers.intersections).toHaveLength(2));
    observers.intersections[0]?.([entryFor(99, true), entryFor(99, false)]);

    expect(painting).not.toHaveBeenCalled();
  });

  it("reports the page that is on screen", async () => {
    const observers = stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockResolvedValue(SHAPE);
    const onPageInView = vi.fn();
    renderPages(2, null, onPageInView);

    await waitFor(() => expect(observers.intersections).toHaveLength(2));
    observers.intersections[1]?.([entryFor(2, true), entryFor(1, false)]);

    expect(onPageInView).toHaveBeenCalledExactlyOnceWith(2);
  });

  it("realigns the text when the pages are resized", async () => {
    const observers = stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockResolvedValue(SHAPE);
    vi.spyOn(PdfViewer, "paintPage").mockResolvedValue(undefined);
    vi.spyOn(PdfViewer, "paintSelectableText").mockResolvedValue(undefined);
    const matching = vi
      .spyOn(PdfViewer, "matchPaintedWidth")
      .mockReturnValue(undefined);
    renderPages(2);

    await waitFor(() => expect(observers.resizes).toHaveLength(1));
    observers.intersections[0]?.([entryFor(1, true)]);
    await waitFor(() => expect(matching).toHaveBeenCalledTimes(1));

    observers.resizes[0]?.();

    expect(matching).toHaveBeenCalledTimes(2);
  });

  it("stops watching once the viewer is gone", async () => {
    const observers = stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockResolvedValue(SHAPE);
    const rendered = renderPages(2);

    await waitFor(() => expect(observers.resizes).toHaveLength(1));
    rendered.unmount();

    expect(observers.disconnects).toHaveBeenCalledTimes(3);
  });

  it("stops watching even before the first page was measured", () => {
    stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockImplementation(
      () => new Promise(() => undefined),
    );
    const rendered = renderPages(2);

    rendered.unmount();

    expect(document.querySelectorAll(".pdf-page")).toHaveLength(0);
  });
});
