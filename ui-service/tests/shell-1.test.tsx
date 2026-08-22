import { describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor } from "@solidjs/testing-library";
import fc from "fast-check";
import { AuthApi } from "../src/features/authentication/authentication-api";
import { Rail } from "../src/shared/ui/Rail";
import { renderAt } from "./router-support";
import { renderShell } from "./shell-support";

describe("Rail", () => {
  it("toggles the ask panel from its own button", () => {
    const onToggleAsk = vi.fn();
    renderAt("/folder/home", "/folder/:id", () => (
      <Rail onToggleAsk={onToggleAsk} />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Ask" }));

    expect(onToggleAsk).toHaveBeenCalledTimes(1);
  });

  it("links home", () => {
    renderAt("/folder/home", "/folder/:id", () => (
      <Rail onToggleAsk={vi.fn()} />
    ));

    expect(
      screen.getByRole("link", { name: "Home" }).getAttribute("href"),
    ).toBe("/folder/home");
  });

  it("opens the settings page from the profile menu", async () => {
    const { history } = renderAt("/folder/home", "/folder/:id", () => (
      <Rail onToggleAsk={vi.fn()} />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Profile" }));
    fireEvent.click(screen.getByRole("menuitem", { name: "Settings" }));

    await waitFor(() => expect(history.get()).toBe("/settings"));
  });

  it("logs out and leaves for the landing page", async () => {
    vi.spyOn(AuthApi, "logOut").mockResolvedValue(undefined);
    const { history } = renderAt("/folder/home", "/folder/:id", () => (
      <Rail onToggleAsk={vi.fn()} />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Profile" }));
    fireEvent.click(screen.getByRole("menuitem", { name: "Log out" }));

    await waitFor(() => expect(history.get()).toBe("/"));
  });

  it("closes the profile menu when the click lands away", () => {
    renderAt("/folder/home", "/folder/:id", () => (
      <Rail onToggleAsk={vi.fn()} />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Profile" }));
    fireEvent.mouseDown(document.body);

    expect(screen.queryByRole("menu")).toBeNull();
  });
});

describe("AppShell", () => {
  it("fixes the screen to the viewport only when asked to", () => {
    fc.assert(
      fc.property(fc.boolean(), (fillsViewport) => {
        const { unmount } = renderShell(fillsViewport);

        expect(
          document.querySelector(".screen")?.className.includes("screen-fixed"),
        ).toBe(fillsViewport);
        unmount();
      }),
      { numRuns: 2 },
    );
  });

  it("shows the page it wraps", () => {
    renderShell();

    expect(document.body.textContent).toContain("page body");
  });

  it("opens the ask panel beside the page", () => {
    renderShell();

    fireEvent.click(screen.getByRole("button", { name: "Ask" }));

    expect(screen.getByRole("complementary", { name: "Ask" })).toBeTruthy();
    expect(document.querySelector(".screen")?.className).toContain(
      "screen-with-chat",
    );
  });

  it("closes the ask panel from inside it", () => {
    renderShell();

    fireEvent.click(screen.getByRole("button", { name: "Ask" }));
    fireEvent.click(screen.getByRole("button", { name: "Close Ask" }));

    expect(screen.queryByRole("complementary", { name: "Ask" })).toBeNull();
  });
});
