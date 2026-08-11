import { For, Show, type JSX } from "solid-js";
import { Icon } from "../../shared/ui/icons/Icon";
import type { IconName } from "../../shared/ui/icons/icon-shapes";
import type { Toast, ToastTone } from "./toast-store";

const TONE_CLASS: Readonly<Record<ToastTone, string>> = {
  progress: "toast-progress",
  success: "toast-success",
  failure: "toast-failure",
};

const TONE_ICON: Readonly<Record<ToastTone, IconName>> = {
  progress: "start",
  success: "success",
  failure: "failure",
};

export type ToastsProps = {
  readonly toasts: readonly Toast[];
  readonly onDismiss: (id: string) => void;
};

export function Toasts(props: ToastsProps): JSX.Element {
  return (
    <Show when={props.toasts.length > 0}>
      <div class="toast-stack" role="status" aria-live="polite">
        <For each={props.toasts}>
          {(toast) => (
            <div class={`toast ${TONE_CLASS[toast.tone]}`}>
              <span class="toast-icon">
                <Icon name={TONE_ICON[toast.tone]} />
              </span>
              <div class="toast-text">
                <span class="toast-title">{toast.title}</span>
                <Show when={toast.detail}>
                  <span class="toast-detail">{toast.detail}</span>
                </Show>
              </div>
              <button
                class="btn btn-quiet btn-icon"
                type="button"
                aria-label={`Dismiss "${toast.title}"`}
                onClick={() => props.onDismiss(toast.id)}
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
