import { createSignal, onCleanup, onMount, type JSX } from "solid-js";
import { Icon } from "../../shared/ui/icons/Icon";
import type { Flashcard } from "./flashcard-models";

const ESCAPE_KEY = "Escape";

export type FlashcardEditorProps = {
  readonly card: Flashcard;
  readonly onSave: (front: string, back: string) => void;
  readonly onCancel: () => void;
};

export function FlashcardEditor(props: FlashcardEditorProps): JSX.Element {
  const [front, setFront] = createSignal(props.card.front);
  const [back, setBack] = createSignal(props.card.back);

  const isEmpty = (): boolean =>
    front().trim().length === 0 || back().trim().length === 0;

  const save = (event: Event): void => {
    event.preventDefault();
    if (isEmpty()) return;

    props.onSave(front().trim(), back().trim());
  };

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
      <form
        class="modal modal-wide"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        onSubmit={save}
      >
        <div class="modal-head">
          <div class="modal-heading">
            <h2 class="modal-title" id="dialog-title">
              Edit card
            </h2>
            <span class="modal-text">
              Changes apply the next time this card comes up.
            </span>
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
          <div class="edit-fields">
            <div class="field">
              <label for="card-front">Front</label>
              <textarea
                class="input"
                id="card-front"
                rows="3"
                value={front()}
                onInput={(event) => setFront(event.currentTarget.value)}
              />
            </div>
            <div class="field">
              <label for="card-back">Back</label>
              <textarea
                class="input"
                id="card-back"
                rows="3"
                value={back()}
                onInput={(event) => setBack(event.currentTarget.value)}
              />
            </div>
          </div>
        </div>

        <div class="modal-foot">
          <button class="btn" type="button" onClick={() => props.onCancel()}>
            Cancel
          </button>
          <button class="btn btn-primary" type="submit" disabled={isEmpty()}>
            Save card
          </button>
        </div>
      </form>
    </div>
  );
}
