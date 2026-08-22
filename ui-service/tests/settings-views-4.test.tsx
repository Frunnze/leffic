import { describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor } from "@solidjs/testing-library";
import { AccountApi } from "../src/features/settings/account-api";
import { AskProvider } from "../src/shared/chatbot/AskContext";
import SettingsPage from "../src/features/settings/SettingsPage";
import { ToastProvider } from "../src/shared/notifications/ToastContext";
import { renderAt } from "./router-support";
import { SettingsToasts } from "./settings-views-support";

describe("SettingsPage", () => {
  function renderSettings(): void {
    vi.spyOn(AccountApi, "read").mockResolvedValue({
      username: "learner",
      email: "learner@example.test",
      theme: "dark",
    });
    vi.spyOn(AccountApi, "providerKeys").mockResolvedValue([]);
    renderAt("/settings", "/settings", () => (
      <ToastProvider>
        <AskProvider>
          <SettingsPage />
          <SettingsToasts />
        </AskProvider>
      </ToastProvider>
    ));
  }

  it("opens on the account section", async () => {
    renderSettings();

    await waitFor(() => expect(screen.getByLabelText("Username")).toBeTruthy());
    expect(
      screen
        .getByRole("button", { name: "Account" })
        .getAttribute("aria-current"),
    ).toBe("page");
  });

  it("chooses a theme and remembers it on the account", async () => {
    const choosing = vi
      .spyOn(AccountApi, "chooseTheme")
      .mockResolvedValue("light");
    renderSettings();

    fireEvent.click(screen.getByRole("button", { name: "Appearance" }));
    await waitFor(() => screen.getByLabelText("Light"));
    fireEvent.change(screen.getByLabelText("Light"));

    await waitFor(() => expect(choosing).toHaveBeenCalledWith("light"));
  });

  it("announces a saved username", async () => {
    vi.spyOn(AccountApi, "changeUsername").mockResolvedValue(undefined);
    renderSettings();

    await waitFor(() => screen.getByLabelText("Username"));
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));

    await waitFor(() =>
      expect(document.querySelector(".toast-title")?.textContent).toBe(
        "Username saved.",
      ),
    );
  });

  it("announces a username that could not be saved", async () => {
    vi.spyOn(AccountApi, "changeUsername").mockRejectedValue(new Error("no"));
    renderSettings();

    await waitFor(() => screen.getByLabelText("Username"));
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));

    await waitFor(() =>
      expect(document.querySelector(".toast-title")?.textContent).toBe(
        "That username could not be saved.",
      ),
    );
  });

  it("opens the provider keys section", async () => {
    renderSettings();

    fireEvent.click(screen.getByRole("button", { name: "AI provider keys" }));

    await waitFor(() =>
      expect(screen.getByLabelText("OpenAI key")).toBeTruthy(),
    );
  });

  it("opens the deletion section", async () => {
    renderSettings();

    fireEvent.click(screen.getByRole("button", { name: "Delete account" }));

    await waitFor(() =>
      expect(document.querySelector(".settings-card-title")?.textContent).toBe(
        "Delete account",
      ),
    );
  });
});
