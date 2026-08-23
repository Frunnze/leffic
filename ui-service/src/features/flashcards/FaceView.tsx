import { Show, type JSX } from "solid-js";
import type { FlashcardFace } from "./flashcard-models";

type FaceViewProps = {
  readonly face: FlashcardFace;
  readonly render: (face: FlashcardFace) => JSX.Element;
};

export function FaceView(props: FaceViewProps): JSX.Element {
  return (
    <Show keyed when={props.face}>
      {(face) => props.render(face)}
    </Show>
  );
}
