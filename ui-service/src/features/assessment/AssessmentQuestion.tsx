import { For, Show, type JSX } from "solid-js";
import { AssessmentProgress } from "./assessment-progress";
import { TestItemActions } from "./TestItemActions";
import { Meter } from "../../shared/ui/Meter";
import type {
  AssessmentAnswer,
  AssessmentItem,
} from "./assessment-models";
import type { EditedTestItem } from "./TestItemEditor";

export type AssessmentQuestionProps = {
  readonly item: AssessmentItem;
  readonly chosenAnswers: readonly AssessmentAnswer[];
  readonly position: number;
  readonly totalItems: number;
  readonly onChoose: (answer: AssessmentAnswer) => void;
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
        <Show
          when={props.item.options.length > 0}
          fallback={
            <input
              class="input test-typed"
              type="text"
              aria-label="Your answer"
              placeholder="Type your answer"
              value={String(props.chosenAnswers[0] ?? "")}
              onInput={(event) => props.onChoose(event.currentTarget.value)}
            />
          }
        >
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
        </Show>
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
