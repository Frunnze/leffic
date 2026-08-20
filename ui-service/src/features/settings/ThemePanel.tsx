import { For, type JSX } from "solid-js";
import type { ThemeChoice } from "../../shared/ui/theme";

type ThemeOption = {
  readonly choice: ThemeChoice;
  readonly label: string;
};

const THEME_OPTIONS: readonly ThemeOption[] = [
  { choice: "system", label: "System" },
  { choice: "light", label: "Light" },
  { choice: "dark", label: "Dark" },
];

export type ThemePanelProps = {
  readonly chosen: ThemeChoice;
  readonly onChoose: (choice: ThemeChoice) => void;
};

export function ThemePanel(props: ThemePanelProps): JSX.Element {
  return (
    <section class="settings-panel">
      <h2 class="settings-panel-title">Appearance</h2>
      <p class="settings-panel-text">
        Kept with your account, so it follows you to every device.
      </p>

      <div class="segmented">
        <For each={THEME_OPTIONS}>
          {(option) => (
            <label class="segment">
              <input
                type="radio"
                name="theme"
                checked={props.chosen === option.choice}
                onChange={() => props.onChoose(option.choice)}
              />
              <span class="segment-face">{option.label}</span>
            </label>
          )}
        </For>
      </div>
    </section>
  );
}
