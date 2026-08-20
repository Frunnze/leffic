import {
  For,
  Show,
  createEffect,
  createSignal,
  on,
  type JSX,
} from "solid-js";
import { ChatbotApi } from "./chatbot-api";
import { useAsk } from "./AskContext";
import { Icon } from "../../shared/ui/icons/Icon";
import type { ChatMessage } from "./chat-models";
import type { PendingAsk } from "./ask-store";

type LoggedMessage = ChatMessage & {
  readonly shownAs: string;
};

export type ChatbotProps = {
  readonly onClose: () => void;
};

export function Chatbot(props: ChatbotProps): JSX.Element {
  const ask = useAsk();
  const [messages, setMessages] = createSignal<readonly LoggedMessage[]>([]);
  const [draft, setDraft] = createSignal("");
  const [isWaiting, setWaiting] = createSignal(false);
  let log: HTMLDivElement | undefined;

  const scrollToNewestMessage = (): void => {
    if (log === undefined) return;

    log.scrollTop = log.scrollHeight;
  };

  createEffect(on([messages, isWaiting], scrollToNewestMessage));

  createEffect(
    on(ask.pendingAsk, (pending: PendingAsk | null) => {
      if (pending === null) return;

      ask.questionSent();
      void send(pending.question, pending.shownAs);
    }),
  );

  const send = async (question: string, shownAs?: string): Promise<void> => {
    const trimmed = question.trim();
    if (trimmed.length === 0 || isWaiting()) return;

    const conversation: readonly LoggedMessage[] = [
      ...messages(),
      { role: "user", content: trimmed, shownAs: shownAs ?? trimmed },
    ];
    setMessages(conversation);
    setDraft("");
    setWaiting(true);

    const asked: readonly ChatMessage[] = conversation.map((message) => ({
      role: message.role,
      content: message.content,
    }));
    const answer = await ChatbotApi.ask(asked).catch(
      () => "Something went wrong. Try again.",
    );

    setMessages([
      ...conversation,
      { role: "assistant", content: answer, shownAs: answer },
    ]);
    setWaiting(false);
  };

  return (
    <aside class="chatbot" aria-label="Ask">
      <div class="chatbot-head">
        <span class="chatbot-title">
          <Icon name="chatHeader" size="sm" />
          Ask
        </span>
        <button
          class="btn btn-quiet btn-icon"
          type="button"
          aria-label="Close Ask"
          onClick={() => props.onClose()}
        >
          <Icon name="closePlain" size="sm" />
        </button>
      </div>

      <div class="chatbot-log" aria-live="polite" ref={log}>
        <Show when={messages().length === 0 && !isWaiting()}>
          <div class="chat-empty">
            <span class="chat-empty-title">No messages yet</span>
          </div>
        </Show>

        <For each={messages()}>
          {(message) => (
            <div
              class="chat-bubble"
              classList={{
                "chat-bubble-assistant": message.role === "assistant",
                "chat-bubble-user": message.role === "user",
              }}
            >
              {message.shownAs}
            </div>
          )}
        </For>
        <Show when={isWaiting()}>
          <div class="chat-bubble chat-bubble-assistant">Thinking…</div>
        </Show>
      </div>

      <form
        class="chatbot-compose"
        onSubmit={(event) => {
          event.preventDefault();
          void send(draft());
        }}
      >
        <textarea
          class="chatbot-input"
          rows="3"
          aria-label="Message"
          placeholder="Ask a question"
          value={draft()}
          onInput={(event) => setDraft(event.currentTarget.value)}
          onKeyDown={(event) => {
            if (event.key !== "Enter" || event.shiftKey) return;

            event.preventDefault();
            void send(draft());
          }}
        />
        <button
          class="btn btn-primary btn-icon chatbot-send"
          type="submit"
          aria-label="Send"
          disabled={isWaiting()}
        >
          <Icon name="send" size="sm" />
        </button>
      </form>
    </aside>
  );
}
