import { Show, createSignal, type JSX } from "solid-js";
import { Dropdown } from "../../shared/ui/Dropdown";
import { Icon } from "../../shared/ui/icons/Icon";
import { TestItemEditor, type EditedTestItem } from "./TestItemEditor";
import type { AssessmentItem } from "./assessment-models";

export type TestItemActionsProps = {
  readonly item: AssessmentItem;
  readonly onSave: (edited: EditedTestItem) => void;
};

export function TestItemActions(props: TestItemActionsProps): JSX.Element {
  const [isMenuOpen, setMenuOpen] = createSignal(false);
  const [isEditing, setEditing] = createSignal(false);

  return (
    <>
      <div class="card-menu">
        <button
          class="btn btn-quiet btn-icon"
          type="button"
          aria-label="Actions for this question"
          aria-expanded={isMenuOpen()}
          onClick={() => setMenuOpen(!isMenuOpen())}
        >
          <Icon name="dots" size="sm" />
        </button>
        <Dropdown
          isOpen={isMenuOpen()}
          onDismiss={() => setMenuOpen(false)}
          items={[
            {
              label: "Edit question",
              icon: "note",
              onSelect: () => {
                setMenuOpen(false);
                setEditing(true);
              },
            },
          ]}
        />
      </div>

      <Show when={isEditing()}>
        <TestItemEditor
          item={props.item}
          onSave={(edited) => {
            setEditing(false);
            props.onSave(edited);
          }}
          onCancel={() => setEditing(false)}
        />
      </Show>
    </>
  );
}
