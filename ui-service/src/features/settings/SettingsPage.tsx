import { For, Show, createSignal, type JSX } from "solid-js";
import { AccountPanel } from "./AccountPanel";
import { AppShell } from "../../shared/ui/AppShell";
import { DeleteAccountPanel } from "./DeleteAccountPanel";
import { ProviderKeysPanel } from "./ProviderKeysPanel";
import { Theme, type ThemeChoice } from "../../shared/ui/theme";
import { ThemePanel } from "./ThemePanel";
import { useToasts } from "../../shared/notifications/ToastContext";

type SectionName = "account" | "appearance" | "keys" | "deletion";

type Section = {
  readonly name: SectionName;
  readonly label: string;
  readonly panel: () => JSX.Element;
};

type ThemeKeepingAccount = {
  chooseTheme(theme: ThemeChoice): Promise<ThemeChoice>;
};

type SettingsPageProps = {
  readonly account: ThemeKeepingAccount;
};

export default function SettingsPage(
  props: SettingsPageProps,
): JSX.Element {
  const toasts = useToasts();
  const [section, setSection] = createSignal<SectionName>("account");

  const chooseTheme = async (choice: ThemeChoice): Promise<void> => {
    Theme.apply(choice);
    await props.account.chooseTheme(choice);
  };

  const announceSuccess = (message: string): void => {
    toasts.show({ tone: "success", title: message });
  };

  const announceFailure = (message: string): void => {
    toasts.show({ tone: "failure", title: message });
  };

  const sections: readonly Section[] = [
    {
      name: "account",
      label: "Account",
      panel: () => (
        <AccountPanel onSaved={announceSuccess} onFailed={announceFailure} />
      ),
    },
    {
      name: "appearance",
      label: "Appearance",
      panel: () => (
        <ThemePanel
          chosen={Theme.painted()}
          onChoose={(choice) => void chooseTheme(choice)}
        />
      ),
    },
    {
      name: "keys",
      label: "AI provider keys",
      panel: () => (
        <ProviderKeysPanel
          onSaved={announceSuccess}
          onFailed={announceFailure}
        />
      ),
    },
    {
      name: "deletion",
      label: "Delete account",
      panel: () => <DeleteAccountPanel onFailed={announceFailure} />,
    },
  ];

  return (
    <AppShell>
      <div class="page">
        <div class="settings">
          <h1 class="settings-title">Settings</h1>

          <div class="settings-layout">
            <nav class="settings-nav" aria-label="Settings sections">
              <For each={sections}>
                {(entry) => (
                  <button
                    class="settings-nav-item"
                    type="button"
                    aria-current={
                      section() === entry.name ? "page" : undefined
                    }
                    onClick={() => setSection(entry.name)}
                  >
                    {entry.label}
                  </button>
                )}
              </For>
            </nav>

            <Show keyed when={section()}>
              {(selected) =>
                sections.find((entry) => entry.name === selected)?.panel()
              }
            </Show>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
