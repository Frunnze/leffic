export type ThemeChoice = "system" | "light" | "dark";

const REMEMBERED_THEME = "leffic-theme";
const SYSTEM_THEME: ThemeChoice = "system";

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
  }

  static lastPainted(): ThemeChoice {
    const remembered = localStorage.getItem(REMEMBERED_THEME);

    if (remembered === "light" || remembered === "dark") return remembered;

    return SYSTEM_THEME;
  }

  static asChoice(value: unknown): ThemeChoice {
    if (value === "light" || value === "dark") return value;

    return SYSTEM_THEME;
  }
}
