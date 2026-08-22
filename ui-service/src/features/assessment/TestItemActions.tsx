import { Show, createSignal, type JSX } from "solid-js";
import { CardMenu } from "../../shared/ui/CardMenu";
import { TestItemEditor, type EditedTestItem } from "./TestItemEditor";
import type { AssessmentItem } from "./assessment-models";

type TestItemActionsProps = {
  readonly item: AssessmentItem;
  readonly onSave: (edited: EditedTestItem) => void;
};

export function TestItemActions(props: TestItemActionsProps): JSX.Element {
  const [isEditing, setEditing] = createSignal(false);

  return (
    <>
      <div class="card-menu">
        <CardMenu
          label="Actions for this question"
          items={[
            {
              label: "Edit question",
              icon: "note",
              onSelect: () => setEditing(true),
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
