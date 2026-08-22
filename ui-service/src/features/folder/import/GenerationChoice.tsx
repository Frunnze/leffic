import { For, Show, createSignal, type JSX } from "solid-js";
import { ImportOptions, type CardTypeOption, type UnitChoice } from "./import-options";
import { TypeCount } from "./TypeCount";

type GenerationChoiceProps = {
  readonly name: string;
  readonly label: string;
  readonly hint: string;
  readonly types: readonly CardTypeOption[];
  readonly choice: UnitChoice;
  readonly onChange: (choice: UnitChoice) => void;
};

export function GenerationChoice(props: GenerationChoiceProps): JSX.Element {
  const [customTypes, setCustomTypes] = createSignal<readonly string[]>([]);

  const isCustom = (typeId: string): boolean =>
    customTypes().includes(typeId);

  const chooseCount = (typeId: string, count: number | null): void => {
    if (count !== null && isCustom(typeId)) {
      setCustomTypes(customTypes().filter((entry) => entry !== typeId));
    }

    props.onChange(ImportOptions.withCount(props.choice, typeId, count));
  };

  return (
    <div class="units-choice">
      <label class="choice-head">
        <input
          type="checkbox"
          checked={props.choice.isChosen}
          onChange={(event) =>
            { props.onChange({
              ...props.choice,
              isChosen: event.currentTarget.checked,
            }); }
          }
        />
        <span class="choice-name">{props.label}</span>
        <span class="choice-hint">{props.hint}</span>
      </label>

      <Show when={props.choice.isChosen && props.types.length > 0}>
        <div class="choice-options">
          <span class="option-label">Types and how many</span>
          <div class="type-rows">
            <For each={props.types}>
              {(type) => (
                <div class="type-row">
                  <span class="type-name">
                    <label class="check">
                      <input
                        type="checkbox"
                        checked={props.choice.chosenTypes.includes(type.id)}
                        disabled={!type.isSupported}
                        onChange={() =>
                          { props.onChange(
                            ImportOptions.withType(props.choice, type.id),
                          ); }
                        }
                      />
                      {type.label}
                    </label>
                  </span>

                  <Show when={props.choice.chosenTypes.includes(type.id)}>
                    <TypeCount
                      name={`${props.name}-${type.id}`}
                      count={props.choice.counts[type.id] ?? null}
                      isCustom={isCustom(type.id)}
                      onChoose={(count) => { chooseCount(type.id, count); }}
                      onCustom={() =>
                        setCustomTypes([...customTypes(), type.id])
                      }
                    />
                  </Show>
                </div>
              )}
            </For>
          </div>
        </div>
      </Show>
    </div>
  );
}
