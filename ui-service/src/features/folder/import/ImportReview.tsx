import { Show, type JSX } from "solid-js";
import { Icon } from "../../../shared/ui/icons/Icon";
import { ImportSpinner } from "./ImportSpinner";

type ImportWaitProps = {
  readonly isWritingNote: boolean;
  readonly sourceName: string;
};

export function ImportWait(props: ImportWaitProps): JSX.Element {
  return (
    <div class="modal-wait">
      <ImportSpinner />
      <span class="modal-wait-text">
        <Show
          when={props.isWritingNote}
          fallback={`Reading ${props.sourceName}…`}
        >
          Writing a note about {props.sourceName}…
        </Show>
      </span>
      <span class="modal-wait-hint">
        You will see the text before anything else is generated.
      </span>
    </div>
  );
}

type ImportReviewProps = {
  readonly sourceName: string;
  readonly isNoteAlreadyMade: boolean;
  readonly text: string;
  readonly onTextChange: (text: string) => void;
};

export function ImportReview(props: ImportReviewProps): JSX.Element {
  return (
    <>
      <div class="review-source">
        <Icon name="fileSmall" size="sm" />
        <span>From {props.sourceName}</span>
      </div>
      <div class="field">
        <label for="review-text">
          <Show when={props.isNoteAlreadyMade} fallback="Text">
            Note
          </Show>
        </label>
        <textarea
          class="input input-tall"
          id="review-text"
          value={props.text}
          onInput={(event) => { props.onTextChange(event.currentTarget.value); }}
        />
        <span class="field-hint">
          <Show
            when={props.isNoteAlreadyMade}
            fallback="Trim anything that should not become study material."
          >
            Your note is saved in the folder. Trim this before making anything
            else from it.
          </Show>
        </span>
      </div>
    </>
  );
}
