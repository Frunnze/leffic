import { Show, type JSX } from "solid-js";
import { AccountApi } from "../../features/settings/account-api";
import { Chatbot } from "../../features/chatbot/Chatbot";
import { useAsk } from "../../features/chatbot/AskContext";
import { Rail } from "./Rail";
import { Theme } from "./theme";

export type AppShellProps = {
  readonly fillsViewport?: boolean;
  readonly children: JSX.Element;
};

export function AppShell(props: AppShellProps): JSX.Element {
  const ask = useAsk();

  Theme.followAccount(async () => (await AccountApi.read()).theme);

  return (
    <div
      class="screen"
      classList={{
        "screen-fixed": props.fillsViewport === true,
        "screen-with-chat": ask.isOpen(),
      }}
    >
      <Rail onToggleAsk={ask.toggle} />
      <Show when={ask.isOpen()}>
        <Chatbot onClose={ask.close} />
      </Show>
      {props.children}
    </div>
  );
}
