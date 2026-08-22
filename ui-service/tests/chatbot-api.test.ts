import { afterEach, describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import { ChatbotApi } from "../src/shared/chatbot/chatbot-api";
import { Session } from "../src/shared/api/session";
import {
  jsonResponse,
  requestedInit,
  requestedUrl,
  stubFetch,
} from "./support";

afterEach(() => {
  vi.unstubAllGlobals();
  Session.store(null);
});

describe("ChatbotApi.ask", () => {
  it("ask property hands back the answer the service gave", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string(), async (answer) => {
        Session.store("token");
        stubFetch(jsonResponse({ answer }));

        await expect(ChatbotApi.ask([])).resolves.toBe(answer);
      }),
    );
  });

  it("ask property posts the whole conversation to the chat endpoint", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(
          fc.record({
            role: fc.constantFrom("user", "assistant"),
            content: fc.string(),
          }),
        ),
        async (conversation) => {
          Session.store("token");
          const fetching = stubFetch(jsonResponse({ answer: "ok" }));

          await ChatbotApi.ask(conversation);

          expect(requestedUrl(fetching)).toContain("/api/content/chat");
          expect(requestedInit(fetching).body).toBe(
            JSON.stringify({ conversation }),
          );
        },
      ),
    );
  });

  it("says so when the service answered with nothing usable", async () => {
    Session.store("token");
    stubFetch(jsonResponse({}));

    await expect(ChatbotApi.ask([])).resolves.toBe(
      "Sorry, there was no answer.",
    );
  });
});
