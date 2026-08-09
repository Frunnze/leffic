import { For, Match, Show, Switch, createSignal, onMount, type JSX } from "solid-js";
import { A } from "@solidjs/router";
import { FlashcardsApi, type DeckScope } from "./flashcards-api";
import { FlashcardQueue } from "./flashcard-queue";
import { FlashcardShortcuts } from "./flashcard-shortcuts";
import { IntervalLabel } from "./interval-label";
import { Meter } from "../../shared/ui/Meter";
import { Icon } from "../../shared/ui/icons/Icon";
import type {
  Flashcard,
  FlashcardRating,
  RatingIntervals,
} from "./flashcard-models";

type RatingChoice = {
  readonly rating: FlashcardRating;
  readonly label: string;
  readonly toneClass: string;
};

const HOME_ROUTE = "/folder/home";

const RATING_CHOICES: readonly RatingChoice[] = [
  { rating: 1, label: "Again", toneClass: "rating-miss" },
  { rating: 2, label: "Hard", toneClass: "rating-slow" },
  { rating: 3, label: "Good", toneClass: "rating-hit" },
  { rating: 4, label: "Easy", toneClass: "rating-hit" },
];

export type FlashcardsReviewProps = {
  readonly scope: DeckScope;
  readonly scopeId: string;
};

export function FlashcardsReview(props: FlashcardsReviewProps): JSX.Element {
  const [cards, setCards] = createSignal<readonly Flashcard[]>([]);
  const [totalToReview, setTotalToReview] = createSignal(0);
  const [reviewedCount, setReviewedCount] = createSignal(0);
  const [isAnswerShown, setAnswerShown] = createSignal(false);
  const [intervals, setIntervals] = createSignal<RatingIntervals | null>(null);
  const [isLoading, setLoading] = createSignal(true);

  const currentCard = (): Flashcard | undefined => cards()[0];

  const loadIntervals = async (card: Flashcard | undefined): Promise<void> => {
    if (card === undefined) return;

    setIntervals(await FlashcardsApi.ratingIntervals(card.fsrsCard));
  };

  const loadDeck = async (): Promise<readonly Flashcard[]> => {
    const deck = await FlashcardsApi.deck(props.scope, props.scopeId);
    if (deck === null) return [];

    setTotalToReview((current) => (current === 0 ? deck.totalFlashcards : current));

    return deck.flashcards;
  };

  onMount(async () => {
    const loaded = await loadDeck();
    setCards(loaded);
    await loadIntervals(loaded[0]);
    setLoading(false);
  });

  const revealAnswer = (): void => {
    setAnswerShown(true);
    void loadIntervals(currentCard());
  };

  const rate = async (rating: FlashcardRating): Promise<void> => {
    const reviewing = currentCard();
    if (reviewing === undefined) return;

    const outcome = await FlashcardsApi.review(reviewing.id, rating);

    if (!FlashcardQueue.isToday(new Date(outcome.dueDate))) {
      setReviewedCount(reviewedCount() + 1);
    }

    const remaining =
      cards().length === 1
        ? await loadDeck()
        : FlashcardQueue.afterReview(cards(), outcome);

    setCards(remaining);
    setAnswerShown(false);
    await loadIntervals(remaining[0]);
  };

  FlashcardShortcuts.bind({
    isAnswerShown,
    onReveal: revealAnswer,
    onRate: (rating) => void rate(rating),
  });

  const intervalLabel = (rating: FlashcardRating): string => {
    const seconds = intervals();
    if (seconds === null) return "";

    return IntervalLabel.fromSeconds(seconds[rating]);
  };

  return (
    <div class="review-inner">
      <Show when={totalToReview() > 0}>
        <Meter
          leadingLabel={`Reviewed ${reviewedCount()} of ${totalToReview()}`}
          trailingLabel={`${Math.max(0, totalToReview() - reviewedCount())} left`}
          done={reviewedCount()}
          total={totalToReview()}
        />
      </Show>

      <Switch>
        <Match when={isLoading()}>
          <div class="flashcard">
            <div class="flashcard-face">
              <p class="flashcard-prompt">Loading your cards…</p>
            </div>
          </div>
        </Match>

        <Match when={currentCard() === undefined}>
          <div class="state">
            <Icon name="success" />
            <span class="state-title">You're done for today</span>
            <span class="state-text">
              Every card in this deck is scheduled. The next one comes back when
              you're about to forget it.
            </span>
            <A class="btn" href={HOME_ROUTE}>
              Back to folder
            </A>
          </div>
        </Match>

        <Match when={currentCard()}>
          {(card) => (
            <>
              <div class="flashcard">
                <div class="flashcard-face">
                  <p class="flashcard-prompt">{card().front}</p>
                </div>
                <Show when={isAnswerShown()}>
                  <div class="flashcard-face flashcard-answer">
                    <p class="flashcard-prompt">{card().back}</p>
                  </div>
                </Show>
              </div>

              <Show
                when={isAnswerShown()}
                fallback={
                  <button
                    class="btn btn-primary btn-block btn-lg"
                    type="button"
                    onClick={revealAnswer}
                  >
                    Show answer <kbd class="kbd">Space</kbd>
                  </button>
                }
              >
                <div class="review-actions">
                  <For each={RATING_CHOICES}>
                    {(choice) => (
                      <button
                        class={`rating ${choice.toneClass}`}
                        type="button"
                        onClick={() => void rate(choice.rating)}
                      >
                        <kbd class="kbd">{choice.rating}</kbd>
                        <span class="rating-label">{choice.label}</span>
                        <span class="rating-interval">
                          {intervalLabel(choice.rating)}
                        </span>
                      </button>
                    )}
                  </For>
                </div>
              </Show>
            </>
          )}
        </Match>
      </Switch>
    </div>
  );
}
