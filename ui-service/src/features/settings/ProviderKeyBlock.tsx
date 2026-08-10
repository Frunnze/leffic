import { Show, createSignal, type JSX } from "solid-js";
import { Money } from "./money";
import type { ProviderKey } from "./account-api";

export type Provider = {
  readonly id: string;
  readonly name: string;
};

export type ProviderKeyBlockProps = {
  readonly provider: Provider;
  readonly savedKey: ProviderKey | undefined;
  readonly onSave: (key: string, monthlyLimitCents: number | null) => void;
  readonly onRemove: () => void;
};

export function ProviderKeyBlock(props: ProviderKeyBlockProps): JSX.Element {
  const [typedKey, setTypedKey] = createSignal("");
  const [isReplacing, setReplacing] = createSignal(false);
  const [limitText, setLimitText] = createSignal<string | null>(null);

  const shownLimit = (): string =>
    limitText() ?? Money.toDollarText(props.savedKey?.monthlyLimitCents ?? null);

  const isSealed = (): boolean =>
    props.savedKey !== undefined && !isReplacing();

  const save = (): void => {
    props.onSave(typedKey().trim(), Money.toCentsOrNull(shownLimit()));
    setTypedKey("");
    setReplacing(false);
  };

  const usage = (): string => {
    const spent = props.savedKey?.spentCents ?? 0;

    if (spent === 0) return "Nothing spent yet.";

    return `${Money.toAmount(spent)} used this month. Generation stops at the limit.`;
  };

  return (
    <div class="key-block">
      <h3 class="key-name">{props.provider.name}</h3>

      <div class="key-field">
        <div class="field">
          <label class="visually-hidden" for={`key-${props.provider.id}`}>
            {props.provider.name} key
          </label>
          <Show
            when={isSealed()}
            fallback={
              <input
                class="input"
                id={`key-${props.provider.id}`}
                type="password"
                placeholder={`Paste your ${props.provider.name} key`}
                value={typedKey()}
                onInput={(event) => setTypedKey(event.currentTarget.value)}
              />
            }
          >
            <input
              class="input"
              id={`key-${props.provider.id}`}
              type="text"
              value={`…${props.savedKey?.hint ?? ""}`}
              readOnly
            />
          </Show>
        </div>

        <Show
          when={isSealed()}
          fallback={
            <button
              class="btn"
              type="button"
              disabled={typedKey().trim().length === 0}
              onClick={save}
            >
              Save key
            </button>
          }
        >
          <button class="btn" type="button" onClick={() => setReplacing(true)}>
            Replace
          </button>
          <button
            class="btn is-danger"
            type="button"
            onClick={() => props.onRemove()}
          >
            Remove
          </button>
        </Show>
      </div>

      <div class="key-limit">
        <div class="field">
          <label for={`limit-${props.provider.id}`}>Monthly limit</label>
          <div class="amount-input">
            <span class="amount-prefix" aria-hidden="true">
              $
            </span>
            <input
              class="input"
              id={`limit-${props.provider.id}`}
              type="text"
              inputmode="decimal"
              placeholder="No limit"
              value={shownLimit()}
              onInput={(event) => setLimitText(event.currentTarget.value)}
            />
          </div>
        </div>
        <span class="key-usage">{usage()}</span>
      </div>
    </div>
  );
}
