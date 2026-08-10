import { For, createSignal, onCleanup, onMount, type JSX } from "solid-js";
import { Icon } from "../../shared/ui/icons/Icon";
import type { AssessmentItem } from "./assessment-models";

const ESCAPE_KEY = "Escape";
const CORRECT_OPTION_ID = 0;

export type EditedTestItem = {
  readonly question: string;
  readonly correctAnswer: string;
  readonly wrongAnswers: readonly string[];
};

export type TestItemEditorProps = {
  readonly item: AssessmentItem;
  readonly onSave: (edited: EditedTestItem) => void;
  readonly onCancel: () => void;
};

export function TestItemEditor(props: TestItemEditorProps): JSX.Element {
  const [question, setQuestion] = createSignal(props.item.question);
  const [answers, setAnswers] = createSignal<readonly string[]>(
    props.item.options.map((option) => option.option),
  );
  const [correctIndex, setCorrectIndex] = createSignal(
    Math.max(
      0,
      props.item.options.findIndex(
        (option) => option.id === CORRECT_OPTION_ID,
      ),
    ),
  );

  const isIncomplete = (): boolean =>
    question().trim().length === 0 ||
    answers().some((answer) => answer.trim().length === 0);

  const changeAnswer = (index: number, value: string): void => {
    setAnswers(
      answers().map((answer, position) =>
        position === index ? value : answer,
      ),
    );
  };

  const removeAnswer = (index: number): void => {
    setAnswers(answers().filter((_, position) => position !== index));

    if (correctIndex() >= index && correctIndex() > 0) {
      setCorrectIndex(correctIndex() - 1);
    }
  };

  const save = (event: Event): void => {
    event.preventDefault();
    if (isIncomplete()) return;

    props.onSave({
      question: question().trim(),
      correctAnswer: answers()[correctIndex()]?.trim() ?? "",
      wrongAnswers: answers()
        .filter((_, position) => position !== correctIndex())
        .map((answer) => answer.trim()),
    });
  };

  onMount(() => {
    const dismissOnEscape = (event: KeyboardEvent): void => {
      if (event.key === ESCAPE_KEY) props.onCancel();
    };

    document.addEventListener("keydown", dismissOnEscape);
    onCleanup(() => document.removeEventListener("keydown", dismissOnEscape));
  });

  return (
    <div
      class="modal-backdrop"
      onClick={(event) => {
        if (event.target === event.currentTarget) props.onCancel();
      }}
    >
      <form
        class="modal modal-wide"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        onSubmit={save}
      >
        <div class="modal-head">
          <div class="modal-heading">
            <h2 class="modal-title" id="dialog-title">
              Edit question
            </h2>
            <span class="modal-text">
              Changes apply the next time this question comes up.
            </span>
          </div>
          <button
            class="btn btn-quiet btn-icon"
            type="button"
            aria-label="Close dialog"
            onClick={() => props.onCancel()}
          >
            <Icon name="closePlain" size="sm" />
          </button>
        </div>

        <div class="modal-body">
          <div class="field">
            <label for="test-question">Question</label>
            <textarea
              class="input"
              id="test-question"
              rows="3"
              value={question()}
              onInput={(event) => setQuestion(event.currentTarget.value)}
            />
          </div>

          <div class="answer-legend">
            <span>Answers</span>
            <button
              class="btn"
              type="button"
              onClick={() => setAnswers([...answers(), ""])}
            >
              Add answer
            </button>
          </div>

          <div class="answer-rows">
            <For each={answers()}>
              {(answer, index) => (
                <div class="answer-row">
                  <label class="answer-correct">
                    <input
                      type="radio"
                      name="correct-answer"
                      checked={correctIndex() === index()}
                      aria-label={`Mark "${answer}" as the correct answer`}
                      onChange={() => setCorrectIndex(index())}
                    />
                    Correct
                  </label>
                  <input
                    class="input"
                    type="text"
                    value={answer}
                    aria-label={`Answer ${index() + 1}`}
                    onInput={(event) =>
                      changeAnswer(index(), event.currentTarget.value)
                    }
                  />
                  <button
                    class="btn btn-quiet btn-icon"
                    type="button"
                    aria-label={`Remove ${answer}`}
                    onClick={() => removeAnswer(index())}
                  >
                    <Icon name="trash" size="sm" />
                  </button>
                </div>
              )}
            </For>
          </div>
        </div>

        <div class="modal-foot">
          <button class="btn" type="button" onClick={() => props.onCancel()}>
            Cancel
          </button>
          <button
            class="btn btn-primary"
            type="submit"
            disabled={isIncomplete()}
          >
            Save question
          </button>
        </div>
      </form>
    </div>
  );
}
