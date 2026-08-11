import { Show, createSignal, type JSX } from "solid-js";
import { AccountApi } from "../../features/settings/account-api";
import { Chatbot } from "../../features/chatbot/Chatbot";
import { Rail } from "./Rail";
import { Theme } from "./theme";

export type AppShellProps = {
  readonly fillsViewport?: boolean;
  readonly children: JSX.Element;
};

export function AppShell(props: AppShellProps): JSX.Element {
  const [isAskOpen, setAskOpen] = createSignal(false);

  Theme.followAccount(async () => (await AccountApi.read()).theme);

  return (
    <div
      class="screen"
      classList={{
        "screen-fixed": props.fillsViewport === true,
        "screen-with-chat": isAskOpen(),
      }}
    >
      <Rail onToggleAsk={() => setAskOpen(!isAskOpen())} />
      <Show when={isAskOpen()}>
        <Chatbot onClose={() => setAskOpen(false)} />
      </Show>
      {props.children}
    </div>
  );
}
