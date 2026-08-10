import { For, createSignal, onCleanup, onMount, type JSX } from "solid-js";
import { Icon } from "../../shared/ui/icons/Icon";
import type { Unit } from "../../shared/models/units";

const ESCAPE_KEY = "Escape";
const HOME_FOLDER_ID = "home";

export type MoveDestination = {
  readonly id: string;
  readonly name: string;
};

export type MoveUnitDialogProps = {
  readonly unit: Unit;
  readonly destinations: readonly MoveDestination[];
  readonly onConfirm: (folderId: string) => void;
  readonly onCancel: () => void;
};

export function MoveUnitDialog(props: MoveUnitDialogProps): JSX.Element {
  const [chosenId, setChosenId] = createSignal(HOME_FOLDER_ID);

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
        class="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        onSubmit={(event) => {
          event.preventDefault();
          props.onConfirm(chosenId());
        }}
      >
        <div class="modal-head">
          <div class="modal-heading">
            <h2 class="modal-title" id="dialog-title">
              Move {props.unit.name}
            </h2>
            <span class="modal-text">Pick where it should live.</span>
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
          <div class="answer-rows">
            <For each={props.destinations}>
              {(destination) => (
                <label class="answer-correct">
                  <input
                    type="radio"
                    name="move-destination"
                    checked={chosenId() === destination.id}
                    onChange={() => setChosenId(destination.id)}
                  />
                  {destination.name}
                </label>
              )}
            </For>
          </div>
        </div>

        <div class="modal-foot">
          <button class="btn" type="button" onClick={() => props.onCancel()}>
            Cancel
          </button>
          <button class="btn btn-primary" type="submit">
            Move here
          </button>
        </div>
      </form>
    </div>
  );
}
