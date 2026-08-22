import { Show, type JSX } from "solid-js";
import { FLASHCARD_TYPES, TEST_TYPES } from "./import-options";
import { GenerationChoice } from "./GenerationChoice";
import type { UnitChoice } from "./import-options";

type GenerationChoicesProps = {
  readonly isNoteAlreadyMade: boolean;
  readonly flashcards: UnitChoice;
  readonly test: UnitChoice;
  readonly note: UnitChoice;
  readonly onFlashcardsChange: (choice: UnitChoice) => void;
  readonly onTestChange: (choice: UnitChoice) => void;
  readonly onNoteChange: (choice: UnitChoice) => void;
};

export function GenerationChoices(
  props: GenerationChoicesProps,
): JSX.Element {
  return (
    <>
      <h3 class="section-label choice-heading">Generate</h3>
      <GenerationChoice
        name="flashcards"
        label="Flashcards"
        hint="Recall one fact at a time"
        types={FLASHCARD_TYPES}
        choice={props.flashcards}
        onChange={props.onFlashcardsChange}
      />
      <GenerationChoice
        name="test"
        label="Test"
        hint="Check what stuck"
        types={TEST_TYPES}
        choice={props.test}
        onChange={props.onTestChange}
      />
      <Show when={!props.isNoteAlreadyMade}>
        <GenerationChoice
          name="note"
          label="Note"
          hint="Read it through once"
          types={[]}
          choice={props.note}
          onChange={props.onNoteChange}
        />
      </Show>
    </>
  );
}
