import { For, Show, createSignal, type JSX } from "solid-js";
import { ChatbotApi } from "./chatbot-api";
import { Icon } from "../../shared/ui/icons/Icon";
import type { ChatMessage } from "./chat-models";

const OPENING_MESSAGE: ChatMessage = {
  role: "assistant",
  content: "Ask me anything about the material in this folder.",
};

const SUGGESTIONS: readonly string[] = [
  "Summarise this folder",
  "Quiz me on this",
];

export type ChatbotProps = {
  readonly onClose: () => void;
};

export function Chatbot(props: ChatbotProps): JSX.Element {
  const [messages, setMessages] = createSignal<readonly ChatMessage[]>([
    OPENING_MESSAGE,
  ]);
  const [draft, setDraft] = createSignal("");
  const [isWaiting, setWaiting] = createSignal(false);

  const send = async (question: string): Promise<void> => {
    const trimmed = question.trim();
    if (trimmed.length === 0 || isWaiting()) return;

    const conversation: readonly ChatMessage[] = [
      ...messages(),
      { role: "user", content: trimmed },
    ];
    setMessages(conversation);
    setDraft("");
    setWaiting(true);

    const answer = await ChatbotApi.ask(conversation).catch(
      () => "Something went wrong. Try again.",
    );

    setMessages([...conversation, { role: "assistant", content: answer }]);
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

      <div class="chatbot-log" aria-live="polite">
        <For each={messages()}>
          {(message) => (
            <div
              class="chat-bubble"
              classList={{
                "chat-bubble-assistant": message.role === "assistant",
                "chat-bubble-user": message.role === "user",
              }}
            >
              {message.content}
            </div>
          )}
        </For>
        <Show when={isWaiting()}>
          <div class="chat-bubble chat-bubble-assistant">Thinking…</div>
        </Show>
      </div>

      <div class="chat-suggestions">
        <For each={SUGGESTIONS}>
          {(suggestion) => (
            <button
              class="chat-suggestion"
              type="button"
              onClick={() => void send(suggestion)}
            >
              {suggestion}
            </button>
          )}
        </For>
      </div>

      <form
        class="chatbot-compose"
        onSubmit={(event) => {
          event.preventDefault();
          void send(draft());
        }}
      >
        <input
          class="input"
          type="text"
          aria-label="Message"
          placeholder="Ask a question"
          value={draft()}
          onInput={(event) => setDraft(event.currentTarget.value)}
        />
        <button class="btn btn-primary" type="submit" disabled={isWaiting()}>
          Send
        </button>
      </form>
    </aside>
  );
}
