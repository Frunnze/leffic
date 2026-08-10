import { HttpClient } from "../../shared/api/http";
import { Json, type JsonObject } from "../../shared/api/json";
import type {
  Flashcard,
  FlashcardDeck,
  FlashcardRating,
  FlashcardReviewResult,
  FsrsCard,
  RatingIntervals,
} from "./flashcard-models";

export type DeckScope = "flashcard_deck" | "folder";

export class FlashcardsApi {
  static async deck(scope: DeckScope, scopeId: string): Promise<FlashcardDeck | null> {
    const query = new URLSearchParams({ [`${scope}_id`]: scopeId }).toString();
    const response = await HttpClient.send({
      endpoint: `/api/content/flashcards?${query}`,
    });

    if (!response.ok) return null;

    const payload: unknown = await response.json();
    const root = Json.object(payload, "deck");
    const total = Json.numberOr(root.total_flashcards, 0);

    if (total === 0) return null;

    const rawCards = Json.array(root.flashcards, "deck.flashcards");

    return {
      totalFlashcards: total,
      flashcards: rawCards.map((entry, index) =>
        FlashcardsApi.toFlashcard(Json.object(entry, `deck.flashcards[${index}]`)),
      ),
    };
  }

  static async ratingIntervals(
    card: FsrsCard | null,
  ): Promise<RatingIntervals | null> {
    const response = await HttpClient.send({
      endpoint: "/api/scheduler/public/ratings-times",
      method: "POST",
      body: { card },
    });

    if (!response.ok) return null;

    const payload: unknown = await response.json();
    const intervals = Json.object(payload, "ratingIntervals");

    return {
      1: Json.numberOr(intervals["1"], 0),
      2: Json.numberOr(intervals["2"], 0),
      3: Json.numberOr(intervals["3"], 0),
      4: Json.numberOr(intervals["4"], 0),
    };
  }

  static async review(
    flashcardId: string,
    rating: FlashcardRating,
  ): Promise<FlashcardReviewResult> {
    const payload = await HttpClient.json({
      endpoint: "/api/content/review-flashcard",
      method: "POST",
      body: { flashcard_id: flashcardId, rating },
    });
    const result = Json.object(payload, "reviewResult");

    return {
      dueDate: Json.string(result.due_date, "reviewResult.due_date"),
      newFsrsCard: Json.object(result.new_fsrs_card, "reviewResult.new_fsrs_card"),
    };
  }

  static async update(
    flashcardId: string,
    front: string,
    back: string,
  ): Promise<void> {
    await HttpClient.json({
      endpoint: "/api/content/update-flashcard",
      method: "PATCH",
      body: { flashcard_id: Number(flashcardId), content: { front, back } },
    });
  }

  static async remove(flashcardId: string): Promise<void> {
    await HttpClient.send({
      endpoint: `/api/content/delete-flashcard/?flashcard_id=${flashcardId}`,
      method: "DELETE",
    });
  }

  private static toFlashcard(raw: JsonObject): Flashcard {
    const content = Json.object(raw.content, "flashcard.content");

    return {
      id: Json.identifier(raw.id, "flashcard.id"),
      front: Json.stringOr(content.front, ""),
      back: Json.stringOr(content.back, ""),
      nextReview: Json.stringOrNull(raw.next_review),
      fsrsCard: Json.objectOrNull(raw.fsrs_card),
    };
  }
}
