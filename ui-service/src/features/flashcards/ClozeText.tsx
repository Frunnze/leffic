import { For, type JSX } from "solid-js";
import { ClozeSplit } from "./cloze-split";

export type ClozeTextProps = {
  readonly text: string;
  readonly hiddenParts: readonly string[];
  readonly isRevealed: boolean;
};

export function ClozeText(props: ClozeTextProps): JSX.Element {
  const pieces = (): ReturnType<typeof ClozeSplit.pieces> =>
    ClozeSplit.pieces(props.text, props.hiddenParts);

  return (
    <For each={pieces()}>
      {(piece) =>
        piece.isHidden ? (
          <mark
            class="cloze-blank"
            classList={{ "is-revealed": props.isRevealed }}
          >
            {props.isRevealed ? piece.text : " ".repeat(piece.text.length)}
          </mark>
        ) : (
          <span>{piece.text}</span>
        )
      }
    </For>
  );
}
