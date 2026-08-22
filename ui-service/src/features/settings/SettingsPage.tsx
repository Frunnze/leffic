import {
  For,
  Match,
  Switch,
  createResource,
  createSignal,
  type JSX,
} from "solid-js";
import { AccountPanel } from "./AccountPanel";
import { AppShell } from "../../shared/ui/AppShell";
import { DeleteAccountPanel } from "./DeleteAccountPanel";
import { AccountApi } from "./account-api";
import { ProviderKeysPanel } from "./ProviderKeysPanel";
import { Theme, type ThemeChoice } from "../../shared/ui/theme";
import { ThemePanel } from "./ThemePanel";
import { useToasts } from "../../shared/notifications/ToastContext";

type SectionName = "account" | "appearance" | "keys" | "deletion";

type Section = {
  readonly name: SectionName;
  readonly label: string;
};

const SECTIONS: readonly Section[] = [
  { name: "account", label: "Account" },
  { name: "appearance", label: "Appearance" },
  { name: "keys", label: "AI provider keys" },
  { name: "deletion", label: "Delete account" },
];

export default function SettingsPage(): JSX.Element {
  const toasts = useToasts();
  const [section, setSection] = createSignal<SectionName>("account");
  const [chosenTheme, setChosenTheme] = createSignal<ThemeChoice>(
    Theme.lastPainted(),
  );
  const [account] = createResource(AccountApi.read);

  const chooseTheme = async (choice: ThemeChoice): Promise<void> => {
    setChosenTheme(choice);
    Theme.apply(choice);
    await AccountApi.chooseTheme(choice);
  };

  const announceSuccess = (message: string): void => {
    toasts.show({ tone: "success", title: message });
  };

  const announceFailure = (message: string): void => {
    toasts.show({ tone: "failure", title: message });
  };

  return (
    <AppShell>
      <div class="page">
        <div class="settings">
          <h1 class="settings-title">Settings</h1>

          <div class="settings-layout">
            <nav class="settings-nav" aria-label="Settings sections">
              <For each={SECTIONS}>
                {(entry) => (
                  <button
                    class="settings-nav-item"
                    type="button"
                    aria-current={section() === entry.name ? "page" : undefined}
                    onClick={() => setSection(entry.name)}
                  >
                    {entry.label}
                  </button>
                )}
              </For>
            </nav>

            <Switch>
              <Match when={section() === "account"}>
                <AccountPanel
                  onSaved={announceSuccess}
                  onFailed={announceFailure}
                />
              </Match>
              <Match when={section() === "appearance"}>
                <ThemePanel
                  chosen={account()?.theme ?? chosenTheme()}
                  onChoose={(choice) => void chooseTheme(choice)}
                />
              </Match>
              <Match when={section() === "keys"}>
                <ProviderKeysPanel
                  onSaved={announceSuccess}
                  onFailed={announceFailure}
                />
              </Match>
              <Match when={section() === "deletion"}>
                <DeleteAccountPanel onFailed={announceFailure} />
              </Match>
            </Switch>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
