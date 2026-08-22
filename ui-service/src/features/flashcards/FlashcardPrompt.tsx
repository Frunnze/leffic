import { For, type JSX } from "solid-js";
import { ClozeText } from "./ClozeText";
import { FaceView } from "./FaceView";
import type { FlashcardFace } from "./flashcard-models";

type FlashcardPromptProps = {
  readonly face: FlashcardFace;
};

export function FlashcardPrompt(props: FlashcardPromptProps): JSX.Element {
  return (
    <FaceView
      face={props.face}
      basic={(face) => <p class="flashcard-prompt">{face().front}</p>}
      cloze={(face) => (
        <p class="flashcard-prompt">
          <ClozeText
            text={face().text}
            hiddenParts={face().hiddenParts}
            isRevealed={false}
          />
        </p>
      )}
      list={(face) => (
        <>
          <p class="flashcard-prompt">{face().question}</p>
          <p class="flashcard-hint">
            Name {face().items.length} items, then check yourself.
          </p>
        </>
      )}
      feynman={(face) => (
        <>
          <p class="flashcard-prompt">{face().prompt}</p>
          <p class="flashcard-hint">
            Explain it out loud in plain language before you flip.
          </p>
        </>
      )}
    />
  );
}

export function FlashcardAnswer(props: FlashcardPromptProps): JSX.Element {
  return (
    <FaceView
      face={props.face}
      basic={(face) => <p class="flashcard-prompt">{face().back}</p>}
      cloze={(face) => (
        <p class="flashcard-prompt">
          <ClozeText
            text={face().text}
            hiddenParts={face().hiddenParts}
            isRevealed
          />
        </p>
      )}
      list={(face) => (
        <ul class="flashcard-list">
          <For each={face().items}>{(item) => <li>{item}</li>}</For>
        </ul>
      )}
      feynman={(face) => (
        <p class="flashcard-prompt">{face().referenceExplanation}</p>
      )}
    />
  );
}
