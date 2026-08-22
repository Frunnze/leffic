import type { JSX } from "solid-js";
import { Icon } from "../../shared/ui/icons/Icon";

type AuthCardHeadProps = {
  readonly title: string;
  readonly subtitle: string;
};

export function AuthCardHead(props: AuthCardHeadProps): JSX.Element {
  return (
    <>
      <span class="auth-mark">
        <Icon name="logo" size="lg" />
      </span>

      <div class="auth-head">
        <h1 class="auth-title">{props.title}</h1>
        <span class="auth-subtitle">{props.subtitle}</span>
      </div>
    </>
  );
}
