import { For, type JSX } from "solid-js";
import { ClozeText } from "./ClozeText";
import { FlashcardTextArea } from "./FlashcardTextArea";
import type {
  BasicFace,
  ClozeFace,
  FeynmanFace,
  FlashcardFace,
  ListFace,
} from "./flashcard-models";

type FaceChange = (face: FlashcardFace) => void;
type FaceProps<Face> = { readonly face: Face };
type FieldsProps<Face> = FaceProps<Face> & {
  readonly onChange: FaceChange;
};

const LINES_APART = "\n";
const SHORT_ROWS = 2;
const MEDIUM_ROWS = 3;
const TALL_ROWS = 4;

export const BasicFields = (
  props: FieldsProps<BasicFace>,
): JSX.Element => (
  <>
    <FlashcardTextArea
      id="card-front"
      label="Front"
      rows={MEDIUM_ROWS}
      value={props.face.front}
      onInput={(front) => { props.onChange({ ...props.face, front }); }}
    />
    <FlashcardTextArea
      id="card-back"
      label="Back"
      rows={MEDIUM_ROWS}
      value={props.face.back}
      onInput={(back) => { props.onChange({ ...props.face, back }); }}
    />
  </>
);

export const ClozeFields = (
  props: FieldsProps<ClozeFace>,
): JSX.Element => (
  <>
    <FlashcardTextArea
      id="card-text"
      label="Sentence"
      rows={MEDIUM_ROWS}
      value={props.face.text}
      onInput={(text) => { props.onChange({ ...props.face, text }); }}
    />
    <FlashcardTextArea
      id="card-hidden"
      label="Hidden parts, one per line"
      rows={MEDIUM_ROWS}
      value={props.face.hiddenParts.join(LINES_APART)}
      onInput={(written) => {
        props.onChange({
          ...props.face,
          hiddenParts: written.split(LINES_APART),
        });
      }}
    />
  </>
);

export const ListFields = (
  props: FieldsProps<ListFace>,
): JSX.Element => (
  <>
    <FlashcardTextArea
      id="card-question"
      label="Question"
      rows={SHORT_ROWS}
      value={props.face.question}
      onInput={(question) => {
        props.onChange({ ...props.face, question });
      }}
    />
    <FlashcardTextArea
      id="card-items"
      label="Items, one per line"
      rows={TALL_ROWS}
      value={props.face.items.join(LINES_APART)}
      onInput={(written) => {
        props.onChange({
          ...props.face,
          items: written.split(LINES_APART),
        });
      }}
    />
  </>
);

export const FeynmanFields = (
  props: FieldsProps<FeynmanFace>,
): JSX.Element => (
  <>
    <FlashcardTextArea
      id="card-prompt"
      label="Explain this"
      rows={SHORT_ROWS}
      value={props.face.prompt}
      onInput={(prompt) => { props.onChange({ ...props.face, prompt }); }}
    />
    <FlashcardTextArea
      id="card-reference"
      label="Reference explanation"
      rows={TALL_ROWS}
      value={props.face.referenceExplanation}
      onInput={(referenceExplanation) => {
        props.onChange({ ...props.face, referenceExplanation });
      }}
    />
  </>
);

export const BasicPrompt = (props: FaceProps<BasicFace>): JSX.Element => (
  <p class="flashcard-prompt">{props.face.front}</p>
);

export const ClozePrompt = (props: FaceProps<ClozeFace>): JSX.Element => (
  <p class="flashcard-prompt">
    <ClozeText
      text={props.face.text}
      hiddenParts={props.face.hiddenParts}
      isRevealed={false}
    />
  </p>
);

export const ListPrompt = (props: FaceProps<ListFace>): JSX.Element => (
  <>
    <p class="flashcard-prompt">{props.face.question}</p>
    <p class="flashcard-hint">
      Name {props.face.items.length} items, then check yourself.
    </p>
  </>
);

export const FeynmanPrompt = (props: FaceProps<FeynmanFace>): JSX.Element => (
  <p class="flashcard-prompt">{props.face.prompt}</p>
);

export const BasicAnswer = (props: FaceProps<BasicFace>): JSX.Element => (
  <p class="flashcard-prompt">{props.face.back}</p>
);

export const ClozeAnswer = (props: FaceProps<ClozeFace>): JSX.Element => (
  <p class="flashcard-prompt">
    <ClozeText
      text={props.face.text}
      hiddenParts={props.face.hiddenParts}
      isRevealed
    />
  </p>
);

export const ListAnswer = (props: FaceProps<ListFace>): JSX.Element => (
  <ul class="flashcard-list">
    <For each={props.face.items}>{(item) => <li>{item}</li>}</For>
  </ul>
);

export const FeynmanAnswer = (props: FaceProps<FeynmanFace>): JSX.Element => (
  <p class="flashcard-prompt">{props.face.referenceExplanation}</p>
);
