import { For, Show, type JSX } from "solid-js";
import type { SourceKind } from "./import-options";
import { SourceKindHandlers } from "./source-kind-handlers";

export type ImportSourceProps = {
  readonly kind: SourceKind;
  readonly chosenFile: File | null;
  readonly link: string;
  readonly text: string;
  readonly topic: string;
  readonly firstPage: string;
  readonly lastPage: string;
  readonly onFirstPageChange: (page: string) => void;
  readonly onLastPageChange: (page: string) => void;
  readonly onKindChange: (kind: SourceKind) => void;
  readonly onFileChosen: (file: File) => void;
  readonly onLinkChange: (link: string) => void;
  readonly onTextChange: (text: string) => void;
  readonly onTopicChange: (topic: string) => void;
};

export function ImportSource(props: ImportSourceProps): JSX.Element {
  return (
    <>
      <div class="segmented segmented-lg">
        <For each={SourceKindHandlers.options()}>
          {(source) => (
            <label class="segment">
              <input
                type="radio"
                name="import-source"
                checked={props.kind === source.kind}
                onChange={() => { props.onKindChange(source.kind); }}
              />
              <span class="segment-face">{source.label}</span>
            </label>
          )}
        </For>
      </div>

      <div class="source-panel">
        <Show keyed when={props.kind}>
          {(kind) => SourceKindHandlers.of(kind).panel(props)}
        </Show>
      </div>

      <input
        class="visually-hidden"
        id="import-file"
        type="file"
        onChange={(event) => {
          const chosen = event.currentTarget.files?.[0];
          event.currentTarget.value = "";
          if (chosen !== undefined) props.onFileChosen(chosen);
        }}
      />
    </>
  );
}
