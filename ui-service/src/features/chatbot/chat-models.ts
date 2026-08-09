export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  readonly role: ChatRole;
  readonly content: string;
};
