import { afterEach, vi } from "vitest";
import { fireEvent, screen } from "@solidjs/testing-library";
import { Session } from "../src/shared/api/session";
import { Toasts } from "../src/shared/notifications/Toasts";
import { useToasts } from "../src/shared/notifications/ToastContext";

export function SettingsToasts(): import("solid-js").JSX.Element {
  const toasts = useToasts();

  return <Toasts toasts={toasts.toasts()} onDismiss={toasts.dismiss} />;
}

export const OPENAI = { id: "openai", name: "OpenAI" };
export const SAVED_KEY = {
  provider: "openai",
  hint: "7f",
  monthlyLimitCents: 2000,
  spentCents: 0,
};

export function typeInto(label: string, value: string): void {
  fireEvent.input(screen.getByLabelText(label), { target: { value } });
}

export function submitDialog(): void {
  fireEvent.submit(document.querySelector("form") as HTMLFormElement);
}

afterEach(() => {
  vi.restoreAllMocks();
  Session.store(null);
});
