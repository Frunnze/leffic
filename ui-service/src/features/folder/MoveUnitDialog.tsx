import { For, createSignal, type JSX } from "solid-js";
import type { Unit } from "./unit-models";
import { ModalBackdrop } from "../../shared/ui/ModalBackdrop";
import { DIALOG_TITLE_ID, ModalHead } from "../../shared/ui/ModalHead";
import { ModalFoot } from "../../shared/ui/ModalFoot";

const HOME_FOLDER_ID = "home";

export type MoveDestination = {
  readonly id: string;
  readonly name: string;
};

type MoveUnitDialogProps = {
  readonly unit: Unit;
  readonly destinations: readonly MoveDestination[];
  readonly onConfirm: (folderId: string) => void;
  readonly onCancel: () => void;
};

export function MoveUnitDialog(props: MoveUnitDialogProps): JSX.Element {
  const [chosenId, setChosenId] = createSignal(HOME_FOLDER_ID);

  return (
    <ModalBackdrop onDismiss={props.onCancel}>
      <form
        class="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby={DIALOG_TITLE_ID}
        onSubmit={(event) => {
          event.preventDefault();
          props.onConfirm(chosenId());
        }}
      >
        <ModalHead
          title={<>Move {props.unit.name}</>}
          description="Pick where it should live."
          onClose={props.onCancel}
        />

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

        <ModalFoot
          confirmLabel="Move here"
          isConfirmBlocked={false}
          onCancel={props.onCancel}
        />
      </form>
    </ModalBackdrop>
  );
}
