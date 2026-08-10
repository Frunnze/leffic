import { For, Show, type JSX } from "solid-js";
import { AssessmentProgress } from "./assessment-progress";
import { TestItemActions } from "./TestItemActions";
import { Meter } from "../../shared/ui/Meter";
import type { AssessmentItem } from "./assessment-models";
import type { EditedTestItem } from "./TestItemEditor";

export type AssessmentQuestionProps = {
  readonly item: AssessmentItem;
  readonly chosenAnswers: readonly number[];
  readonly position: number;
  readonly totalItems: number;
  readonly onChoose: (optionId: number) => void;
  readonly onEdit: (edited: EditedTestItem) => void;
  readonly onBack: () => void;
  readonly onNext: () => void;
};

export function AssessmentQuestion(props: AssessmentQuestionProps): JSX.Element {
  const isLastQuestion = (): boolean => props.position >= props.totalItems;

  return (
    <>
      <Meter
        leadingLabel={`Question ${props.position} of ${props.totalItems}`}
        trailingLabel={`${Math.max(0, props.totalItems - props.position)} to go`}
        done={props.position}
        total={props.totalItems}
      />

      <div class="test-card">
        <TestItemActions item={props.item} onSave={props.onEdit} />
        <h1 class="test-question">{props.item.question}</h1>
        <div class="test-options">
          <For each={props.item.options}>
            {(option, index) => (
              <button
                class="test-option"
                type="button"
                aria-pressed={props.chosenAnswers.includes(option.id)}
                onClick={() => props.onChoose(option.id)}
              >
                <span class="test-key">
                  {AssessmentProgress.optionLetter(index())}
                </span>
                {option.option}
              </button>
            )}
          </For>
        </div>
      </div>

      <div class="test-nav">
        <button
          class="btn"
          type="button"
          disabled={props.position <= 1}
          onClick={() => props.onBack()}
        >
          Back
        </button>
        <button class="btn btn-primary" type="button" onClick={() => props.onNext()}>
          <Show when={isLastQuestion()} fallback="Next">
            Finish
          </Show>
        </button>
      </div>
    </>
  );
}
