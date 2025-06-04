import { createSignal, For, Match, onMount, batch } from "solid-js";
import { useParams } from "@solidjs/router";
import { apiRequest } from "../utils/apiRequest";
import { createStore } from "solid-js/store";


const reviewTestItem = async (test_item_id, test_session, answers) => {
    await apiRequest({
      method: "POST",
      endpoint: "/api/content/review-test-item",
      body: {
        test_item_id: test_item_id,
        test_session: test_session,
        answers: answers
      }
    })
};

const getTest = async (params) => {
  const res = await apiRequest({
    endpoint: `/api/content/test-items?${new URLSearchParams(params).toString()}`,
  });
  const data = await res.json();
  console.log("TEST", data)
  return data;
};

export default function TestMainReview(props) {
  const params = useParams();
  const [test, setTest] = createStore();
  const [itemIndex, setItemIndex] = createSignal(Number(localStorage.getItem(`testLastIndex${params.id}`) || 0));
  const [showFinalResult, setShowFinalResult] = createSignal(false);
  const [page, setPage] = createSignal(Number(localStorage.getItem(`testPage${params.id}`) || 1));
  const [correctAns, setCorrectAns] = createSignal(0);
  const testParams = { [`${props.testReviewOrigin}_id`]: params.id, page: page(), per_page: 10 };

  onMount(async () => {
    const newTest = await getTest(testParams);
    setTest(newTest);
  });

  const moveToNextItem = async () => {
    if (test.test_items[itemIndex()].last_answers) {
      await reviewTestItem(
        test.test_items[itemIndex()].id,
        test.test_session,
        test.test_items[itemIndex()].last_answers
      );
    };

    if (test.test_items.length === itemIndex()+1) {
      // Check if there are more pages
      if (test.total_items === (test.page-1)*test.per_page+itemIndex()+1) {
        // Req to get the result
        const res = await apiRequest({
          endpoint: `/api/content/test-session-results?test_session=${test.test_session}`,
        });
        if (res.ok) {
          const resData = await res.json()
          setCorrectAns(resData.correct);
        };

        setShowFinalResult(true);
        localStorage.removeItem(`testLastIndex${params.id}`);
        localStorage.removeItem(`testPage${params.id}`);
      } else {
        // Request the next page
        const newTestPage = await getTest({...testParams, page: page() + 1});
        batch(() => {
          setItemIndex(0);
          localStorage.setItem(`testLastIndex${params.id}`, 0);
          setTest(newTestPage);
          localStorage.setItem(`testPage${params.id}`, page()+1)
          setPage(page()+1);
        });
      };
    } else {
      localStorage.setItem(`testLastIndex${params.id}`, itemIndex()+1);
      setItemIndex(itemIndex()+1);
    };
  };

  const moveToPrevItem = async () => {
    if (test.test_items[itemIndex()].last_answers) {
      await reviewTestItem(
        test.test_items[itemIndex()].id,
        test.test_session,
        test.test_items[itemIndex()].last_answers
      );
    };

    if (itemIndex() === 0) {
      if (test.page !== 1) {
        const newTestPage = await getTest({...testParams, page: page() - 1});
        batch(() => {
          setItemIndex(newTestPage.test_items.length - 1);
          localStorage.setItem(`testLastIndex${params.id}`, newTestPage.test_items.length - 1);
          setTest(newTestPage);
          localStorage.setItem(`testPage${params.id}`, page()-1)
          setPage(page()-1);
        });
      };
      return;
    };
    localStorage.setItem(`testLastIndex${params.id}`, itemIndex()-1);
    setItemIndex(itemIndex()-1);
  };

  const restartTest = async () => {
    setShowFinalResult(false);
    localStorage.setItem(`testPage${params.id}`, 1)
    localStorage.setItem(`testLastIndex${params.id}`, 0);
    const firstTestPage = await getTest({...testParams, page: 1});
    batch(() => {
      setItemIndex(0);
      setPage(1);
      setTest(firstTestPage);
    });
  };

  const chooseAnswer = (item, index) => { 
    setTest("test_items", itemIndex(), "last_answers", [item.id]);
  };

  return (
      <div class="min-h-[80vh] min-w-[80%] px-5 py-8 bg-primary shadow-sm flex flex-col gap-y-5 justify-center border border-tertiary-100/20 rounded-lg">
          <Switch>
              <Match when={showFinalResult()}>
                  <div class="flex flex-col justify-content items-center gap-y-5">
                  <div class="text-center text-3xl">
                      <span class="text-bold text-4xl">
                      Result:
                      </span>
                      <br/>
                      <span class="font-bold text-4xl">
                      {((correctAns()/test.total_items)*100).toFixed(1)}%
                      </span>
                      <br/>
                      <span class="text-2xl">
                      ({correctAns()}/{test.total_items})
                      </span>
                  </div>
                  <div onClick={restartTest} class="text-primary shadow cursor-pointer bg-secondary border border-primary rounded px-6 py-3 w-40 text-center">
                      Restart
                  </div>
                  </div>
              </Match>

              <Match when={test && test.total_items === 0}>
                  <div class="text-center flex flex-col w-full h-full justify-center items-center text-tertiary-100 font-medium text-lg">
                      <span class="flex w-full h-full justify-center items-center text-tertiary-100 font-medium text-xl">
                          This test has no items!
                      </span>
                  </div>
              </Match>
              
              <Match when={test.test_items}>
                  <span class="font-semibold text-center text-xl">
                      {test.test_items[itemIndex()].content.question}
                  </span>
                  <hr class="w-full border-tertiary-10 border-0.5"/>
                  <div class="rounded flex flex-col gap-y-5 text-center">
                      <For each={test.test_items[itemIndex()].content.shuffled_options}>
                      {(item, index) => (
                          <div
                          onClick={() => chooseAnswer(item, index())}
                          class="p-5 border hover:border-secondary rounded-sm cursor-pointer flex items-center justify-center transition-colors"
                          classList={{
                              "border-2": test.test_items[itemIndex()].last_answers?.includes(item.id),
                              "border-secondary": test.test_items[itemIndex()].last_answers?.includes(item.id),
                              "border-tertiary-100/20": !test.test_items[itemIndex()].last_answers?.includes(item.id),
                          }}
                          >
                          {item.option}
                          </div>
                      )}
                      </For>
                  </div>
                  <hr class="w-full border-tertiary-10 border-0.5"/>
                  <div class="flex justify-center items-center gap-x-10 text-primary">
                      <div onClick={() => moveToPrevItem()} class="shadow cursor-pointer bg-secondary border rounded px-6 py-3 w-40 text-center">
                      Back
                      </div>
                      <div class="flex items-center justify-center py-3 shadow bg-primary text-secondary border border-secondary rounded-full w-30 text-center">
                      {(test.page-1)*test.per_page+itemIndex()+1}/{test.total_items}
                      </div>
                      <div onClick={() => moveToNextItem()} class="shadow cursor-pointer bg-secondary border rounded px-6 py-3 w-40 text-center">
                      Next
                      </div>
                  </div>
              </Match>
          </Switch>
      </div>
    );
}