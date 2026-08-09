import { Show, createSignal, type JSX } from "solid-js";
import { Dropdown } from "../../shared/ui/Dropdown";
import { Icon } from "../../shared/ui/icons/Icon";
import { Meter } from "../../shared/ui/Meter";
import type { DueBreakdown } from "../../shared/models/units";

export type DueSectionProps = {
  readonly breakdown: DueBreakdown;
  readonly onReviewFlashcards: () => void;
  readonly onReviewTest: () => void;
};

class DueMath {
  static totalDue(breakdown: DueBreakdown): number {
    return breakdown.flashcardsDue + breakdown.testItemsDue + breakdown.notesDue;
  }
}

export function DueSection(props: DueSectionProps): JSX.Element {
  const [isMenuOpen, setMenuOpen] = createSignal(false);
  const totalDue = (): number => DueMath.totalDue(props.breakdown);

  const choose = (start: () => void): void => {
    setMenuOpen(false);
    start();
  };

  return (
    <section class="due" aria-labelledby="due-heading">
      <div class="due-head">
        <h2 class="section-label" id="due-heading">
          Due today
        </h2>
        <span class="due-progress">
          {props.breakdown.doneToday} of {props.breakdown.totalToday} done
        </span>
      </div>

      <Meter done={props.breakdown.doneToday} total={props.breakdown.totalToday} />

      <div class="due-foot">
        <ul class="due-breakdown">
          <li class="due-item" classList={{ "is-clear": props.breakdown.flashcardsDue === 0 }}>
            <Icon name="flashcards" size="sm" />
            <span class="due-count">{props.breakdown.flashcardsDue}</span> flashcards
          </li>
          <li class="due-item" classList={{ "is-clear": props.breakdown.testItemsDue === 0 }}>
            <Icon name="test" size="sm" />
            <span class="due-count">{props.breakdown.testItemsDue}</span> test items
          </li>
          <li class="due-item" classList={{ "is-clear": props.breakdown.notesDue === 0 }}>
            <Icon name="note" size="sm" />
            <span class="due-count">{props.breakdown.notesDue}</span> notes
          </li>
        </ul>

        <Show when={totalDue() > 0}>
          <div class="due-action">
            <button
              class="btn btn-primary btn-lg"
              type="button"
              aria-expanded={isMenuOpen()}
              onClick={() => setMenuOpen(!isMenuOpen())}
            >
              <Icon name="study" size="sm" />
              Review {totalDue()} items
            </button>
            <Dropdown
              isOpen={isMenuOpen()}
              onDismiss={() => setMenuOpen(false)}
              items={[
                {
                  label: "Flashcards",
                  icon: "flashcards",
                  hint: `${props.breakdown.flashcardsDue} due`,
                  onSelect: () => choose(props.onReviewFlashcards),
                },
                {
                  label: "Test",
                  icon: "test",
                  hint: `${props.breakdown.testItemsDue} due`,
                  onSelect: () => choose(props.onReviewTest),
                },
              ]}
            />
          </div>
        </Show>
      </div>
    </section>
  );
}
