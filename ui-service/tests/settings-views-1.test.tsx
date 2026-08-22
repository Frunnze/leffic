import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@solidjs/testing-library";
import fc from "fast-check";
import { AccountApi } from "../src/features/settings/account-api";
import { AccountPanel } from "../src/features/settings/AccountPanel";
import { ThemePanel } from "../src/features/settings/ThemePanel";
import type { ThemeChoice } from "../src/shared/ui/theme";
import { typeInto } from "./settings-views-support";

describe("ThemePanel", () => {
  it("marks the theme already chosen", () => {
    fc.assert(
      fc.property(
        fc.constantFrom<ThemeChoice>("system", "light", "dark"),
        (chosen) => {
          const { unmount } = render(() => (
            <ThemePanel chosen={chosen} onChoose={vi.fn()} />
          ));
          const labels = { system: "System", light: "Light", dark: "Dark" };

          expect(screen.getByLabelText(labels[chosen])).toHaveProperty(
            "checked",
            true,
          );
          unmount();
        },
      ),
    );
  });

  it("reports the theme that was picked", () => {
    const onChoose = vi.fn();
    render(() => <ThemePanel chosen="system" onChoose={onChoose} />);

    fireEvent.change(screen.getByLabelText("Dark"));

    expect(onChoose).toHaveBeenCalledWith("dark");
  });
});

describe("AccountPanel", () => {
  function renderPanel(onSaved = vi.fn(), onFailed = vi.fn()): void {
    render(() => <AccountPanel onSaved={onSaved} onFailed={onFailed} />);
  }

  it("shows the username the account holds", async () => {
    vi.spyOn(AccountApi, "read").mockResolvedValue({
      username: "learner",
      email: "learner@example.test",
      theme: "system",
    });
    renderPanel();

    await waitFor(() =>
      expect(screen.getByLabelText("Username")).toHaveProperty(
        "value",
        "learner",
      ),
    );
  });

  it("shows an empty username before the account loads", () => {
    vi.spyOn(AccountApi, "read").mockImplementation(
      () => new Promise(() => undefined),
    );
    renderPanel();

    expect(screen.getByLabelText("Username")).toHaveProperty("value", "");
    expect(screen.getByRole("button", { name: "Save changes" })).toHaveProperty(
      "disabled",
      true,
    );
  });

  it("saves the username that was typed", async () => {
    vi.spyOn(AccountApi, "read").mockResolvedValue({
      username: "learner",
      email: "e",
      theme: "system",
    });
    const changing = vi
      .spyOn(AccountApi, "changeUsername")
      .mockResolvedValue(undefined);
    const onSaved = vi.fn();
    renderPanel(onSaved);

    await waitFor(() => screen.getByLabelText("Username"));
    typeInto("Username", " scholar ");
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));

    await waitFor(() => expect(changing).toHaveBeenCalledWith("scholar"));
    expect(onSaved).toHaveBeenCalledWith("Username saved.");
  });

  it("reports a username that could not be saved", async () => {
    vi.spyOn(AccountApi, "read").mockResolvedValue({
      username: "learner",
      email: "e",
      theme: "system",
    });
    vi.spyOn(AccountApi, "changeUsername").mockRejectedValue(new Error("no"));
    const onFailed = vi.fn();
    renderPanel(vi.fn(), onFailed);

    await waitFor(() => screen.getByLabelText("Username"));
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));

    await waitFor(() =>
      expect(onFailed).toHaveBeenCalledWith(
        "That username could not be saved.",
      ),
    );
  });

  it("changes the password and closes the form", async () => {
    vi.spyOn(AccountApi, "read").mockResolvedValue({
      username: "learner",
      email: "e",
      theme: "system",
    });
    const changing = vi
      .spyOn(AccountApi, "changePassword")
      .mockResolvedValue(undefined);
    const onSaved = vi.fn();
    renderPanel(onSaved);

    fireEvent.click(screen.getByRole("button", { name: "Change password" }));
    typeInto("Current password", "old");
    typeInto("New password", "new");
    fireEvent.click(screen.getByRole("button", { name: "Save password" }));

    await waitFor(() => expect(changing).toHaveBeenCalledWith("old", "new"));
    expect(onSaved).toHaveBeenCalledWith("Password changed.");
    expect(
      screen.getByRole("button", { name: "Change password" }),
    ).toBeTruthy();
  });

  it("reports a password that could not be changed", async () => {
    vi.spyOn(AccountApi, "read").mockResolvedValue({
      username: "learner",
      email: "e",
      theme: "system",
    });
    vi.spyOn(AccountApi, "changePassword").mockRejectedValue(new Error("no"));
    const onFailed = vi.fn();
    renderPanel(vi.fn(), onFailed);

    fireEvent.click(screen.getByRole("button", { name: "Change password" }));
    typeInto("New password", "new");
    fireEvent.click(screen.getByRole("button", { name: "Save password" }));

    await waitFor(() =>
      expect(onFailed).toHaveBeenCalledWith(
        "That password could not be changed.",
      ),
    );
  });

  it("blocks saving an empty new password", () => {
    vi.spyOn(AccountApi, "read").mockImplementation(
      () => new Promise(() => undefined),
    );
    renderPanel();

    fireEvent.click(screen.getByRole("button", { name: "Change password" }));

    expect(
      screen.getByRole("button", { name: "Save password" }),
    ).toHaveProperty("disabled", true);
  });

  it("closes the password form when it is cancelled", () => {
    vi.spyOn(AccountApi, "read").mockImplementation(
      () => new Promise(() => undefined),
    );
    renderPanel();

    fireEvent.click(screen.getByRole("button", { name: "Change password" }));
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(screen.queryByLabelText("New password")).toBeNull();
  });
});
