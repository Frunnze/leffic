import { Show, type JSX } from "solid-js";

export type ImportFooterProps = {
  readonly missingSource: string | null;
  readonly nothingChosen: boolean;
  readonly isReviewing: boolean;
  readonly isExtracting: boolean;
  readonly canUploadOnly: boolean;
  readonly onCancel: () => void;
  readonly onUploadOnly: () => void;
  readonly onContinue: () => void;
  readonly onGenerate: () => void;
};

export function ImportFooter(props: ImportFooterProps): JSX.Element {
  return (
    <div class="modal-foot">
      <Show when={props.missingSource}>
        {(hint) => <span class="modal-foot-hint">{hint()}</span>}
      </Show>

      <button class="btn" type="button" onClick={() => props.onCancel()}>
        Cancel
      </button>

      <Show when={props.canUploadOnly}>
        <button
          class="btn"
          type="button"
          disabled={props.isExtracting}
          onClick={() => props.onUploadOnly()}
        >
          Upload only
        </button>
      </Show>

      <Show
        when={props.isReviewing}
        fallback={
          <button
            class="btn btn-primary"
            type="button"
            disabled={props.missingSource !== null || props.isExtracting}
            onClick={() => props.onContinue()}
          >
            Continue
          </button>
        }
      >
        <button
          class="btn btn-primary"
          type="button"
          disabled={props.missingSource !== null || props.nothingChosen}
          onClick={() => props.onGenerate()}
        >
          Generate
        </button>
      </Show>
    </div>
  );
}
