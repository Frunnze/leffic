import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@solidjs/testing-library";
import { NewFolderButton } from "../src/features/folder/NewFolderButton";
import { ToastProvider } from "../src/shared/notifications/ToastContext";
import { UnitsApi } from "../src/features/folder/units-api";
import { unitOf } from "./unit-factories";
import "./folder-views-support";

describe("NewFolderButton", () => {
  function renderButton(onFolderCreated = vi.fn()): void {
    render(() => (
      <ToastProvider>
        <NewFolderButton folderId="home" onFolderCreated={onFolderCreated} />
      </ToastProvider>
    ));
  }

  it("creates the folder the learner named", async () => {
    const created = unitOf({ id: "new", name: "Biology", type: "folder" });
    vi.spyOn(UnitsApi, "createFolder").mockResolvedValue(created);
    const onFolderCreated = vi.fn();
    renderButton(onFolderCreated);

    fireEvent.click(screen.getByRole("button", { name: "New folder" }));
    fireEvent.input(screen.getByLabelText("Folder name"), {
      target: { value: "Biology" },
    });
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() =>
      expect(onFolderCreated).toHaveBeenCalledWith([created]),
    );
  });

  it("raises a toast when the folder cannot be created", async () => {
    vi.spyOn(UnitsApi, "createFolder").mockRejectedValue(new Error("no"));
    renderButton();

    fireEvent.click(screen.getByRole("button", { name: "New folder" }));
    fireEvent.input(screen.getByLabelText("Folder name"), {
      target: { value: "Biology" },
    });
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() =>
      expect(UnitsApi.createFolder).toHaveBeenCalledWith("Biology", "home"),
    );
  });

  it("closes the dialog when it is cancelled", () => {
    renderButton();

    fireEvent.click(screen.getByRole("button", { name: "New folder" }));
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(document.querySelector(".modal")).toBeNull();
  });
});
