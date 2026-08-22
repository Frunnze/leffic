import {
  Match,
  Show,
  Switch,
  createSignal,
  onMount,
  untrack,
  type JSX,
} from "solid-js";
import { AssessmentApi, type AssessmentScope } from "./assessment-api";
import { AssessmentProgress } from "./assessment-progress";
import { AssessmentQuestion } from "./AssessmentQuestion";
import { AssessmentResult } from "./AssessmentResult";
import type {
  AssessmentAnswer,
  AssessmentItem,
  AssessmentPage,
  AssessmentSessionResult,
} from "./assessment-models";
import type { EditedTestItem } from "./TestItemEditor";

const FIRST_PAGE = 1;
const NOTHING_CORRECT: AssessmentSessionResult = { correct: 0 };

type AssessmentReviewProps = {
  readonly scope: AssessmentScope;
  readonly scopeId: string;
};

export function AssessmentReview(props: AssessmentReviewProps): JSX.Element {
  const [currentPage, setCurrentPage] = createSignal<AssessmentPage | null>(null);
  const [itemIndex, setItemIndex] = createSignal(
    untrack(() => AssessmentProgress.storedIndex(props.scopeId)),
  );
  const [chosenAnswers, setChosenAnswers] = createSignal<
    Readonly<Record<string, readonly AssessmentAnswer[]>>
  >({});
  const [result, setResult] = createSignal<AssessmentSessionResult | null>(null);

  const itemOn = (page: AssessmentPage): AssessmentItem | undefined =>
    page.items[itemIndex()];

  const answersFor = (item: AssessmentItem): readonly AssessmentAnswer[] =>
    chosenAnswers()[item.id] ?? item.lastAnswers;

  const positionOn = (page: AssessmentPage): number =>
    AssessmentProgress.overallPosition(page.page, page.perPage, itemIndex());

  const loadPage = async (number: number): Promise<AssessmentPage> => {
    const loaded = await AssessmentApi.page(props.scope, props.scopeId, number);
    setCurrentPage(loaded);

    return loaded;
  };

  onMount(() => void loadPage(AssessmentProgress.storedPage(props.scopeId)));

  const submitCurrent = async (
    page: AssessmentPage,
    item: AssessmentItem,
  ): Promise<void> => {
    const answers = answersFor(item);
    if (answers.length === 0) return;

    await AssessmentApi.submitAnswer(item.id, page.testSession, answers);
  };

  const finish = async (page: AssessmentPage): Promise<void> => {
    const outcome = await AssessmentApi.sessionResult(page.testSession);
    setResult(outcome ?? NOTHING_CORRECT);
    AssessmentProgress.forget(props.scopeId);
  };

  const goToNext = async (
    page: AssessmentPage,
    item: AssessmentItem,
  ): Promise<void> => {
    await submitCurrent(page, item);

    if (itemIndex() + 1 < page.items.length) {
      AssessmentProgress.remember(props.scopeId, page.page, itemIndex() + 1);
      setItemIndex(itemIndex() + 1);
      return;
    }

    if (positionOn(page) >= page.totalItems) {
      await finish(page);
      return;
    }

    await loadPage(page.page + 1);
    AssessmentProgress.remember(props.scopeId, page.page + 1, 0);
    setItemIndex(0);
  };

  const goToPrevious = async (
    page: AssessmentPage,
    item: AssessmentItem,
  ): Promise<void> => {
    await submitCurrent(page, item);

    if (itemIndex() > 0) {
      AssessmentProgress.remember(props.scopeId, page.page, itemIndex() - 1);
      setItemIndex(itemIndex() - 1);
      return;
    }

    const previousNumber = Math.max(FIRST_PAGE, page.page - 1);
    const previous = await loadPage(previousNumber);
    const lastIndex = Math.max(0, previous.items.length - 1);
    AssessmentProgress.remember(props.scopeId, previousNumber, lastIndex);
    setItemIndex(lastIndex);
  };

  const saveQuestion = async (
    page: AssessmentPage,
    item: AssessmentItem,
    edited: EditedTestItem,
  ): Promise<void> => {
    await AssessmentApi.updateItem(item.id, edited);
    await loadPage(page.page);
  };

  const restart = async (): Promise<void> => {
    setResult(null);
    setChosenAnswers({});
    AssessmentProgress.remember(props.scopeId, FIRST_PAGE, 0);
    setItemIndex(0);
    await loadPage(FIRST_PAGE);
  };

  const chooseAnswer = (
    item: AssessmentItem,
    answer: AssessmentAnswer,
  ): void => {
    setChosenAnswers({ ...chosenAnswers(), [item.id]: [answer] });
  };

  return (
    <div class="test-inner">
      <Show when={currentPage()}>
        {(page) => (
          <Switch>
            <Match when={result()}>
              {(finished) => (
                <AssessmentResult
                  correct={finished().correct}
                  total={page().totalItems}
                  onRetake={() => void restart()}
                />
              )}
            </Match>

            <Match when={page().totalItems === 0}>
              <div class="state">
                <span class="state-title">This test has no questions yet</span>
                <span class="state-text">
                  Import a file, a link or a topic and Leffic will write
                  questions from it.
                </span>
              </div>
            </Match>

            <Match when={itemOn(page())}>
              {(item) => (
                <AssessmentQuestion
                  item={item()}
                  chosenAnswers={answersFor(item())}
                  position={positionOn(page())}
                  totalItems={page().totalItems}
                  onChoose={(answer) => { chooseAnswer(item(), answer); }}
                  onEdit={(edited) => void saveQuestion(page(), item(), edited)}
                  onBack={() => void goToPrevious(page(), item())}
                  onNext={() => void goToNext(page(), item())}
                />
              )}
            </Match>
          </Switch>
        )}
      </Show>
    </div>
  );
}
