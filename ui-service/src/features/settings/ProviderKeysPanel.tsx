import { For, Show, createResource, createSignal, type JSX } from "solid-js";
import { AccountApi } from "./account-api";
import { Icon } from "../../shared/ui/icons/Icon";
import { ProviderKeyBlock, type Provider } from "./ProviderKeyBlock";
import { PromptDialog } from "../../shared/ui/PromptDialog";

const PROVIDERS: readonly Provider[] = [
  { id: "openai", name: "OpenAI" },
  { id: "gemini", name: "Gemini" },
];

const ENCRYPTION_CODE_URL = "https://github.com/Frunnze/leffic";

type PendingKey = {
  readonly provider: string;
  readonly key: string;
  readonly monthlyLimitCents: number | null;
};

type ProviderKeysPanelProps = {
  readonly onSaved: (message: string) => void;
  readonly onFailed: (message: string) => void;
};

export function ProviderKeysPanel(
  props: ProviderKeysPanelProps,
): JSX.Element {
  const [keys, { refetch }] = createResource(() => AccountApi.providerKeys());
  const [pending, setPending] = createSignal<PendingKey | null>(null);

  const savedKey = (provider: string) =>
    keys()?.find((entry) => entry.provider === provider);

  const seal = async (
    request: PendingKey,
    password: string,
  ): Promise<void> => {
    setPending(null);

    try {
      await AccountApi.saveProviderKey({ ...request, password });
      void refetch();
      props.onSaved("Key sealed with your password.");
    } catch {
      props.onFailed("That key could not be saved.");
    }
  };

  const remove = async (provider: string): Promise<void> => {
    try {
      await AccountApi.removeProviderKey(provider);
      void refetch();
      props.onSaved("Key removed.");
    } catch {
      props.onFailed("That key could not be removed.");
    }
  };

  return (
    <section class="settings-panel" aria-labelledby="panel-title">
      <div class="settings-card-head">
        <h2 class="settings-card-title" id="panel-title">
          AI provider keys
        </h2>
        <span class="settings-card-text">
          Bring your own key and Leffic generates with it instead of the
          shared quota.
        </span>
      </div>

      <div class="secure-note">
        <Icon name="success" size="sm" />
        <div class="secure-note-body">
          <p>
            <span class="secure-note-text">
              Your key is encrypted with your password. Only you can unlock it
              — not Leffic, not the developer.
            </span>
          </p>
          <a class="text-action" href={ENCRYPTION_CODE_URL}>
            Read the encryption code
          </a>
        </div>
      </div>

      <For each={PROVIDERS}>
        {(provider) => (
          <ProviderKeyBlock
            provider={provider}
            savedKey={savedKey(provider.id)}
            onSave={(key, monthlyLimitCents) =>
              setPending({ provider: provider.id, key, monthlyLimitCents })
            }
            onRemove={() => void remove(provider.id)}
          />
        )}
      </For>

      <Show when={pending()}>
        {(request) => (
          <PromptDialog
            title="Confirm your password"
            description="The key is sealed with a secret derived from it."
            label="Password"
            placeholder="Your password"
            inputType="password"
            confirmLabel="Seal the key"
            onConfirm={(password) => void seal(request(), password)}
            onCancel={() => setPending(null)}
          />
        )}
      </Show>
    </section>
  );
}
