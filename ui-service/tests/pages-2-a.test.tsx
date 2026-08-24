import { describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor } from "@solidjs/testing-library";
import { AskProvider } from "../src/shared/chatbot/AskContext";
import FolderPage from "../src/features/folder/FolderPage";
import { GenerationProvider } from "../src/features/folder/import/GenerationContext";
import { GenerationApi } from "../src/features/folder/import/generation-api";
import { StatsApi } from "../src/features/folder/stats-api";
import { ToastProvider } from "../src/shared/notifications/ToastContext";
import { UnitsApi } from "../src/features/folder/units-api";
import { unitOf } from "./unit-factories";
import { pdfFile } from "./import-factories";
import { renderAt } from "./router-support";
import { NOTHING_DUE, stubAccount } from "./pages-support";

describe("FolderPage", () => {
  function renderFolder(breakdown = NOTHING_DUE): ReturnType<typeof renderAt> {
    stubAccount();
    vi.spyOn(StatsApi, "dueBreakdown").mockResolvedValue(breakdown);

    return renderAt("/folder/home", "/folder/:id", () => (
      <ToastProvider>
        <GenerationProvider>
          <AskProvider>
            <FolderPage />
          </AskProvider>
        </GenerationProvider>
      </ToastProvider>
    ));
  }

  it("stands in for the list while the folder loads", () => {
    vi.spyOn(UnitsApi, "folderContent").mockImplementation(
      () => new Promise(() => undefined),
    );
    renderFolder();

    expect(document.querySelector(".skeleton-list")).toBeTruthy();
    expect(document.querySelector(".folder-name")?.textContent).toBe("Home");
    expect(document.querySelector("#items-heading")?.textContent).toBe(
      "0 items",
    );
  });

  it("invites an import into an empty folder", async () => {
    vi.spyOn(UnitsApi, "folderContent").mockResolvedValue({
      parentFolderName: "Biology",
      units: [],
    });
    renderFolder();

    await waitFor(() =>
      expect(document.querySelector(".state-title")?.textContent).toBe(
        "Nothing here yet",
      ),
    );
    expect(document.querySelector(".folder-name")?.textContent).toBe("Biology");
  });

  it("lists the units the folder holds", async () => {
    vi.spyOn(UnitsApi, "folderContent").mockResolvedValue({
      parentFolderName: "Biology",
      units: [unitOf({ id: "1", name: "Cells", type: "note" })],
    });
    renderFolder();

    await waitFor(() =>
      expect(document.querySelector(".unit-name")?.textContent).toBe("Cells"),
    );
    expect(document.querySelector("#items-heading")?.textContent).toBe(
      "1 item",
    );
  });

  it("opens the import flow from the toolbar", async () => {
    vi.spyOn(UnitsApi, "folderContent").mockResolvedValue({
      parentFolderName: "Biology",
      units: [unitOf({ id: "1", name: "Cells", type: "note" })],
    });
    renderFolder();

    await waitFor(() => screen.getByRole("button", { name: "Import" }));
    fireEvent.click(screen.getByRole("button", { name: "Import" }));

    expect(document.querySelector(".modal")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(document.querySelector(".modal")).toBeNull();
  });

  it("opens the import flow from the empty state", async () => {
    vi.spyOn(UnitsApi, "folderContent").mockResolvedValue({
      parentFolderName: "Biology",
      units: [],
    });
    renderFolder();

    await waitFor(() => screen.getByRole("button", { name: "Import" }));
    fireEvent.click(screen.getByRole("button", { name: "Import" }));

    expect(document.querySelector(".modal")).toBeTruthy();
  });

  it("adds a created folder to the top of the list", async () => {
    vi.spyOn(UnitsApi, "folderContent").mockResolvedValue({
      parentFolderName: "Biology",
      units: [unitOf({ id: "old", name: "Older", type: "note" })],
    });
    const created = unitOf({
      id: "new",
      name: "Cells",
      type: "folder",
      createdAt: "2030-01-01T00:00:00.000Z",
    });
    vi.spyOn(UnitsApi, "createFolder").mockResolvedValue(created);
    renderFolder();

    await waitFor(() => screen.getByRole("button", { name: "New folder" }));
    fireEvent.click(screen.getByRole("button", { name: "New folder" }));
    fireEvent.input(screen.getByLabelText("Folder name"), {
      target: { value: "Cells" },
    });
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() =>
      expect(document.querySelector(".unit-name")?.textContent).toBe("Cells"),
    );
    expect(document.body.textContent).toContain("Older");
  });

  it("ignores a unit added to another folder", async () => {
    vi.spyOn(UnitsApi, "folderContent").mockImplementation(
      () => new Promise(() => undefined),
    );
    vi.spyOn(UnitsApi, "createFolder").mockResolvedValue(
      unitOf({ id: "new", name: "Cells", type: "folder" }),
    );
    renderFolder();

    fireEvent.click(screen.getByRole("button", { name: "New folder" }));
    fireEvent.input(screen.getByLabelText("Folder name"), {
      target: { value: "Cells" },
    });
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() => expect(UnitsApi.createFolder).toHaveBeenCalledTimes(1));
    expect(document.querySelector(".unit-name")).toBeNull();
  });

  it("does not add an upload after leaving its target folder", async () => {
    vi.spyOn(UnitsApi, "folderContent").mockResolvedValue({
      parentFolderName: "Biology",
      units: [unitOf({ id: "1", name: "Cells", type: "note" })],
    });
    const upload = Promise.withResolvers<
      readonly {
        readonly fileId: string;
        readonly name: string;
        readonly extension: string;
        readonly createdAt: string;
      }[]
    >();
    vi.spyOn(GenerationApi, "uploadFile").mockReturnValue(upload.promise);
    const { history } = renderFolder();

    await waitFor(() => screen.getByRole("button", { name: "Import" }));
    fireEvent.click(screen.getByRole("button", { name: "Import" }));
    const input = document.querySelector("#import-file") as HTMLInputElement;
    Object.defineProperty(input, "files", {
      value: [pdfFile()],
      writable: true,
    });
    fireEvent.change(input);
    fireEvent.click(screen.getByRole("button", { name: "Upload only" }));
    await waitFor(() => expect(GenerationApi.uploadFile).toHaveBeenCalled());

    history.set({ value: "/folder/other" });
    upload.resolve([
      {
        fileId: "uploaded",
        name: "Uploaded.pdf",
        extension: "pdf",
        createdAt: "now",
      },
    ]);

    await waitFor(() => expect(history.get()).toBe("/folder/other"));
    expect(document.body.textContent).not.toContain("Uploaded.pdf");
  });
});
