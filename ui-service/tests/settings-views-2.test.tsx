import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@solidjs/testing-library";
import { AccountApi } from "../src/features/settings/account-api";
import {
  DeleteAccountPanel,
} from "../src/features/settings/DeleteAccountPanel";
import { ProviderKeyBlock } from "../src/features/settings/ProviderKeyBlock";
import { Session } from "../src/shared/api/session";
import { renderAt } from "./router-support";
import {
  OPENAI,
  SAVED_KEY,
  submitDialog,
  typeInto,
} from "./settings-views-support";

describe("DeleteAccountPanel", () => {
  it("deletes the account and leaves for the landing page", async () => {
    const deleting = vi
      .spyOn(AccountApi, "deleteAccount")
      .mockResolvedValue(undefined);
    Session.store("token");
    const { history } = renderAt("/settings", "/settings", () => (
      <DeleteAccountPanel onFailed={vi.fn()} />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Delete account" }));
    typeInto("Enter your password to confirm", "secret");
    submitDialog();

    await waitFor(() => expect(history.get()).toBe("/"));
    expect(deleting).toHaveBeenCalledWith("secret");
    expect(Session.currentToken()).toBeNull();
  });

  it("reports an account that could not be deleted", async () => {
    vi.spyOn(AccountApi, "deleteAccount").mockRejectedValue(new Error("no"));
    const onFailed = vi.fn();
    renderAt("/settings", "/settings", () => (
      <DeleteAccountPanel onFailed={onFailed} />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Delete account" }));
    typeInto("Enter your password to confirm", "secret");
    submitDialog();

    await waitFor(() =>
      expect(onFailed).toHaveBeenCalledWith(
        "That account could not be deleted.",
      ),
    );
  });

  it("closes the confirmation when it is cancelled", () => {
    renderAt("/settings", "/settings", () => (
      <DeleteAccountPanel onFailed={vi.fn()} />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Delete account" }));
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(document.querySelector(".modal")).toBeNull();
  });
});

describe("ProviderKeyBlock", () => {
  it("takes a new key and its limit", () => {
    const onSave = vi.fn();
    render(() => (
      <ProviderKeyBlock
        provider={OPENAI}
        savedKey={undefined}
        onSave={onSave}
        onRemove={vi.fn()}
      />
    ));

    typeInto("OpenAI key", " sk-123 ");
    typeInto("Monthly limit", "20");
    fireEvent.click(screen.getByRole("button", { name: "Save key" }));

    expect(onSave).toHaveBeenCalledWith("sk-123", 2000);
  });

  it("blocks saving before a key is pasted", () => {
    render(() => (
      <ProviderKeyBlock
        provider={OPENAI}
        savedKey={undefined}
        onSave={vi.fn()}
        onRemove={vi.fn()}
      />
    ));

    expect(screen.getByRole("button", { name: "Save key" })).toHaveProperty(
      "disabled",
      true,
    );
    expect(document.querySelector(".key-usage")?.textContent).toBe(
      "Nothing spent yet.",
    );
  });

  it("seals a saved key behind its hint", () => {
    render(() => (
      <ProviderKeyBlock
        provider={OPENAI}
        savedKey={{ ...SAVED_KEY, spentCents: 125 }}
        onSave={vi.fn()}
        onRemove={vi.fn()}
      />
    ));

    expect(screen.getByLabelText("OpenAI key")).toHaveProperty("value", "…7f");
    expect(screen.getByLabelText("Monthly limit")).toHaveProperty(
      "value",
      "20.00",
    );
    expect(document.querySelector(".key-usage")?.textContent).toContain(
      "$1.25 used this month",
    );
  });

  it("shows no hint for a key stored without one", () => {
    render(() => (
      <ProviderKeyBlock
        provider={OPENAI}
        savedKey={{ ...SAVED_KEY, hint: "", monthlyLimitCents: null }}
        onSave={vi.fn()}
        onRemove={vi.fn()}
      />
    ));

    expect(screen.getByLabelText("OpenAI key")).toHaveProperty("value", "…");
    expect(screen.getByLabelText("Monthly limit")).toHaveProperty("value", "");
  });

  it("replaces a sealed key", () => {
    render(() => (
      <ProviderKeyBlock
        provider={OPENAI}
        savedKey={SAVED_KEY}
        onSave={vi.fn()}
        onRemove={vi.fn()}
      />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Replace" }));

    expect(screen.getByRole("button", { name: "Save key" })).toBeTruthy();
  });

  it("removes a sealed key", () => {
    const onRemove = vi.fn();
    render(() => (
      <ProviderKeyBlock
        provider={OPENAI}
        savedKey={SAVED_KEY}
        onSave={vi.fn()}
        onRemove={onRemove}
      />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Remove" }));

    expect(onRemove).toHaveBeenCalledTimes(1);
  });
});
