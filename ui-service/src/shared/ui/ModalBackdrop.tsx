import { onCleanup, onMount, type JSX } from "solid-js";

const ESCAPE_KEY = "Escape";

type ModalBackdropProps = {
  readonly onDismiss: () => void;
  readonly children: JSX.Element;
};

export function ModalBackdrop(props: ModalBackdropProps): JSX.Element {
  const dismissOnEscape = (event: KeyboardEvent): void => {
    if (event.key === ESCAPE_KEY) props.onDismiss();
  };

  onMount(() => {
    document.addEventListener("keydown", dismissOnEscape);

    onCleanup(() => {
      document.removeEventListener("keydown", dismissOnEscape);
    });
  });

  return (
    <div
      class="modal-backdrop"
      onClick={(event) => {
        if (event.target === event.currentTarget) props.onDismiss();
      }}
    >
      {props.children}
    </div>
  );
}
