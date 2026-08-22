import { describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor } from "@solidjs/testing-library";
import { AccountApi } from "../src/features/settings/account-api";
import { ProviderKeysPanel } from "../src/features/settings/ProviderKeysPanel";
import { renderAt } from "./router-support";
import { SAVED_KEY, submitDialog, typeInto } from "./settings-views-support";

describe("ProviderKeysPanel", () => {
  function renderPanel(onSaved = vi.fn(), onFailed = vi.fn()): void {
    renderAt("/settings", "/settings", () => (
      <ProviderKeysPanel onSaved={onSaved} onFailed={onFailed} />
    ));
  }

  it("seals a pasted key behind the account password", async () => {
    vi.spyOn(AccountApi, "providerKeys").mockResolvedValue([]);
    const saving = vi
      .spyOn(AccountApi, "saveProviderKey")
      .mockResolvedValue(undefined);
    const onSaved = vi.fn();
    renderPanel(onSaved);

    await waitFor(() => screen.getByLabelText("OpenAI key"));
    typeInto("OpenAI key", "sk-123");
    fireEvent.click(
      screen.getAllByRole("button", { name: "Save key" })[0] as HTMLElement,
    );
    typeInto("Password", "secret");
    submitDialog();

    await waitFor(() =>
      expect(saving).toHaveBeenCalledWith({
        provider: "openai",
        key: "sk-123",
        monthlyLimitCents: null,
        password: "secret",
      }),
    );
    expect(onSaved).toHaveBeenCalledWith("Key sealed with your password.");
  });

  it("reports a key that could not be saved", async () => {
    vi.spyOn(AccountApi, "providerKeys").mockResolvedValue([]);
    vi.spyOn(AccountApi, "saveProviderKey").mockRejectedValue(new Error("no"));
    const onFailed = vi.fn();
    renderPanel(vi.fn(), onFailed);

    await waitFor(() => screen.getByLabelText("OpenAI key"));
    typeInto("OpenAI key", "sk-123");
    fireEvent.click(
      screen.getAllByRole("button", { name: "Save key" })[0] as HTMLElement,
    );
    typeInto("Password", "secret");
    submitDialog();

    await waitFor(() =>
      expect(onFailed).toHaveBeenCalledWith("That key could not be saved."),
    );
  });

  it("forgets the pending key when the password prompt is cancelled", async () => {
    vi.spyOn(AccountApi, "providerKeys").mockResolvedValue([]);
    const saving = vi.spyOn(AccountApi, "saveProviderKey");
    renderPanel();

    await waitFor(() => screen.getByLabelText("OpenAI key"));
    typeInto("OpenAI key", "sk-123");
    fireEvent.click(
      screen.getAllByRole("button", { name: "Save key" })[0] as HTMLElement,
    );
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(saving).not.toHaveBeenCalled();
  });

  it("removes a saved key", async () => {
    vi.spyOn(AccountApi, "providerKeys").mockResolvedValue([SAVED_KEY]);
    const removing = vi
      .spyOn(AccountApi, "removeProviderKey")
      .mockResolvedValue(undefined);
    const onSaved = vi.fn();
    renderPanel(onSaved);

    await waitFor(() => screen.getByRole("button", { name: "Remove" }));
    fireEvent.click(screen.getByRole("button", { name: "Remove" }));

    await waitFor(() => expect(removing).toHaveBeenCalledWith("openai"));
    expect(onSaved).toHaveBeenCalledWith("Key removed.");
  });

  it("reports a key that could not be removed", async () => {
    vi.spyOn(AccountApi, "providerKeys").mockResolvedValue([SAVED_KEY]);
    vi.spyOn(AccountApi, "removeProviderKey").mockRejectedValue(
      new Error("no"),
    );
    const onFailed = vi.fn();
    renderPanel(vi.fn(), onFailed);

    await waitFor(() => screen.getByRole("button", { name: "Remove" }));
    fireEvent.click(screen.getByRole("button", { name: "Remove" }));

    await waitFor(() =>
      expect(onFailed).toHaveBeenCalledWith("That key could not be removed."),
    );
  });

  it("shows no saved key before the list arrives", () => {
    vi.spyOn(AccountApi, "providerKeys").mockImplementation(
      () => new Promise(() => undefined),
    );
    renderPanel();

    expect(screen.queryByRole("button", { name: "Remove" })).toBeNull();
  });
});
