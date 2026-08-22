import type { JSX } from "solid-js";
import { Icon } from "./icons/Icon";

export const DIALOG_TITLE_ID = "dialog-title";

type ModalHeadProps = {
  readonly title: JSX.Element;
  readonly description: JSX.Element;
  readonly onClose: () => void;
};

export function ModalHead(props: ModalHeadProps): JSX.Element {
  return (
    <div class="modal-head">
      <div class="modal-heading">
        <h2 class="modal-title" id={DIALOG_TITLE_ID}>
          {props.title}
        </h2>
        <span class="modal-text">{props.description}</span>
      </div>
      <button
        class="btn btn-quiet btn-icon"
        type="button"
        aria-label="Close dialog"
        onClick={() => {
          props.onClose();
        }}
      >
        <Icon name="closePlain" size="sm" />
      </button>
    </div>
  );
}
