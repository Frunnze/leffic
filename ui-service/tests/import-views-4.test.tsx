import { describe, expect, it } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import { ImportSource } from "../src/features/folder/import/ImportSource";
import { pdfFile } from "./import-factories";
import { NO_SOURCE_PROPS, sourceHandlers } from "./import-views-support";

describe("ImportSource", () => {
  it("offers every kind of source", () => {
    render(() => <ImportSource {...NO_SOURCE_PROPS} {...sourceHandlers()} />);

    expect(screen.getByLabelText("File")).toHaveProperty("checked", true);
    expect(screen.getByLabelText("Link")).toBeTruthy();
  });

  it("switches to another kind of source", () => {
    const handlers = sourceHandlers();
    render(() => <ImportSource {...NO_SOURCE_PROPS} {...handlers} />);

    fireEvent.change(screen.getByLabelText("Topic"));

    expect(handlers.onKindChange).toHaveBeenCalledWith("topic");
  });

  it("invites a file when none was chosen", () => {
    render(() => <ImportSource {...NO_SOURCE_PROPS} {...sourceHandlers()} />);

    expect(document.querySelector(".dropzone-text")?.textContent).toBe(
      "Drop a file here",
    );
  });

  it("names the chosen file and offers the page range for a pdf", () => {
    render(() => (
      <ImportSource
        {...NO_SOURCE_PROPS}
        chosenFile={pdfFile("biology.pdf")}
        {...sourceHandlers()}
      />
    ));

    expect(document.querySelector(".chosen-file-name")?.textContent).toBe(
      "biology.pdf",
    );
    expect(screen.getByLabelText("First page")).toBeTruthy();
  });

  it("reports both ends of the page range", () => {
    const handlers = sourceHandlers();
    render(() => (
      <ImportSource
        {...NO_SOURCE_PROPS}
        chosenFile={pdfFile("biology.pdf")}
        {...handlers}
      />
    ));

    fireEvent.input(screen.getByLabelText("First page"), {
      target: { value: "2" },
    });
    fireEvent.input(screen.getByLabelText("Last page"), {
      target: { value: "8" },
    });

    expect(handlers.onFirstPageChange).toHaveBeenCalledWith("2");
    expect(handlers.onLastPageChange).toHaveBeenCalledWith("8");
  });

  it("offers no page range for a file without pages", () => {
    render(() => (
      <ImportSource
        {...NO_SOURCE_PROPS}
        chosenFile={new File(["x"], "notes.txt")}
        {...sourceHandlers()}
      />
    ));

    expect(screen.queryByLabelText("First page")).toBeNull();
  });

  it("reports the file that was chosen", () => {
    const handlers = sourceHandlers();
    const chosen = pdfFile();
    render(() => <ImportSource {...NO_SOURCE_PROPS} {...handlers} />);
    const input = document.querySelector("#import-file") as HTMLInputElement;

    Object.defineProperty(input, "files", { value: [chosen], writable: true });
    fireEvent.change(input);

    expect(handlers.onFileChosen).toHaveBeenCalledWith(chosen);
  });

  it("reports nothing when the picker was dismissed", () => {
    const handlers = sourceHandlers();
    render(() => <ImportSource {...NO_SOURCE_PROPS} {...handlers} />);
    const input = document.querySelector("#import-file") as HTMLInputElement;

    Object.defineProperty(input, "files", { value: [], writable: true });
    fireEvent.change(input);

    expect(handlers.onFileChosen).not.toHaveBeenCalled();
  });

  it("reports nothing when the browser offers no file list", () => {
    const handlers = sourceHandlers();
    render(() => <ImportSource {...NO_SOURCE_PROPS} {...handlers} />);
    const input = document.querySelector("#import-file") as HTMLInputElement;

    Object.defineProperty(input, "files", { value: null, writable: true });
    fireEvent.change(input);

    expect(handlers.onFileChosen).not.toHaveBeenCalled();
  });

  it("takes a link", () => {
    const handlers = sourceHandlers();
    render(() => (
      <ImportSource {...NO_SOURCE_PROPS} kind="link" {...handlers} />
    ));

    fireEvent.input(document.querySelector("#import-link") as HTMLElement, {
      target: { value: "https://example.test" },
    });

    expect(handlers.onLinkChange).toHaveBeenCalledWith("https://example.test");
  });

  it("takes pasted text", () => {
    const handlers = sourceHandlers();
    render(() => (
      <ImportSource {...NO_SOURCE_PROPS} kind="text" {...handlers} />
    ));

    fireEvent.input(document.querySelector("#import-text") as HTMLElement, {
      target: { value: "some notes" },
    });

    expect(handlers.onTextChange).toHaveBeenCalledWith("some notes");
  });

  it("takes a topic", () => {
    const handlers = sourceHandlers();
    render(() => (
      <ImportSource {...NO_SOURCE_PROPS} kind="topic" {...handlers} />
    ));

    fireEvent.input(document.querySelector("#import-topic") as HTMLElement, {
      target: { value: "mitosis" },
    });

    expect(handlers.onTopicChange).toHaveBeenCalledWith("mitosis");
  });
});
