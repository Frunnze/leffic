import { afterEach, vi } from "vitest";
import { Toasts } from "../src/shared/notifications/Toasts";
import { useToasts } from "../src/shared/notifications/ToastContext";

export const NO_TASKS = {
  flashcardsTaskIds: [],
  noteTaskId: null,
  testTaskIds: [],
};

export function FlowToasts(): import("solid-js").JSX.Element {
  const toasts = useToasts();

  return <Toasts toasts={toasts.toasts()} onDismiss={toasts.dismiss} />;
}

export function toastTitles(): readonly string[] {
  return [...document.querySelectorAll(".toast-title")].map(
    (title) => title.textContent ?? "",
  );
}

afterEach(() => {
  vi.restoreAllMocks();
});
