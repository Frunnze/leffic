import { Show, createSignal, type JSX } from "solid-js";
import { ConfirmDialog } from "./ConfirmDialog";
import { CardMenu } from "../../shared/ui/CardMenu";
import { FlashcardEditor } from "./FlashcardEditor";
import { Icon } from "../../shared/ui/icons/Icon";
import type { Flashcard, FlashcardFace } from "./flashcard-models";

type FlashcardActionsProps = {
  readonly card: Flashcard;
  readonly onSave: (face: FlashcardFace) => void;
  readonly onDelete: () => void;
  readonly onMnemonic: () => void;
};

export function FlashcardActions(props: FlashcardActionsProps): JSX.Element {
  const [isEditing, setEditing] = createSignal(false);
  const [isDeleting, setDeleting] = createSignal(false);

  return (
    <>
      <div class="card-menu">
        <button
          class="btn btn-quiet btn-icon"
          type="button"
          aria-label="Ask for a way to memorise this card"
          title="Mnemonic"
          onClick={() => { props.onMnemonic(); }}
        >
          <Icon name="mnemonic" size="sm" />
        </button>
        <CardMenu
          label="Actions for this card"
          items={[
            {
              label: "Edit card",
              icon: "note",
              onSelect: () => setEditing(true),
            },
            {
              label: "Delete card",
              icon: "trash",
              danger: true,
              onSelect: () => setDeleting(true),
            },
          ]}
        />
      </div>

      <Show when={isEditing()}>
        <FlashcardEditor
          card={props.card}
          onSave={(face) => {
            setEditing(false);
            props.onSave(face);
          }}
          onCancel={() => setEditing(false)}
        />
      </Show>

      <Show when={isDeleting()}>
        <ConfirmDialog
          title="Delete this card?"
          description="It leaves the deck for good."
          confirmLabel="Delete card"
          onConfirm={() => {
            setDeleting(false);
            props.onDelete();
          }}
          onCancel={() => setDeleting(false)}
        />
      </Show>
    </>
  );
}
