import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import fc from "fast-check";
import { FileBookmark } from "../src/features/files/FileBookmark";
import { FileFailure } from "../src/features/files/FileFailure";
import { FileSpinner } from "../src/features/files/FileSpinner";
import "./file-views-support";

describe("FileSpinner", () => {
  it("says what it is waiting for", () => {
    fc.assert(
      fc.property(fc.stringMatching(/^[A-Za-z .…]{1,20}$/), (label) => {
        const { unmount } = render(() => <FileSpinner label={label} />);

        expect(document.querySelector(".file-loading")?.textContent).toBe(
          label,
        );
        unmount();
      }),
    );
  });
});

describe("FileFailure", () => {
  it("names the file and the reason it would not open", () => {
    render(() => <FileFailure fileName="notes.pdf" reason="It is corrupt" />);

    expect(document.querySelector(".file-failure-title")?.textContent).toBe(
      "Couldn't open notes.pdf",
    );
    expect(document.querySelector(".file-failure-reason")?.textContent).toBe(
      "It is corrupt",
    );
  });

  it("reloads the page when asked to try again", () => {
    const reload = vi.fn();
    Object.defineProperty(window, "location", {
      value: { reload },
      writable: true,
      configurable: true,
    });
    render(() => <FileFailure fileName="notes.pdf" reason="It is corrupt" />);

    fireEvent.click(screen.getByRole("button", { name: "Try again" }));

    expect(reload).toHaveBeenCalledTimes(1);
  });
});

describe("FileBookmark", () => {
  it("bookmarks the page in view when there is none", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 50 }), (pageInView) => {
        const onRemember = vi.fn();
        const { unmount } = render(() => (
          <FileBookmark
            page={null}
            pageInView={pageInView}
            onRemember={onRemember}
            onForget={vi.fn()}
          />
        ));

        fireEvent.click(
          screen.getByRole("button", { name: `Bookmark page ${pageInView}` }),
        );

        expect(onRemember).toHaveBeenCalledWith(pageInView);
        unmount();
      }),
    );
  });

  it("removes the bookmark on the page in view", () => {
    const onForget = vi.fn();
    render(() => (
      <FileBookmark
        page={3}
        pageInView={3}
        onRemember={vi.fn()}
        onForget={onForget}
      />
    ));
    const button = screen.getByRole("button", {
      name: "Remove the bookmark on page 3",
    });

    expect(button.className).toContain("is-bookmarked");
    expect(button.getAttribute("aria-pressed")).toBe("true");

    fireEvent.click(button);

    expect(onForget).toHaveBeenCalledTimes(1);
  });
});
