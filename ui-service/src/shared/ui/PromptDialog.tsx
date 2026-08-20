import { createSignal, onCleanup, onMount, type JSX } from "solid-js";
import { Icon } from "./icons/Icon";

const ESCAPE_KEY = "Escape";

export type PromptDialogProps = {
  readonly title: string;
  readonly description: string;
  readonly label: string;
  readonly placeholder: string;
  readonly inputType: "text" | "url" | "password";
  readonly confirmLabel: string;
  readonly confirmTone?: "primary" | "danger";
  readonly onConfirm: (value: string) => void;
  readonly onCancel: () => void;
};

export function PromptDialog(props: PromptDialogProps): JSX.Element {
  const [value, setValue] = createSignal("");
  let inputElement: HTMLInputElement | undefined;

  const isEmpty = (): boolean => value().trim().length === 0;

  const confirm = (event: Event): void => {
    event.preventDefault();
    if (isEmpty()) return;

    props.onConfirm(value().trim());
  };

  onMount(() => {
    inputElement?.focus();

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
      <form
        class="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        onSubmit={confirm}
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

        <div class="modal-body">
          <div class="field">
            <label for="dialog-input">{props.label}</label>
            <input
              ref={inputElement}
              class="input"
              id="dialog-input"
              type={props.inputType}
              placeholder={props.placeholder}
              value={value()}
              onInput={(event) => setValue(event.currentTarget.value)}
            />
          </div>
        </div>

        <div class="modal-foot">
          <button class="btn" type="button" onClick={() => props.onCancel()}>
            Cancel
          </button>
          <button
            class={
              props.confirmTone === "danger"
                ? "btn btn-danger"
                : "btn btn-primary"
            }
            type="submit"
            disabled={isEmpty()}
          >
            {props.confirmLabel}
          </button>
        </div>
      </form>
    </div>
  );
}
