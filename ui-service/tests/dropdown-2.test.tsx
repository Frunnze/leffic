import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import fc from "fast-check";
import { CardMenu } from "../src/shared/ui/CardMenu";
import { itemNamed } from "./dropdown-support";

describe("CardMenu", () => {
  it("names its own button whatever it was told to", () => {
    fc.assert(
      fc.property(fc.stringMatching(/^[A-Za-z]{1,10}$/), (label) => {
        const { unmount } = render(() => (
          <CardMenu label={label} items={[itemNamed("Edit")]} />
        ));

        expect(screen.getByRole("button", { name: label })).toBeTruthy();
        unmount();
      }),
    );
  });

  it("starts closed and opens when pressed", () => {
    render(() => <CardMenu label="Actions" items={[itemNamed("Edit")]} />);

    expect(screen.queryByRole("menu")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Actions" }));

    expect(screen.getByRole("menu")).toBeTruthy();
  });

  it("closes itself when an item is chosen", () => {
    const onSelect = vi.fn();
    render(() => (
      <CardMenu label="Actions" items={[itemNamed("Edit", onSelect)]} />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Actions" }));
    fireEvent.click(screen.getByRole("menuitem", { name: "Edit" }));

    expect(onSelect).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole("menu")).toBeNull();
  });

  it("closes when the click lands away from it", () => {
    render(() => <CardMenu label="Actions" items={[itemNamed("Edit")]} />);

    fireEvent.click(screen.getByRole("button", { name: "Actions" }));
    fireEvent.mouseDown(document.body);

    expect(screen.queryByRole("menu")).toBeNull();
  });
});
