import { Match, Switch, type Accessor, type JSX } from "solid-js";
import type {
  BasicFace,
  ClozeFace,
  FeynmanFace,
  FlashcardFace,
  ListFace,
} from "./flashcard-models";

type FaceViewProps = {
  readonly face: FlashcardFace;
  readonly basic: (face: Accessor<BasicFace>) => JSX.Element;
  readonly cloze: (face: Accessor<ClozeFace>) => JSX.Element;
  readonly list: (face: Accessor<ListFace>) => JSX.Element;
  readonly feynman: (face: Accessor<FeynmanFace>) => JSX.Element;
};

export function FaceView(props: FaceViewProps): JSX.Element {
  return (
    <Switch>
      <Match when={props.face.kind === "basic" && props.face}>
        {(face) => props.basic(face)}
      </Match>

      <Match when={props.face.kind === "cloze" && props.face}>
        {(face) => props.cloze(face)}
      </Match>

      <Match when={props.face.kind === "list" && props.face}>
        {(face) => props.list(face)}
      </Match>

      <Match when={props.face.kind === "feynman" && props.face}>
        {(face) => props.feynman(face)}
      </Match>
    </Switch>
  );
}
