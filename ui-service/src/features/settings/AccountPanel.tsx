import { Show, createResource, createSignal, type JSX } from "solid-js";
import { AccountApi } from "./account-api";

export type AccountPanelProps = {
  readonly onSaved: (message: string) => void;
  readonly onFailed: (message: string) => void;
};

export function AccountPanel(props: AccountPanelProps): JSX.Element {
  const [account, { refetch }] = createResource(() => AccountApi.read());
  const [username, setUsername] = createSignal<string | null>(null);
  const [isChangingPassword, setChangingPassword] = createSignal(false);
  const [currentPassword, setCurrentPassword] = createSignal("");
  const [newPassword, setNewPassword] = createSignal("");

  const shownUsername = (): string =>
    username() ?? account()?.username ?? "";

  const saveUsername = async (): Promise<void> => {
    try {
      await AccountApi.changeUsername(shownUsername().trim());
      void refetch();
      props.onSaved("Username saved.");
    } catch {
      props.onFailed("That username could not be saved.");
    }
  };

  const savePassword = async (): Promise<void> => {
    try {
      await AccountApi.changePassword(currentPassword(), newPassword());
      setChangingPassword(false);
      setCurrentPassword("");
      setNewPassword("");
      props.onSaved("Password changed.");
    } catch {
      props.onFailed("That password could not be changed.");
    }
  };

  return (
    <section class="settings-panel" aria-labelledby="panel-title">
      <div class="settings-card-head">
        <h2 class="settings-card-title" id="panel-title">
          Account
        </h2>
        <span class="settings-card-text">
          Your username is how you log in.
        </span>
      </div>

      <div class="field">
        <label for="account-username">Username</label>
        <input
          class="input"
          id="account-username"
          type="text"
          value={shownUsername()}
          onInput={(event) => setUsername(event.currentTarget.value)}
        />
      </div>

      <div class="settings-actions">
        <button
          class="btn"
          type="button"
          disabled={shownUsername().trim().length === 0}
          onClick={() => void saveUsername()}
        >
          Save changes
        </button>
      </div>

      <div class="settings-row">
        <span class="settings-row-label">
          Password
          <span class="settings-row-value">
            Only you know it. Change it whenever you like.
          </span>
        </span>
        <Show when={!isChangingPassword()}>
          <button
            class="btn"
            type="button"
            onClick={() => setChangingPassword(true)}
          >
            Change password
          </button>
        </Show>
      </div>

      <Show when={isChangingPassword()}>
        <div class="field">
          <label for="current-password">Current password</label>
          <input
            class="input"
            id="current-password"
            type="password"
            value={currentPassword()}
            onInput={(event) => setCurrentPassword(event.currentTarget.value)}
          />
        </div>

        <div class="field">
          <label for="new-password">New password</label>
          <input
            class="input"
            id="new-password"
            type="password"
            value={newPassword()}
            onInput={(event) => setNewPassword(event.currentTarget.value)}
          />
        </div>

        <div class="settings-actions">
          <button
            class="btn btn-primary"
            type="button"
            disabled={newPassword().length === 0}
            onClick={() => void savePassword()}
          >
            Save password
          </button>
          <button
            class="btn"
            type="button"
            onClick={() => setChangingPassword(false)}
          >
            Cancel
          </button>
        </div>
      </Show>
    </section>
  );
}
