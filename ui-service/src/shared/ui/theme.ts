import { createSignal, type Accessor } from "solid-js";

export type ThemeChoice = "system" | "light" | "dark";

const REMEMBERED_THEME = "leffic-theme";
const SYSTEM_THEME: ThemeChoice = "system";

const rememberedTheme = localStorage.getItem(REMEMBERED_THEME);
const [paintedTheme, setPaintedTheme] = createSignal<ThemeChoice>(
  rememberedTheme === "light" || rememberedTheme === "dark"
    ? rememberedTheme
    : SYSTEM_THEME,
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

  static readonly painted: Accessor<ThemeChoice> = paintedTheme;

  static lastPainted(): ThemeChoice {
    return Theme.asChoice(localStorage.getItem(REMEMBERED_THEME));
  }

  static asChoice(value: unknown): ThemeChoice {
    if (value === "light" || value === "dark") return value;

    return SYSTEM_THEME;
  }
}
