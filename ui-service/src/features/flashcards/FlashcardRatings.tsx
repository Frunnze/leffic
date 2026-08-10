import { For, type JSX } from "solid-js";
import { IntervalLabel } from "./interval-label";
import type { FlashcardRating, RatingIntervals } from "./flashcard-models";

type RatingChoice = {
  readonly rating: FlashcardRating;
  readonly label: string;
  readonly toneClass: string;
};

const RATING_CHOICES: readonly RatingChoice[] = [
  { rating: 1, label: "Again", toneClass: "rating-miss" },
  { rating: 2, label: "Hard", toneClass: "rating-slow" },
  { rating: 3, label: "Good", toneClass: "rating-hit" },
  { rating: 4, label: "Easy", toneClass: "rating-hit" },
];

export type FlashcardRatingsProps = {
  readonly intervals: RatingIntervals | null;
  readonly onRate: (rating: FlashcardRating) => void;
};

export function FlashcardRatings(props: FlashcardRatingsProps): JSX.Element {
  const intervalLabel = (rating: FlashcardRating): string => {
    const seconds = props.intervals;

    if (seconds === null) return "";

    return IntervalLabel.fromSeconds(seconds[rating]);
  };

  return (
    <div class="review-actions">
      <For each={RATING_CHOICES}>
        {(choice) => (
          <button
            class={`rating ${choice.toneClass}`}
            type="button"
            onClick={() => props.onRate(choice.rating)}
          >
            <kbd class="kbd">{choice.rating}</kbd>
            <span class="rating-label">{choice.label}</span>
            <span class="rating-interval">{intervalLabel(choice.rating)}</span>
          </button>
        )}
      </For>
    </div>
  );
}
