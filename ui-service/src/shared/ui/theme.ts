import { createSignal } from "solid-js";

export type ThemeChoice = "system" | "light" | "dark";

const REMEMBERED_THEME = "leffic-theme";
const SYSTEM_THEME: ThemeChoice = "system";

export function asThemeChoice(value: unknown): ThemeChoice {
  if (value === "light" || value === "dark") return value;

  return SYSTEM_THEME;
}

const [paintedTheme, setPaintedTheme] = createSignal<ThemeChoice>(
  asThemeChoice(localStorage.getItem(REMEMBERED_THEME)),
);

export class Theme {
  private static pulledFromAccount: Promise<void> | null = null;

  static followAccount(read: () => Promise<ThemeChoice>): void {
    Theme.pulledFromAccount ??= read().then(Theme.apply);
  }

  static apply(choice: ThemeChoice): void {
    if (choice === SYSTEM_THEME) {
      delete document.documentElement.dataset.theme;
    } else {
      document.documentElement.dataset.theme = choice;
    }

    localStorage.setItem(REMEMBERED_THEME, choice);
    setPaintedTheme(choice);
  }

  static lastPainted(): ThemeChoice {
    return paintedTheme();
  }
}
