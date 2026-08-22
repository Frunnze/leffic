import { createSignal, onMount, type JSX } from "solid-js";
import { ModalBackdrop } from "./ModalBackdrop";
import { DIALOG_TITLE_ID, ModalHead } from "./ModalHead";

type PromptDialogProps = {
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
  });

  return (
    <ModalBackdrop onDismiss={props.onCancel}>
      <form
        class="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby={DIALOG_TITLE_ID}
        onSubmit={confirm}
      >
        <ModalHead
          title={props.title}
          description={props.description}
          onClose={props.onCancel}
        />

        <div class="modal-body">
          <div class="field">
            <label for="dialog-input">{props.label}</label>
            <input
              ref={(element) => {
                inputElement = element;
              }}
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
          <button class="btn" type="button" onClick={() => { props.onCancel(); }}>
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
    </ModalBackdrop>
  );
}
