import { Match, Switch, type JSX } from "solid-js";
import type { FlashcardFace } from "./flashcard-models";

const LINES_APART = "\n";

export type FlashcardFieldsProps = {
  readonly face: FlashcardFace;
  readonly onChange: (face: FlashcardFace) => void;
};

export function FlashcardFields(props: FlashcardFieldsProps): JSX.Element {
  return (
    <Switch>
      <Match when={props.face.kind === "basic" && props.face}>
        {(face) => (
          <>
            <div class="field">
              <label for="card-front">Front</label>
              <textarea
                class="input"
                id="card-front"
                rows="3"
                value={face().front}
                onInput={(event) =>
                  props.onChange({
                    ...face(),
                    front: event.currentTarget.value,
                  })
                }
              />
            </div>
            <div class="field">
              <label for="card-back">Back</label>
              <textarea
                class="input"
                id="card-back"
                rows="3"
                value={face().back}
                onInput={(event) =>
                  props.onChange({ ...face(), back: event.currentTarget.value })
                }
              />
            </div>
          </>
        )}
      </Match>

      <Match when={props.face.kind === "cloze" && props.face}>
        {(face) => (
          <>
            <div class="field">
              <label for="card-text">Sentence</label>
              <textarea
                class="input"
                id="card-text"
                rows="3"
                value={face().text}
                onInput={(event) =>
                  props.onChange({ ...face(), text: event.currentTarget.value })
                }
              />
            </div>
            <div class="field">
              <label for="card-hidden">Hidden parts, one per line</label>
              <textarea
                class="input"
                id="card-hidden"
                rows="3"
                value={face().hiddenParts.join(LINES_APART)}
                onInput={(event) =>
                  props.onChange({
                    ...face(),
                    hiddenParts: event.currentTarget.value.split(LINES_APART),
                  })
                }
              />
            </div>
          </>
        )}
      </Match>

      <Match when={props.face.kind === "list" && props.face}>
        {(face) => (
          <>
            <div class="field">
              <label for="card-question">Question</label>
              <textarea
                class="input"
                id="card-question"
                rows="2"
                value={face().question}
                onInput={(event) =>
                  props.onChange({
                    ...face(),
                    question: event.currentTarget.value,
                  })
                }
              />
            </div>
            <div class="field">
              <label for="card-items">Items, one per line</label>
              <textarea
                class="input"
                id="card-items"
                rows="4"
                value={face().items.join(LINES_APART)}
                onInput={(event) =>
                  props.onChange({
                    ...face(),
                    items: event.currentTarget.value.split(LINES_APART),
                  })
                }
              />
            </div>
          </>
        )}
      </Match>

      <Match when={props.face.kind === "feynman" && props.face}>
        {(face) => (
          <>
            <div class="field">
              <label for="card-prompt">Explain this</label>
              <textarea
                class="input"
                id="card-prompt"
                rows="2"
                value={face().prompt}
                onInput={(event) =>
                  props.onChange({
                    ...face(),
                    prompt: event.currentTarget.value,
                  })
                }
              />
            </div>
            <div class="field">
              <label for="card-reference">Reference explanation</label>
              <textarea
                class="input"
                id="card-reference"
                rows="4"
                value={face().referenceExplanation}
                onInput={(event) =>
                  props.onChange({
                    ...face(),
                    referenceExplanation: event.currentTarget.value,
                  })
                }
              />
            </div>
          </>
        )}
      </Match>
    </Switch>
  );
}
