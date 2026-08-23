import type { JSX } from "solid-js";
import { FaceView } from "./FaceView";
import { FlashcardFaceHandlers } from "./flashcard-face-handlers";
import type { FlashcardFace } from "./flashcard-models";

type FlashcardFieldsProps = {
  readonly face: FlashcardFace;
  readonly onChange: (face: FlashcardFace) => void;
};

export function FlashcardFields(props: FlashcardFieldsProps): JSX.Element {
  return (
    <FaceView
      face={props.face}
      render={(face) => FlashcardFaceHandlers.fields(face, props.onChange)}
    />
  );
}
