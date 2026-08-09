import { Match, Switch, createSignal, onMount, type JSX } from "solid-js";
import { AssessmentApi, type AssessmentScope } from "./assessment-api";
import { AssessmentProgress } from "./assessment-progress";
import { AssessmentQuestion } from "./AssessmentQuestion";
import { AssessmentResult } from "./AssessmentResult";
import type { AssessmentItem, AssessmentPage } from "./assessment-models";

const FIRST_PAGE = 1;

export type AssessmentReviewProps = {
  readonly scope: AssessmentScope;
  readonly scopeId: string;
};

export function AssessmentReview(props: AssessmentReviewProps): JSX.Element {
  const [currentPage, setCurrentPage] = createSignal<AssessmentPage | null>(null);
  const [itemIndex, setItemIndex] = createSignal(
    AssessmentProgress.storedIndex(props.scopeId),
  );
  const [chosenAnswers, setChosenAnswers] = createSignal<
    Readonly<Record<string, readonly string[]>>
  >({});
  const [correctCount, setCorrectCount] = createSignal<number | null>(null);

  const currentItem = (): AssessmentItem | undefined =>
    currentPage()?.items[itemIndex()];

  const answersFor = (item: AssessmentItem): readonly string[] =>
    chosenAnswers()[item.id] ?? item.lastAnswers;

  const totalItems = (): number => currentPage()?.totalItems ?? 0;

  const loadPage = async (page: number): Promise<void> => {
    setCurrentPage(await AssessmentApi.page(props.scope, props.scopeId, page));
  };

  onMount(() => void loadPage(AssessmentProgress.storedPage(props.scopeId)));

  const position = (): number => {
    const page = currentPage();
    if (page === null) return 0;

    return AssessmentProgress.overallPosition(page.page, page.perPage, itemIndex());
  };

  const submitCurrent = async (): Promise<void> => {
    const page = currentPage();
    const item = currentItem();
    if (page === null || item === undefined) return;

    const answers = answersFor(item);
    if (answers.length === 0) return;

    await AssessmentApi.submitAnswer(item.id, page.testSession, answers);
  };

  const goToNext = async (): Promise<void> => {
    const page = currentPage();
    if (page === null) return;

    await submitCurrent();

    if (itemIndex() + 1 < page.items.length) {
      AssessmentProgress.remember(props.scopeId, page.page, itemIndex() + 1);
      setItemIndex(itemIndex() + 1);
      return;
    }

    if (position() >= page.totalItems) {
      const outcome = await AssessmentApi.sessionResult(page.testSession);
      setCorrectCount(outcome?.correct ?? 0);
      AssessmentProgress.forget(props.scopeId);
      return;
    }

    await loadPage(page.page + 1);
    AssessmentProgress.remember(props.scopeId, page.page + 1, 0);
    setItemIndex(0);
  };

  const goToPrevious = async (): Promise<void> => {
    const page = currentPage();
    if (page === null) return;

    await submitCurrent();

    if (itemIndex() > 0) {
      AssessmentProgress.remember(props.scopeId, page.page, itemIndex() - 1);
      setItemIndex(itemIndex() - 1);
      return;
    }

    if (page.page === FIRST_PAGE) return;

    await loadPage(page.page - 1);
    const lastIndex = Math.max(0, (currentPage()?.items.length ?? 1) - 1);
    AssessmentProgress.remember(props.scopeId, page.page - 1, lastIndex);
    setItemIndex(lastIndex);
  };

  const restart = async (): Promise<void> => {
    setCorrectCount(null);
    setChosenAnswers({});
    AssessmentProgress.remember(props.scopeId, FIRST_PAGE, 0);
    setItemIndex(0);
    await loadPage(FIRST_PAGE);
  };

  const chooseAnswer = (item: AssessmentItem, optionId: string): void => {
    setChosenAnswers({ ...chosenAnswers(), [item.id]: [optionId] });
  };

  return (
    <div class="test-inner">
      <Switch>
        <Match when={correctCount() !== null}>
          <AssessmentResult
            correct={correctCount() ?? 0}
            total={totalItems()}
            onRetake={() => void restart()}
          />
        </Match>

        <Match when={currentPage()?.totalItems === 0}>
          <div class="state">
            <span class="state-title">This test has no questions yet</span>
            <span class="state-text">
              Import a file, a link or a topic and Leffic will write questions
              from it.
            </span>
          </div>
        </Match>

        <Match when={currentItem()}>
          {(item) => (
            <AssessmentQuestion
              item={item()}
              chosenAnswers={answersFor(item())}
              position={position()}
              totalItems={totalItems()}
              onChoose={(optionId) => chooseAnswer(item(), optionId)}
              onBack={() => void goToPrevious()}
              onNext={() => void goToNext()}
            />
          )}
        </Match>
      </Switch>
    </div>
  );
}
