import { createSignal, type JSX } from "solid-js";
import { Icon } from "./icons/Icon";

export type PromptDialogProps = {
  readonly title: string;
  readonly description: string;
  readonly label: string;
  readonly placeholder: string;
  readonly inputType: "text" | "url";
  readonly confirmLabel: string;
  readonly onConfirm: (value: string) => void;
  readonly onCancel: () => void;
};

export function PromptDialog(props: PromptDialogProps): JSX.Element {
  const [value, setValue] = createSignal("");

  const confirm = (event: Event): void => {
    event.preventDefault();
    const entered = value().trim();
    if (entered.length === 0) return;

    props.onConfirm(entered);
  };

  return (
    <div class="modal-backdrop">
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
          <button class="btn btn-primary" type="submit">
            {props.confirmLabel}
          </button>
        </div>
      </form>
    </div>
  );
}
