import { onCleanup, onMount, type JSX } from "solid-js";
import { Icon } from "./icons/Icon";

const ESCAPE_KEY = "Escape";

export type ConfirmDialogProps = {
  readonly title: string;
  readonly description: string;
  readonly confirmLabel: string;
  readonly onConfirm: () => void;
  readonly onCancel: () => void;
};

export function ConfirmDialog(props: ConfirmDialogProps): JSX.Element {
  onMount(() => {
    const dismissOnEscape = (event: KeyboardEvent): void => {
      if (event.key === ESCAPE_KEY) props.onCancel();
    };

    document.addEventListener("keydown", dismissOnEscape);
    onCleanup(() => document.removeEventListener("keydown", dismissOnEscape));
  });

  return (
    <div
      class="modal-backdrop"
      onClick={(event) => {
        if (event.target === event.currentTarget) props.onCancel();
      }}
    >
      <div
        class="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
      >
        <div class="modal-head">
          <div class="modal-heading">
            <h2 class="modal-title" id="dialog-title">
              {props.title}
            </h2>
            <span class="modal-text">{props.description}</span>
          </div>
          <button
            class="btn btn-quiet btn-icon"
            type="button"
            aria-label="Close dialog"
            onClick={() => props.onCancel()}
          >
            <Icon name="closePlain" size="sm" />
          </button>
        </div>

        <div class="modal-foot">
          <button class="btn" type="button" onClick={() => props.onCancel()}>
            Cancel
          </button>
          <button
            class="btn btn-danger"
            type="button"
            onClick={() => props.onConfirm()}
          >
            {props.confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
