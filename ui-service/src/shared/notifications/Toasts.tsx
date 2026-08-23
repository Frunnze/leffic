import { For, Show, type JSX } from "solid-js";
import { Icon } from "../ui/icons/Icon";
import type { IconName } from "../ui/icons/icon-shapes";
import type { Toast, ToastTone } from "./toast-store";

const TONES: Readonly<
  Record<ToastTone, { readonly className: string; readonly icon: IconName }>
> = {
  progress: { className: "toast-progress", icon: "start" },
  success: { className: "toast-success", icon: "success" },
  failure: { className: "toast-failure", icon: "failure" },
};

type ToastsProps = {
  readonly toasts: readonly Toast[];
  readonly onDismiss: (id: string) => void;
};

export function Toasts(props: ToastsProps): JSX.Element {
  return (
    <Show when={props.toasts.length > 0}>
      <div class="toast-stack" role="status" aria-live="polite">
        <For each={props.toasts}>
          {(toast) => (
            <div class={`toast ${TONES[toast.tone].className}`}>
              <span class="toast-icon">
                <Icon name={TONES[toast.tone].icon} />
              </span>
              <div class="toast-text">
                <span class="toast-title">{toast.title}</span>
                <Show when={toast.detail}>
                  <span class="toast-detail">{toast.detail}</span>
                </Show>
              </div>
              <button
                class="toast-dismiss"
                type="button"
                aria-label={`Dismiss "${toast.title}"`}
                onClick={() => { props.onDismiss(toast.id); }}
              >
                <Icon name="closePlain" size="sm" />
              </button>
            </div>
          )}
        </For>
      </div>
    </Show>
  );
}
