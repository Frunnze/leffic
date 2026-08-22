import { describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor } from "@solidjs/testing-library";
import { AccountApi } from "../src/features/settings/account-api";
import { AskProvider } from "../src/shared/chatbot/AskContext";
import FilePage from "../src/features/files/FilePage";
import { FilesApi } from "../src/features/files/files-api";
import { PdfViewer } from "../src/features/files/pdf-viewer";
import { stubObservers } from "./observer-support";
import { renderAt } from "./router-support";
import { SHAPE, documentOf } from "./file-views-support";

describe("FilePage", () => {
  function renderFilePage(): ReturnType<typeof renderAt> {
    vi.spyOn(AccountApi, "read").mockResolvedValue({
      username: "learner",
      email: "learner@example.test",
      theme: "system",
    });

    return renderAt("/file/7/pdf", "/file/:id/:extension", () => (
      <AskProvider>
        <FilePage />
      </AskProvider>
    ));
  }

  it("waits while the file is opening", () => {
    stubObservers();
    vi.spyOn(FilesApi, "opened").mockImplementation(
      () => new Promise(() => undefined),
    );
    renderFilePage();

    expect(document.querySelector(".file-loading")?.textContent).toContain(
      "Opening 7.pdf…",
    );
  });

  it("shows the document and its page count", async () => {
    stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockResolvedValue(SHAPE);
    vi.spyOn(FilesApi, "opened").mockResolvedValue({
      document: documentOf(4),
      bookmarkedPage: null,
    });
    renderFilePage();

    await waitFor(() =>
      expect(document.querySelector(".file-position")?.textContent).toBe(
        "Page 1 of 4",
      ),
    );
    expect(document.querySelector(".file-chip")?.textContent).toBe("PDF");
  });

  it("says why the file would not open", async () => {
    vi.spyOn(FilesApi, "opened").mockRejectedValue(new Error("It is corrupt"));
    renderFilePage();

    await waitFor(() =>
      expect(document.querySelector(".file-failure-reason")?.textContent).toBe(
        "It is corrupt",
      ),
    );
  });

  it("shows a plain reason the file would not open", async () => {
    vi.spyOn(FilesApi, "opened").mockRejectedValue("Too large");
    renderFilePage();

    await waitFor(() =>
      expect(document.querySelector(".file-failure-reason")?.textContent).toBe(
        "Too large",
      ),
    );
  });

  it("bookmarks and un-bookmarks the page in view", async () => {
    stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockResolvedValue(SHAPE);
    vi.spyOn(FilesApi, "opened").mockResolvedValue({
      document: documentOf(2),
      bookmarkedPage: null,
    });
    const remembering = vi.spyOn(FilesApi, "rememberPage").mockResolvedValue(1);
    const forgetting = vi
      .spyOn(FilesApi, "forgetPage")
      .mockResolvedValue(undefined);
    renderFilePage();

    await waitFor(() =>
      screen.getByRole("button", { name: "Bookmark page 1" }),
    );
    fireEvent.click(screen.getByRole("button", { name: "Bookmark page 1" }));

    await waitFor(() => expect(remembering).toHaveBeenCalledWith("7", 1));
    fireEvent.click(
      screen.getByRole("button", { name: "Remove the bookmark on page 1" }),
    );

    await waitFor(() => expect(forgetting).toHaveBeenCalledWith("7"));
  });

  it("shows the bookmark the file already carries", async () => {
    stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockResolvedValue(SHAPE);
    vi.spyOn(FilesApi, "opened").mockResolvedValue({
      document: documentOf(3),
      bookmarkedPage: 2,
    });
    renderFilePage();

    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: "Bookmark page 1" }),
      ).toBeTruthy(),
    );
    expect(document.querySelector(".file-bookmark")).toBeTruthy();
  });

  it("closes the file", async () => {
    stubObservers();
    vi.spyOn(PdfViewer, "pageShape").mockResolvedValue(SHAPE);
    vi.spyOn(FilesApi, "opened").mockResolvedValue({
      document: documentOf(1),
      bookmarkedPage: null,
    });
    renderFilePage();

    await waitFor(() => screen.getByRole("button", { name: "Close 7.pdf" }));
    fireEvent.click(screen.getByRole("button", { name: "Close 7.pdf" }));

    expect(document.querySelector(".file-stage")).toBeTruthy();
  });
});
