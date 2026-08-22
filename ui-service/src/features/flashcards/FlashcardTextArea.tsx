import type { JSX } from "solid-js";

type FlashcardTextAreaProps = {
  readonly id: string;
  readonly label: string;
  readonly rows: number;
  readonly value: string;
  readonly onInput: (value: string) => void;
};

export function FlashcardTextArea(props: FlashcardTextAreaProps): JSX.Element {
  return (
    <div class="field">
      <label for={props.id}>{props.label}</label>
      <textarea
        class="input"
        id={props.id}
        rows={props.rows}
        value={props.value}
        onInput={(event) => {
          props.onInput(event.currentTarget.value);
        }}
      />
    </div>
  );
}
