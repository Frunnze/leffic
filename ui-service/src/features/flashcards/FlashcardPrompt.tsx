import type { JSX } from "solid-js";
import { FaceView } from "./FaceView";
import { FlashcardFaceHandlers } from "./flashcard-face-handlers";
import type { FlashcardFace } from "./flashcard-models";

type FlashcardPromptProps = {
  readonly face: FlashcardFace;
};

export function FlashcardPrompt(props: FlashcardPromptProps): JSX.Element {
  return (
    <FaceView
      face={props.face}
      render={(face) => FlashcardFaceHandlers.prompt(face)}
    />
  );
}

export function FlashcardAnswer(props: FlashcardPromptProps): JSX.Element {
  return (
    <FaceView
      face={props.face}
      render={(face) => FlashcardFaceHandlers.answer(face)}
    />
  );
}
