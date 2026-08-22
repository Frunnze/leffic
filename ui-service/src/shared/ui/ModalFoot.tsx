import type { JSX } from "solid-js";

type ModalFootProps = {
  readonly confirmLabel: string;
  readonly isConfirmBlocked: boolean;
  readonly onCancel: () => void;
};

export function ModalFoot(props: ModalFootProps): JSX.Element {
  return (
    <div class="modal-foot">
      <button
        class="btn"
        type="button"
        onClick={() => {
          props.onCancel();
        }}
      >
        Cancel
      </button>
      <button
        class="btn btn-primary"
        type="submit"
        disabled={props.isConfirmBlocked}
      >
        {props.confirmLabel}
      </button>
    </div>
  );
}
