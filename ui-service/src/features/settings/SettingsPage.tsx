import { For, Match, Switch, createSignal, type JSX } from "solid-js";
import { AccountPanel } from "./AccountPanel";
import { AppShell } from "../../shared/ui/AppShell";
import { DeleteAccountPanel } from "./DeleteAccountPanel";
import { ProviderKeysPanel } from "./ProviderKeysPanel";
import { useToasts } from "../notifications/ToastContext";

type SectionName = "account" | "keys" | "deletion";

type Section = {
  readonly name: SectionName;
  readonly label: string;
};

const SECTIONS: readonly Section[] = [
  { name: "account", label: "Account" },
  { name: "keys", label: "AI provider keys" },
  { name: "deletion", label: "Delete account" },
];

export default function SettingsPage(): JSX.Element {
  const toasts = useToasts();
  const [section, setSection] = createSignal<SectionName>("account");

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
