import { Show, createSignal, type JSX } from "solid-js";
import { Chatbot } from "../../features/chatbot/Chatbot";
import { Rail } from "./Rail";

export type AppShellProps = {
  readonly fillsViewport?: boolean;
  readonly children: JSX.Element;
};

export function AppShell(props: AppShellProps): JSX.Element {
  const [isAskOpen, setAskOpen] = createSignal(false);

  return (
    <div
      class="screen"
      classList={{ "screen-fixed": props.fillsViewport === true }}
    >
      <Rail onToggleAsk={() => setAskOpen(!isAskOpen())} />
      <Show when={isAskOpen()}>
        <Chatbot onClose={() => setAskOpen(false)} />
      </Show>
      {props.children}
    </div>
  );
}
