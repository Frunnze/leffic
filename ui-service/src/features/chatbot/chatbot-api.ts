import { HttpClient } from "../../shared/api/http";
import { Json } from "../../shared/api/json";
import type { ChatMessage } from "./chat-models";

const MISSING_ANSWER = "Sorry, there was no answer.";

export class ChatbotApi {
  static async ask(conversation: readonly ChatMessage[]): Promise<string> {
    const payload = await HttpClient.json({
      endpoint: "/api/files/chat",
      method: "POST",
      body: { conversation },
    });

    return Json.stringOr(Json.object(payload, "chatAnswer").answer, MISSING_ANSWER);
  }
}
