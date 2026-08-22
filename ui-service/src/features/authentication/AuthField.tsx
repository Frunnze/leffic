import { Show, type JSX } from "solid-js";
import { Icon } from "../../shared/ui/icons/Icon";

type AuthFieldProps = {
  readonly id: string;
  readonly label: string;
  readonly type: "text" | "email" | "password";
  readonly autocomplete: string;
  readonly value: string;
  readonly error: string;
  readonly onInput: (value: string) => void;
};

export function AuthField(props: AuthFieldProps): JSX.Element {
  const errorId = (): string => `${props.id}-error`;
  const hasError = (): boolean => props.error.length > 0;

  return (
    <div class="field">
      <label for={props.id}>{props.label}</label>
      <input
        class="input input-lg"
        id={props.id}
        type={props.type}
        autocomplete={props.autocomplete}
        aria-invalid={hasError()}
        aria-describedby={hasError() ? errorId() : undefined}
        value={props.value}
        onInput={(event) => {
          props.onInput(event.currentTarget.value);
        }}
      />
      <Show when={hasError()}>
        <span class="field-error" id={errorId()}>
          <Icon name="failure" size="sm" />
          {props.error}
        </span>
      </Show>
    </div>
  );
}
