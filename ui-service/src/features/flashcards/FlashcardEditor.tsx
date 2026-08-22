import { createSignal, untrack, type JSX } from "solid-js";
import { FlashcardFields } from "./FlashcardFields";
import { FlashcardWording } from "./flashcard-wording";
import type { Flashcard, FlashcardFace } from "./flashcard-models";
import { ModalBackdrop } from "../../shared/ui/ModalBackdrop";
import { DIALOG_TITLE_ID, ModalHead } from "../../shared/ui/ModalHead";
import { ModalFoot } from "../../shared/ui/ModalFoot";

type FlashcardEditorProps = {
  readonly card: Flashcard;
  readonly onSave: (face: FlashcardFace) => void;
  readonly onCancel: () => void;
};

export function FlashcardEditor(props: FlashcardEditorProps): JSX.Element {
  const [face, setFace] = createSignal<FlashcardFace>(
    untrack(() => props.card.face),
  );

  const isEmpty = (): boolean => {
    const words = FlashcardWording.of(face());

    return (
      words.question.trim().length === 0 || words.answer.trim().length === 0
    );
  };

  const save = (event: Event): void => {
    event.preventDefault();
    if (isEmpty()) return;

    props.onSave(face());
  };

  return (
    <ModalBackdrop onDismiss={props.onCancel}>
      <form
        class="modal modal-wide"
        role="dialog"
        aria-modal="true"
        aria-labelledby={DIALOG_TITLE_ID}
        onSubmit={save}
      >
        <ModalHead
          title="Edit card"
          description="Changes apply the next time this card comes up."
          onClose={props.onCancel}
        />

        <div class="modal-body">
          <div class="edit-fields">
            <FlashcardFields face={face()} onChange={setFace} />
          </div>
        </div>

        <ModalFoot
          confirmLabel="Save card"
          isConfirmBlocked={isEmpty()}
          onCancel={props.onCancel}
        />
      </form>
    </ModalBackdrop>
  );
}
