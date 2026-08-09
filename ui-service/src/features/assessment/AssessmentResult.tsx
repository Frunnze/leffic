import type { JSX } from "solid-js";

export type AssessmentResultProps = {
  readonly correct: number;
  readonly total: number;
  readonly onRetake: () => void;
};

export function AssessmentResult(props: AssessmentResultProps): JSX.Element {
  const missed = (): number => Math.max(0, props.total - props.correct);

  return (
    <div class="test-card">
      <div class="test-result">
        <h1 class="section-label">Test complete</h1>
        <p class="test-score">
          {props.correct} / {props.total}
        </p>
        <p class="test-score-detail">
          The {missed()} you missed come back tomorrow. The rest are scheduled
          further out.
        </p>
        <div class="test-result-actions">
          <button class="btn btn-primary" type="button" onClick={() => props.onRetake()}>
            Retake test
          </button>
        </div>
      </div>
    </div>
  );
}
