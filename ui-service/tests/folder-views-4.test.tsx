import { describe, expect, it, vi } from "vitest";
import { fireEvent, screen } from "@solidjs/testing-library";
import { UnitRow } from "../src/features/folder/UnitRow";
import { unitOf } from "./unit-factories";
import { renderAt } from "./router-support";
import "./folder-views-support";

describe("UnitRow", () => {
  const note = unitOf({ id: "7", name: "Cells", type: "note", meta: "3 min" });

  it("links to the unit and shows what it carries", () => {
    renderAt("/folder/home", "/folder/:id", () => (
      <UnitRow
        unit={unitOf({ ...note, dueCount: 4 })}
        onDelete={vi.fn()}
        onRename={vi.fn()}
        onMove={vi.fn()}
        destinations={[]}
      />
    ));

    expect(document.querySelector(".unit-link")?.getAttribute("href")).toBe(
      "/note/7",
    );
    expect(document.querySelector(".unit-meta")?.textContent).toBe("3 min");
    expect(document.querySelector(".unit-badge")?.textContent).toBe("4 due");
  });

  it("shows neither meta nor badge when the unit carries none", () => {
    renderAt("/folder/home", "/folder/:id", () => (
      <UnitRow
        unit={unitOf({ id: "8", name: "Plain", type: "note" })}
        onDelete={vi.fn()}
        onRename={vi.fn()}
        onMove={vi.fn()}
        destinations={[]}
      />
    ));

    expect(document.querySelector(".unit-meta")).toBeNull();
    expect(document.querySelector(".unit-badge")).toBeNull();
  });

  it("deletes the unit from its own menu", () => {
    const onDelete = vi.fn();
    renderAt("/folder/home", "/folder/:id", () => (
      <UnitRow
        unit={note}
        onDelete={onDelete}
        onRename={vi.fn()}
        onMove={vi.fn()}
        destinations={[]}
      />
    ));

    fireEvent.click(
      screen.getByRole("button", { name: "More actions for Cells" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Delete" }));

    expect(onDelete).toHaveBeenCalledWith(note);
  });

  it("renames the unit through the prompt dialog", () => {
    const onRename = vi.fn();
    renderAt("/folder/home", "/folder/:id", () => (
      <UnitRow
        unit={note}
        onDelete={vi.fn()}
        onRename={onRename}
        onMove={vi.fn()}
        destinations={[]}
      />
    ));

    fireEvent.click(
      screen.getByRole("button", { name: "More actions for Cells" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Rename" }));
    fireEvent.input(screen.getByLabelText("Name"), {
      target: { value: "Mitosis" },
    });
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(onRename).toHaveBeenCalledWith(note, "Mitosis");
  });

  it("closes the rename dialog when it is cancelled", () => {
    renderAt("/folder/home", "/folder/:id", () => (
      <UnitRow
        unit={note}
        onDelete={vi.fn()}
        onRename={vi.fn()}
        onMove={vi.fn()}
        destinations={[]}
      />
    ));

    fireEvent.click(
      screen.getByRole("button", { name: "More actions for Cells" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Rename" }));
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(document.querySelector(".modal")).toBeNull();
  });

  it("moves the unit through the move dialog", () => {
    const onMove = vi.fn();
    renderAt("/folder/home", "/folder/:id", () => (
      <UnitRow
        unit={note}
        onDelete={vi.fn()}
        onRename={vi.fn()}
        onMove={onMove}
        destinations={[{ id: "home", name: "Home" }]}
      />
    ));

    fireEvent.click(
      screen.getByRole("button", { name: "More actions for Cells" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Move to folder" }));
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(onMove).toHaveBeenCalledWith(note, "home");
  });

  it("closes its own menu when the click lands away", () => {
    renderAt("/folder/home", "/folder/:id", () => (
      <UnitRow
        unit={note}
        onDelete={vi.fn()}
        onRename={vi.fn()}
        onMove={vi.fn()}
        destinations={[]}
      />
    ));

    fireEvent.click(
      screen.getByRole("button", { name: "More actions for Cells" }),
    );
    fireEvent.mouseDown(document.body);

    expect(screen.queryByRole("menu")).toBeNull();
  });

  it("closes the move dialog when it is cancelled", () => {
    renderAt("/folder/home", "/folder/:id", () => (
      <UnitRow
        unit={note}
        onDelete={vi.fn()}
        onRename={vi.fn()}
        onMove={vi.fn()}
        destinations={[{ id: "home", name: "Home" }]}
      />
    ));

    fireEvent.click(
      screen.getByRole("button", { name: "More actions for Cells" }),
    );
    fireEvent.click(screen.getByRole("menuitem", { name: "Move to folder" }));
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(document.querySelector(".modal")).toBeNull();
  });
});
