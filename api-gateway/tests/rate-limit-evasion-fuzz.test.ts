import { describe, expect, it } from "vitest";
import {
  AUTHENTICATION_LIMITED_ROUTES,
  AUTHENTICATION_UNLIMITED_ROUTES,
  AUTHENTICATION_ZONE_WORD,
  GENERATION_COST_LIMITED_ROUTES,
  GENERATION_COST_ZONE_WORD,
  GENERATION_WATCHER_POLL,
  UNCOUNTED_ROUTES,
  evaluatedKey,
} from "./rate-limit-support";
import { HEXADECIMAL_BASE } from "./uri-normalisation-support";

type EvasiveRequest = {
  readonly zoneWord: string;
  readonly requestUri: string;
};

const ESCAPE_DIGITS = 2;

const SELECTOR_ZONE_WORDS = [
  AUTHENTICATION_ZONE_WORD,
  GENERATION_COST_ZONE_WORD,
];

const UNCOUNTED_SPELLING_ROUTES = UNCOUNTED_ROUTES
  .concat(AUTHENTICATION_UNLIMITED_ROUTES)
  .concat([GENERATION_WATCHER_POLL]);

const EVASIVE_SPELLINGS_OF_THROTTLED_ROUTES: readonly EvasiveRequest[] = [
  { zoneWord: AUTHENTICATION_ZONE_WORD, requestUri: "/api/user/%6cogin" },
  { zoneWord: AUTHENTICATION_ZONE_WORD, requestUri: "/api/user//login" },
  { zoneWord: AUTHENTICATION_ZONE_WORD, requestUri: "/api/user/./sign-up" },
  { zoneWord: AUTHENTICATION_ZONE_WORD, requestUri: "/api/user/%73ign-up" },
  { zoneWord: GENERATION_COST_ZONE_WORD, requestUri: "/api/content/%63hat" },
  { zoneWord: GENERATION_COST_ZONE_WORD, requestUri: "/api/content/./chat" },
  {
    zoneWord: GENERATION_COST_ZONE_WORD,
    requestUri: "/api/content//extract-text",
  },
  {
    zoneWord: GENERATION_COST_ZONE_WORD,
    requestUri: "/api/content/%65xtract-text",
  },
  {
    zoneWord: GENERATION_COST_ZONE_WORD,
    requestUri: "/api/content/%75pload-files",
  },
  {
    zoneWord: GENERATION_COST_ZONE_WORD,
    requestUri: "/api/content/./upload-files",
  },
  {
    zoneWord: GENERATION_COST_ZONE_WORD,
    requestUri: "/api/content/%67enerate-study-units",
  },
  {
    zoneWord: GENERATION_COST_ZONE_WORD,
    requestUri: "/api/content//generate-study-units",
  },
];

const EVASIVE_SPELLINGS_OF_UNCOUNTED_ROUTES: readonly EvasiveRequest[] = [
  {
    zoneWord: AUTHENTICATION_ZONE_WORD,
    requestUri: "/api/user/%72efresh-token",
  },
  {
    zoneWord: AUTHENTICATION_ZONE_WORD,
    requestUri: "/api/user//refresh-token",
  },
  { zoneWord: AUTHENTICATION_ZONE_WORD, requestUri: "/api/user/./logout" },
  { zoneWord: AUTHENTICATION_ZONE_WORD, requestUri: "/api/user/account" },
  {
    zoneWord: AUTHENTICATION_ZONE_WORD,
    requestUri: GENERATION_WATCHER_POLL,
  },
  {
    zoneWord: GENERATION_COST_ZONE_WORD,
    requestUri: GENERATION_WATCHER_POLL,
  },
];

function withCharacterEncodedAt(route: string, position: number): string {
  const character = route.charCodeAt(position);
  const escape = character
    .toString(HEXADECIMAL_BASE)
    .padStart(ESCAPE_DIGITS, "0");

  return `${route.slice(0, position)}%${escape}${route.slice(position + 1)}`;
}

function keysForEveryEncodingOf(
  routes: readonly string[],
  zoneWord: string,
): readonly string[] {
  const keys: string[] = [];

  for (const route of routes) {
    for (let position = 0; position < route.length; position += 1) {
      const requestUri = withCharacterEncodedAt(route, position);

      keys.push(evaluatedKey(zoneWord, requestUri));
    }
  }

  return keys;
}

describe("request spellings written to dodge a throttled selector", () => {
  it("counts every listed bypass spelling of a throttled route", () => {
    for (const evasive of EVASIVE_SPELLINGS_OF_THROTTLED_ROUTES) {
      expect(evaluatedKey(evasive.zoneWord, evasive.requestUri)).not.toBe("");
    }
  });

  it("spares every listed bypass spelling of an uncounted route", () => {
    for (const evasive of EVASIVE_SPELLINGS_OF_UNCOUNTED_ROUTES) {
      expect(evaluatedKey(evasive.zoneWord, evasive.requestUri)).toBe("");
    }
  });

  it("counts a sign-in route with any single character encoded", () => {
    const keys = keysForEveryEncodingOf(
      AUTHENTICATION_LIMITED_ROUTES,
      AUTHENTICATION_ZONE_WORD,
    );

    for (const key of keys) {
      expect(key).not.toBe("");
    }
  });

  it("counts a paid route with any single character encoded", () => {
    const keys = keysForEveryEncodingOf(
      GENERATION_COST_LIMITED_ROUTES,
      GENERATION_COST_ZONE_WORD,
    );

    for (const key of keys) {
      expect(key).not.toBe("");
    }
  });
});

describe("request spellings that name no throttled route at all", () => {
  it("spares an uncounted route with any single character encoded", () => {
    for (const zoneWord of SELECTOR_ZONE_WORDS) {
      const keys = keysForEveryEncodingOf(
        UNCOUNTED_SPELLING_ROUTES,
        zoneWord,
      );

      for (const key of keys) {
        expect(key).toBe("");
      }
    }
  });

  it("spares a paid route whose first letter is encoded upper case", () => {
    expect(
      evaluatedKey(GENERATION_COST_ZONE_WORD, "/api/content/%43hat"),
    ).toBe("");
  });
});
