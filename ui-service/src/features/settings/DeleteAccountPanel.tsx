import { Show, createSignal, type JSX } from "solid-js";
import { useNavigate } from "@solidjs/router";
import { AccountApi } from "./account-api";
import { PromptDialog } from "../../shared/ui/PromptDialog";
import { Session } from "../../shared/api/session";

export type DeleteAccountPanelProps = {
  readonly onFailed: (message: string) => void;
};

export function DeleteAccountPanel(
  props: DeleteAccountPanelProps,
): JSX.Element {
  const navigate = useNavigate();
  const [isConfirming, setConfirming] = createSignal(false);

  const remove = async (password: string): Promise<void> => {
    setConfirming(false);

    try {
      await AccountApi.deleteAccount(password);
      Session.store(null);
      navigate("/");
    } catch {
      props.onFailed("That account could not be deleted.");
    }
  };

  return (
    <section class="settings-panel" aria-labelledby="panel-title">
      <div class="settings-card-head">
        <h2 class="settings-card-title" id="panel-title">
          Delete account
        </h2>
        <span class="settings-card-text">
          Removes your folders, decks, tests, notes, review history and saved
          keys. This cannot be undone.
        </span>
      </div>

      <div class="settings-actions">
        <button
          class="btn is-danger"
          type="button"
          onClick={() => setConfirming(true)}
        >
          Delete account
        </button>
      </div>

      <Show when={isConfirming()}>
        <PromptDialog
          title="Delete your account?"
          description="Everything goes with it."
          label="Enter your password to confirm"
          placeholder="Your password"
          inputType="password"
          confirmLabel="Delete account"
          confirmTone="danger"
          onConfirm={(password) => void remove(password)}
          onCancel={() => setConfirming(false)}
        />
      </Show>
    </section>
  );
}
