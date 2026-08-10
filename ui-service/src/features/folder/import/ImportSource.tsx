import { For, Match, Switch, type JSX } from "solid-js";
import { Icon } from "../../../shared/ui/icons/Icon";
import { SOURCE_KINDS, type SourceKind } from "./import-options";

export type ImportSourceProps = {
  readonly kind: SourceKind;
  readonly chosenFile: File | null;
  readonly link: string;
  readonly text: string;
  readonly topic: string;
  readonly onKindChange: (kind: SourceKind) => void;
  readonly onFileChosen: (file: File) => void;
  readonly onLinkChange: (link: string) => void;
  readonly onTextChange: (text: string) => void;
  readonly onTopicChange: (topic: string) => void;
};

export function ImportSource(props: ImportSourceProps): JSX.Element {
  let fileInput: HTMLInputElement | undefined;

  return (
    <>
      <div class="segmented segmented-lg">
        <For each={SOURCE_KINDS}>
          {(source) => (
            <label class="segment">
              <input
                type="radio"
                name="import-source"
                checked={props.kind === source.kind}
                onChange={() => props.onKindChange(source.kind)}
              />
              <span class="segment-face">{source.label}</span>
            </label>
          )}
        </For>
      </div>

      <div class="source-panel">
        <Switch>
          <Match when={props.kind === "file" && props.chosenFile === null}>
            <div class="dropzone">
              <Icon name="fileSmall" />
              <span class="dropzone-text">Drop a file here</span>
              <button
                class="btn"
                type="button"
                onClick={() => fileInput?.click()}
              >
                Browse files
              </button>
              <span class="dropzone-hint">
                PDF, DOCX, PPTX or TXT · up to 20 MB
              </span>
            </div>
          </Match>

          <Match when={props.kind === "file" && props.chosenFile !== null}>
            <div class="chosen-file">
              <Icon name="fileSmall" size="sm" />
              <span class="chosen-file-name">{props.chosenFile?.name}</span>
              <button
                class="btn"
                type="button"
                onClick={() => fileInput?.click()}
              >
                Replace
              </button>
            </div>
          </Match>

          <Match when={props.kind === "link"}>
            <div class="field">
              <label for="import-link">Link</label>
              <input
                class="input"
                id="import-link"
                type="url"
                placeholder="https://"
                value={props.link}
                onInput={(event) =>
                  props.onLinkChange(event.currentTarget.value)
                }
              />
              <span class="field-hint">
                A web page or a YouTube video with a transcript.
              </span>
            </div>
          </Match>

          <Match when={props.kind === "text"}>
            <div class="field">
              <label for="import-text">Text</label>
              <textarea
                class="input input-tall"
                id="import-text"
                value={props.text}
                onInput={(event) =>
                  props.onTextChange(event.currentTarget.value)
                }
              />
              <span class="field-hint">
                Everything comes from this text. Leffic adds nothing of its
                own.
              </span>
            </div>
          </Match>

          <Match when={props.kind === "topic"}>
            <div class="field">
              <label for="import-topic">Topic</label>
              <input
                class="input"
                id="import-topic"
                type="text"
                placeholder="e.g. Action potentials"
                value={props.topic}
                onInput={(event) =>
                  props.onTopicChange(event.currentTarget.value)
                }
              />
              <span class="field-hint">
                Leffic writes the material from what it knows.
              </span>
            </div>
          </Match>
        </Switch>
      </div>

      <input
        ref={fileInput}
        class="visually-hidden"
        type="file"
        aria-label="Choose a file to import"
        onChange={(event) => {
          const chosen = event.currentTarget.files?.[0];
          event.currentTarget.value = "";
          if (chosen !== undefined) props.onFileChosen(chosen);
        }}
      />
    </>
  );
}
