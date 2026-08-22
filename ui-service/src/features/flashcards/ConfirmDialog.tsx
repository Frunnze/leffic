import type { JSX } from "solid-js";
import { ModalBackdrop } from "../../shared/ui/ModalBackdrop";
import { DIALOG_TITLE_ID, ModalHead } from "../../shared/ui/ModalHead";

type ConfirmDialogProps = {
  readonly title: string;
  readonly description: string;
  readonly confirmLabel: string;
  readonly onConfirm: () => void;
  readonly onCancel: () => void;
};

export function ConfirmDialog(props: ConfirmDialogProps): JSX.Element {
  return (
    <ModalBackdrop onDismiss={props.onCancel}>
      <div
        class="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby={DIALOG_TITLE_ID}
      >
        <ModalHead
          title={props.title}
          description={props.description}
          onClose={props.onCancel}
        />

        <div class="modal-foot">
          <button class="btn" type="button" onClick={() => { props.onCancel(); }}>
            Cancel
          </button>
          <button
            class="btn btn-danger"
            type="button"
            onClick={() => { props.onConfirm(); }}
          >
            {props.confirmLabel}
          </button>
        </div>
      </div>
    </ModalBackdrop>
  );
}
