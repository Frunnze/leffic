import { For, Show, type JSX } from "solid-js";

const PRESET_COUNTS: readonly number[] = [10, 20];

export type TypeCountProps = {
  readonly name: string;
  readonly count: number | null;
  readonly isCustom: boolean;
  readonly onChoose: (count: number | null) => void;
  readonly onCustom: () => void;
};

export function TypeCount(props: TypeCountProps): JSX.Element {
  const isPreset = (value: number): boolean =>
    !props.isCustom && props.count === value;

  return (
    <>
      <div class="segmented">
        <label class="segment">
          <input
            type="radio"
            name={props.name}
            checked={!props.isCustom && props.count === null}
            onChange={() => props.onChoose(null)}
          />
          <span class="segment-face">Auto</span>
        </label>

        <For each={PRESET_COUNTS}>
          {(preset) => (
            <label class="segment">
              <input
                type="radio"
                name={props.name}
                checked={isPreset(preset)}
                onChange={() => props.onChoose(preset)}
              />
              <span class="segment-face">{preset}</span>
            </label>
          )}
        </For>

        <label class="segment">
          <input
            type="radio"
            name={props.name}
            checked={props.isCustom}
            onChange={() => props.onCustom()}
          />
          <span class="segment-face">Custom</span>
        </label>
      </div>

      <Show when={props.isCustom}>
        <div class="count-custom">
          <input
            class="input"
            type="number"
            min="1"
            aria-label={`How many for ${props.name}`}
            value={props.count ?? ""}
            onInput={(event) =>
              props.onChoose(Number(event.currentTarget.value) || null)
            }
          />
        </div>
      </Show>
    </>
  );
}
