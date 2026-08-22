import type { JSX } from "solid-js";
import { FaceView } from "./FaceView";
import { FlashcardTextArea } from "./FlashcardTextArea";
import type { FlashcardFace } from "./flashcard-models";

const LINES_APART = "\n";
const SHORT_ROWS = 2;
const MEDIUM_ROWS = 3;
const TALL_ROWS = 4;

type FlashcardFieldsProps = {
  readonly face: FlashcardFace;
  readonly onChange: (face: FlashcardFace) => void;
};

export function FlashcardFields(props: FlashcardFieldsProps): JSX.Element {
  return (
    <FaceView
      face={props.face}
      basic={(face) => (
        <>
          <FlashcardTextArea
            id="card-front"
            label="Front"
            rows={MEDIUM_ROWS}
            value={face().front}
            onInput={(front) => {
              props.onChange({ ...face(), front });
            }}
          />
          <FlashcardTextArea
            id="card-back"
            label="Back"
            rows={MEDIUM_ROWS}
            value={face().back}
            onInput={(back) => {
              props.onChange({ ...face(), back });
            }}
          />
        </>
      )}
      cloze={(face) => (
        <>
          <FlashcardTextArea
            id="card-text"
            label="Sentence"
            rows={MEDIUM_ROWS}
            value={face().text}
            onInput={(text) => {
              props.onChange({ ...face(), text });
            }}
          />
          <FlashcardTextArea
            id="card-hidden"
            label="Hidden parts, one per line"
            rows={MEDIUM_ROWS}
            value={face().hiddenParts.join(LINES_APART)}
            onInput={(written) => {
              props.onChange({
                ...face(),
                hiddenParts: written.split(LINES_APART),
              });
            }}
          />
        </>
      )}
      list={(face) => (
        <>
          <FlashcardTextArea
            id="card-question"
            label="Question"
            rows={SHORT_ROWS}
            value={face().question}
            onInput={(question) => {
              props.onChange({ ...face(), question });
            }}
          />
          <FlashcardTextArea
            id="card-items"
            label="Items, one per line"
            rows={TALL_ROWS}
            value={face().items.join(LINES_APART)}
            onInput={(written) => {
              props.onChange({ ...face(), items: written.split(LINES_APART) });
            }}
          />
        </>
      )}
      feynman={(face) => (
        <>
          <FlashcardTextArea
            id="card-prompt"
            label="Explain this"
            rows={SHORT_ROWS}
            value={face().prompt}
            onInput={(prompt) => {
              props.onChange({ ...face(), prompt });
            }}
          />
          <FlashcardTextArea
            id="card-reference"
            label="Reference explanation"
            rows={TALL_ROWS}
            value={face().referenceExplanation}
            onInput={(referenceExplanation) => {
              props.onChange({ ...face(), referenceExplanation });
            }}
          />
        </>
      )}
    />
  );
}
