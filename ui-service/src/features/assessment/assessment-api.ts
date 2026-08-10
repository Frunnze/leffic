import { HttpClient } from "../../shared/api/http";
import { Json, type JsonObject } from "../../shared/api/json";
import type { EditedTestItem } from "./TestItemEditor";
import type {
  AssessmentItem,
  AssessmentOption,
  AssessmentPage,
  AssessmentSessionResult,
} from "./assessment-models";

export type AssessmentScope = "test" | "folder";

const ITEMS_PER_PAGE = 10;

export class AssessmentApi {
  static async page(
    scope: AssessmentScope,
    scopeId: string,
    page: number,
  ): Promise<AssessmentPage> {
    const query = new URLSearchParams({
      [`${scope}_id`]: scopeId,
      page: String(page),
      per_page: String(ITEMS_PER_PAGE),
    }).toString();
    const payload = await HttpClient.json({
      endpoint: `/api/content/test-items?${query}`,
    });
    const root = Json.object(payload, "assessmentPage");
    const rawItems = Json.array(root.test_items, "assessmentPage.test_items");

    return {
      testSession: Json.stringOr(root.test_session, ""),
      items: rawItems.map((entry, index) =>
        AssessmentApi.toItem(Json.object(entry, `testPage.test_items[${index}]`)),
      ),
      page: Json.numberOr(root.page, page),
      perPage: Json.numberOr(root.per_page, ITEMS_PER_PAGE),
      totalItems: Json.numberOr(root.total_items, 0),
    };
  }

  static async submitAnswer(
    testItemId: string,
    testSession: string,
    answers: readonly number[],
  ): Promise<void> {
    await HttpClient.send({
      endpoint: "/api/content/review-test-item",
      method: "POST",
      body: {
        test_item_id: testItemId,
        test_session: testSession,
        answers,
      },
    });
  }

  static async sessionResult(
    testSession: string,
  ): Promise<AssessmentSessionResult | null> {
    const response = await HttpClient.send({
      endpoint: `/api/content/test-session-results?test_session=${testSession}`,
    });

    if (!response.ok) return null;

    const payload: unknown = await response.json();

    return { correct: Json.numberOr(Json.object(payload, "result").correct, 0) };
  }

  static async updateItem(
    testItemId: string,
    edited: EditedTestItem,
  ): Promise<void> {
    await HttpClient.json({
      endpoint: "/api/content/update-test-item",
      method: "PATCH",
      body: {
        test_item_id: Number(testItemId),
        content: {
          question: edited.question,
          true_option: edited.correctAnswer,
          false_options: edited.wrongAnswers,
        },
      },
    });
  }

  private static toItem(raw: JsonObject): AssessmentItem {
    const content = Json.object(raw.content, "assessmentItem.content");
    const rawOptions = Json.array(
      content.shuffled_options,
      "assessmentItem.content.shuffled_options",
    );

    return {
      id: Json.identifier(raw.id, "assessmentItem.id"),
      question: Json.stringOr(content.question, ""),
      options: rawOptions.map((entry, index) =>
        AssessmentApi.toOption(Json.object(entry, `testItem.options[${index}]`)),
      ),
      lastAnswers: AssessmentApi.toAnswers(raw.last_answers),
    };
  }

  private static toOption(raw: JsonObject): AssessmentOption {
    return {
      id: Json.number(raw.id, "assessmentOption.id"),
      option: Json.stringOr(raw.option, ""),
    };
  }

  private static toAnswers(value: unknown): readonly number[] {
    if (!Array.isArray(value)) return [];

    return value.map((entry, index) =>
      Json.number(entry, `testItem.last_answers[${index}]`),
    );
  }
}
