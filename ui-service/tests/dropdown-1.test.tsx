import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import fc from "fast-check";
import { Dropdown } from "../src/shared/ui/Dropdown";
import { itemNamed } from "./dropdown-support";

describe("Dropdown", () => {
  it("lists exactly the items it was given", () => {
    fc.assert(
      fc.property(
        fc.array(fc.stringMatching(/^[A-Za-z]{1,8}$/), { maxLength: 4 }),
        (labels) => {
          const { unmount } = render(() => (
            <Dropdown
              isOpen
              items={labels.map((label) => itemNamed(label))}
              onDismiss={vi.fn()}
            />
          ));

          expect(screen.queryAllByRole("menuitem")).toHaveLength(labels.length);
          unmount();
        },
      ),
    );
  });

  it("shows nothing while it is closed", () => {
    render(() => (
      <Dropdown
        isOpen={false}
        items={[itemNamed("Edit")]}
        onDismiss={vi.fn()}
      />
    ));

    expect(screen.queryByRole("menu")).toBeNull();
  });

  it("selects the item that was pressed", () => {
    const onSelect = vi.fn();
    render(() => (
      <Dropdown
        isOpen
        items={[itemNamed("Edit", onSelect)]}
        onDismiss={vi.fn()}
      />
    ));

    fireEvent.click(screen.getByRole("menuitem", { name: "Edit" }));

    expect(onSelect).toHaveBeenCalledTimes(1);
  });

  it("marks a dangerous item as such", () => {
    render(() => (
      <Dropdown
        isOpen
        items={[{ ...itemNamed("Delete"), danger: true }]}
        onDismiss={vi.fn()}
      />
    ));

    expect(
      screen.getByRole("menuitem", { name: "Delete" }).className,
    ).toContain("is-danger");
  });

  it("leaves an ordinary item unmarked", () => {
    render(() => (
      <Dropdown isOpen items={[itemNamed("Edit")]} onDismiss={vi.fn()} />
    ));

    expect(
      screen.getByRole("menuitem", { name: "Edit" }).className,
    ).not.toContain("is-danger");
  });

  it("shows the hint an item carries", () => {
    render(() => (
      <Dropdown
        isOpen
        items={[{ ...itemNamed("Edit"), hint: "E" }]}
        onDismiss={vi.fn()}
      />
    ));

    expect(document.querySelector(".dropdown-hint")?.textContent).toBe("E");
  });

  it("shows no hint for an item that carries none", () => {
    render(() => (
      <Dropdown isOpen items={[itemNamed("Edit")]} onDismiss={vi.fn()} />
    ));

    expect(document.querySelector(".dropdown-hint")).toBeNull();
  });
});

describe("ClickAway.watch", () => {
  it("watch property listens outside only while the menu is open", () => {
    fc.assert(
      fc.property(fc.constantFrom(true, false), (isOpen) => {
        const onDismiss = vi.fn();
        const { unmount } = render(() => (
          <Dropdown
            isOpen={isOpen}
            items={[itemNamed("Edit")]}
            onDismiss={onDismiss}
          />
        ));

        fireEvent.mouseDown(document.body);

        expect(onDismiss).toHaveBeenCalledTimes(isOpen ? 1 : 0);
        unmount();
      }),
    );
  });

  it("stays open when the click lands inside the menu", () => {
    const onDismiss = vi.fn();
    render(() => (
      <Dropdown isOpen items={[itemNamed("Edit")]} onDismiss={onDismiss} />
    ));

    fireEvent.mouseDown(screen.getByRole("menuitem", { name: "Edit" }));

    expect(onDismiss).not.toHaveBeenCalled();
  });

  it("dismisses when the click lands on nothing at all", () => {
    const onDismiss = vi.fn();
    render(() => (
      <Dropdown isOpen items={[itemNamed("Edit")]} onDismiss={onDismiss} />
    ));

    document.dispatchEvent(new MouseEvent("mousedown", { bubbles: true }));

    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it("stops listening once the menu is gone", () => {
    const onDismiss = vi.fn();
    const { unmount } = render(() => (
      <Dropdown isOpen items={[itemNamed("Edit")]} onDismiss={onDismiss} />
    ));

    unmount();
    fireEvent.mouseDown(document.body);

    expect(onDismiss).not.toHaveBeenCalled();
  });
});
