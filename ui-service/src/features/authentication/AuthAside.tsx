import { For, type JSX } from "solid-js";
import { Icon } from "../../shared/ui/icons/Icon";

type AuthAsideProps = {
  readonly heading: string;
  readonly points: readonly string[];
};

export function AuthAside(props: AuthAsideProps): JSX.Element {
  return (
    <aside class="auth-aside">
      <span class="auth-brand">
        <Icon name="logo" />
        Leffic
      </span>

      <div class="auth-pitch">
        <h2>{props.heading}</h2>
        <ul class="auth-points">
          <For each={props.points}>
            {(point) => (
              <li>
                <Icon name="check" />
                {point}
              </li>
            )}
          </For>
        </ul>
      </div>

      <span class="auth-aside-note">Learn efficiently.</span>
    </aside>
  );
}
