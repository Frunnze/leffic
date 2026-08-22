import { afterEach, vi } from "vitest";
import { AccountApi } from "../src/features/settings/account-api";
import { AppShell } from "../src/shared/ui/AppShell";
import { AskProvider, useAsk } from "../src/shared/chatbot/AskContext";
import { renderAt } from "./router-support";

afterEach(() => {
  vi.restoreAllMocks();
});

export function renderShell(
  fillsViewport = false,
): ReturnType<typeof renderAt> {
  vi.spyOn(AccountApi, "read").mockResolvedValue({
    username: "learner",
    email: "learner@example.test",
    theme: "system",
  });

  return renderAt("/folder/home", "/folder/:id", () => (
    <AskProvider>
      <AppShell fillsViewport={fillsViewport}>
        <p>page body</p>
      </AppShell>
    </AskProvider>
  ));
}

export function AskRaiser(): import("solid-js").JSX.Element {
  const ask = useAsk();

  return (
    <button
      type="button"
      onClick={() => {
        ask.askAbout({
          question: "the long prompt",
          shownAs: "Mnemonic for: Front",
        });
      }}
    >
      raise
    </button>
  );
}
