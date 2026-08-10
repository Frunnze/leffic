import { createSignal, type JSX } from "solid-js";
import { A, useNavigate } from "@solidjs/router";
import { AuthApi } from "../../features/authentication/authentication-api";
import { Dropdown } from "./Dropdown";
import { Icon } from "./icons/Icon";

const HOME_ROUTE = "/folder/home";
const SETTINGS_ROUTE = "/settings";

export type RailProps = {
  readonly onToggleAsk: () => void;
};

export function Rail(props: RailProps): JSX.Element {
  const navigate = useNavigate();
  const [isProfileOpen, setProfileOpen] = createSignal(false);

  const logOut = async (): Promise<void> => {
    await AuthApi.logOut();
    setProfileOpen(false);
    navigate("/");
  };

  return (
    <nav class="rail" aria-label="Main">
      <div>
        <div class="rail-logo">
          <Icon name="logo" size="lg" />
        </div>
        <ul class="rail-list">
          <li>
            <A class="rail-item" href={HOME_ROUTE}>
              <Icon name="home" />
              Home
            </A>
          </li>
          <li>
            <button class="rail-item" type="button" onClick={() => props.onToggleAsk()}>
              <Icon name="ask" />
              Ask
            </button>
          </li>
        </ul>
      </div>

      <div class="rail-foot-wrap">
        <button
          class="rail-foot"
          type="button"
          aria-expanded={isProfileOpen()}
          onClick={() => setProfileOpen(!isProfileOpen())}
        >
          <Icon name="profile" />
          Profile
        </button>
        <Dropdown
          isOpen={isProfileOpen()}
          onDismiss={() => setProfileOpen(false)}
          items={[
            {
              label: "Settings",
              icon: "settings",
              onSelect: () => {
                setProfileOpen(false);
                navigate(SETTINGS_ROUTE);
              },
            },
            { label: "Log out", icon: "logout", onSelect: () => void logOut() },
          ]}
        />
      </div>
    </nav>
  );
}
