import { Match, Show, Switch, createSignal, onMount, type JSX } from "solid-js";
import { A } from "@solidjs/router";
import { FlashcardsApi, type DeckScope } from "./flashcards-api";
import { FlashcardActions } from "./FlashcardActions";
import { FlashcardRatings } from "./FlashcardRatings";
import { FlashcardAnswer, FlashcardPrompt } from "./FlashcardPrompt";
import { FlashcardQueue } from "./flashcard-queue";
import { FlashcardShortcuts } from "./flashcard-shortcuts";
import { MnemonicRequest } from "./mnemonic-request";
import { useAsk } from "../../shared/chatbot/AskContext";
import { Meter } from "../../shared/ui/Meter";
import { Icon } from "../../shared/ui/icons/Icon";
import type {
  Flashcard,
  FlashcardFace,
  FlashcardRating,
  RatingIntervals,
} from "./flashcard-models";

const HOME_ROUTE = "/folder/home";

type FlashcardsReviewProps = {
  readonly scope: DeckScope;
  readonly scopeId: string;
};

export function FlashcardsReview(props: FlashcardsReviewProps): JSX.Element {
  const ask = useAsk();
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

    setTotalToReview((current) =>
      current === 0 ? deck.totalFlashcards : current,
    );

    return deck.flashcards;
  };

  const openFirstCard = async (): Promise<void> => {
    const loaded = await loadDeck();
    setCards(loaded);
    await loadIntervals(loaded[0]);
    setLoading(false);
  };

  onMount(() => {
    void openFirstCard();
  });

  const revealAnswer = (): void => {
    setAnswerShown(true);
    void loadIntervals(currentCard());
  };

  const rate = async (
    reviewing: Flashcard,
    rating: FlashcardRating,
  ): Promise<void> => {
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

  const askForMnemonic = (card: Flashcard): void => {
    ask.askAbout(MnemonicRequest.forCard(card));
  };

  const saveCard = async (
    editing: Flashcard,
    face: FlashcardFace,
  ): Promise<void> => {
    await FlashcardsApi.update(editing.id, face);
    setCards([{ ...editing, face }, ...cards().slice(1)]);
  };

  const deleteCard = async (removing: Flashcard): Promise<void> => {
    await FlashcardsApi.remove(removing.id);
    setTotalToReview(Math.max(0, totalToReview() - 1));
    setAnswerShown(false);

    const remaining = cards().slice(1);
    setCards(remaining.length === 0 ? await loadDeck() : remaining);
    await loadIntervals(currentCard());
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
          {(card) => {
            FlashcardShortcuts.bind({
              isAnswerShown,
              onReveal: revealAnswer,
              onRate: (rating) => void rate(card(), rating),
            });

            return (
              <>
                <div class="flashcard">
                  <FlashcardActions
                    card={card()}
                    onSave={(face) => void saveCard(card(), face)}
                    onDelete={() => void deleteCard(card())}
                    onMnemonic={() => {
                      askForMnemonic(card());
                    }}
                  />
                  <div class="flashcard-face">
                    <FlashcardPrompt face={card().face} />
                  </div>
                  <Show when={isAnswerShown()}>
                    <div class="flashcard-face flashcard-answer">
                      <FlashcardAnswer face={card().face} />
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
                  <FlashcardRatings
                    intervals={intervals()}
                    onRate={(rating) => void rate(card(), rating)}
                  />
                </Show>
              </>
            );
          }}
        </Match>
      </Switch>
    </div>
  );
}
