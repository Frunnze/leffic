import { For, Match, Switch, type JSX } from "solid-js";
import { ClozeText } from "./ClozeText";
import type { FlashcardFace } from "./flashcard-models";

export type FlashcardPromptProps = {
  readonly face: FlashcardFace;
};

export function FlashcardPrompt(props: FlashcardPromptProps): JSX.Element {
  return (
    <Switch>
      <Match when={props.face.kind === "basic" && props.face}>
        {(face) => <p class="flashcard-prompt">{face().front}</p>}
      </Match>

      <Match when={props.face.kind === "cloze" && props.face}>
        {(face) => (
          <p class="flashcard-prompt">
            <ClozeText
              text={face().text}
              hiddenParts={face().hiddenParts}
              isRevealed={false}
            />
          </p>
        )}
      </Match>

      <Match when={props.face.kind === "list" && props.face}>
        {(face) => (
          <>
            <p class="flashcard-prompt">{face().question}</p>
            <p class="flashcard-hint">
              Name {face().items.length} items, then check yourself.
            </p>
          </>
        )}
      </Match>

      <Match when={props.face.kind === "feynman" && props.face}>
        {(face) => (
          <>
            <p class="flashcard-prompt">{face().prompt}</p>
            <p class="flashcard-hint">
              Explain it out loud in plain language before you flip.
            </p>
          </>
        )}
      </Match>
    </Switch>
  );
}

export function FlashcardAnswer(props: FlashcardPromptProps): JSX.Element {
  return (
    <Switch>
      <Match when={props.face.kind === "basic" && props.face}>
        {(face) => <p class="flashcard-prompt">{face().back}</p>}
      </Match>

      <Match when={props.face.kind === "cloze" && props.face}>
        {(face) => (
          <p class="flashcard-prompt">
            <ClozeText
              text={face().text}
              hiddenParts={face().hiddenParts}
              isRevealed
            />
          </p>
        )}
      </Match>

      <Match when={props.face.kind === "list" && props.face}>
        {(face) => (
          <ul class="flashcard-list">
            <For each={face().items}>{(item) => <li>{item}</li>}</For>
          </ul>
        )}
      </Match>

      <Match when={props.face.kind === "feynman" && props.face}>
        {(face) => (
          <p class="flashcard-prompt">{face().referenceExplanation}</p>
        )}
      </Match>
    </Switch>
  );
}
