import { Show, createSignal, type JSX } from "solid-js";
import { ConfirmDialog } from "../../shared/ui/ConfirmDialog";
import { Dropdown } from "../../shared/ui/Dropdown";
import { FlashcardEditor } from "./FlashcardEditor";
import { Icon } from "../../shared/ui/icons/Icon";
import type { Flashcard } from "./flashcard-models";

export type FlashcardActionsProps = {
  readonly card: Flashcard;
  readonly onSave: (front: string, back: string) => void;
  readonly onDelete: () => void;
  readonly onMnemonic: () => void;
};

export function FlashcardActions(props: FlashcardActionsProps): JSX.Element {
  const [isMenuOpen, setMenuOpen] = createSignal(false);
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
          onClick={() => props.onMnemonic()}
        >
          <Icon name="mnemonic" size="sm" />
        </button>
        <button
          class="btn btn-quiet btn-icon"
          type="button"
          aria-label="Actions for this card"
          aria-expanded={isMenuOpen()}
          onClick={() => setMenuOpen(!isMenuOpen())}
        >
          <Icon name="dots" size="sm" />
        </button>
        <Dropdown
          isOpen={isMenuOpen()}
          onDismiss={() => setMenuOpen(false)}
          items={[
            {
              label: "Edit card",
              icon: "note",
              onSelect: () => {
                setMenuOpen(false);
                setEditing(true);
              },
            },
            {
              label: "Delete card",
              icon: "trash",
              danger: true,
              onSelect: () => {
                setMenuOpen(false);
                setDeleting(true);
              },
            },
          ]}
        />
      </div>

      <Show when={isEditing()}>
        <FlashcardEditor
          card={props.card}
          onSave={(front, back) => {
            setEditing(false);
            props.onSave(front, back);
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
