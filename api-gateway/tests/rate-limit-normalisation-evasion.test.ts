import { describe, expect, it } from "vitest";
import { mappedValueFor } from "./nginx-selector-support";
import {
  GENERATION_COST_ZONE_WORD,
  selectorOf,
} from "./rate-limit-support";

const EVASIVE_CHAT_REQUEST_URIS = [
  "/api/content/%63hat",
  "/api/content/./chat",
  "/api/content/%67enerate-study-units",
  "/api/content/%75pload-files",
];

describe("generation-cost selector under uri normalisation", () => {
  it("counts a chat request nginx normalises back to the chat route", () => {
    const costSelector = selectorOf(GENERATION_COST_ZONE_WORD);

    for (const requestUri of EVASIVE_CHAT_REQUEST_URIS) {
      expect(mappedValueFor(costSelector, requestUri)).not.toBe("");
    }
  });
});
