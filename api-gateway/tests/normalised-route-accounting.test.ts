import { describe, expect, it } from "vitest";
import {
  AUTHENTICATION_ZONE_WORD,
  GENERATION_COST_LIMITED_ROUTES,
  GENERATION_COST_ZONE_WORD,
  GENERATION_WATCHER_POLL,
  evaluatedKey,
} from "./rate-limit-support";

const ACCOUNT_PATHS = [
  "/api/user/account",
  "/api/user/account/provider-keys",
];

const PATHS_MERELY_STARTING_WITH_AN_EXCLUDED_NAME = [
  "/api/user/logout-all",
  "/api/user/accounts",
];

describe("what the sign-in budget pays for", () => {
  it("counts a sign-in attempt against the sign-in budget", () => {
    expect(
      evaluatedKey(AUTHENTICATION_ZONE_WORD, "/api/user/login"),
    ).not.toBe("");
  });

  it("counts a new-account attempt against the sign-in budget", () => {
    expect(
      evaluatedKey(AUTHENTICATION_ZONE_WORD, "/api/user/sign-up"),
    ).not.toBe("");
  });

  it("spares the silent token refresh the sign-in budget", () => {
    expect(
      evaluatedKey(AUTHENTICATION_ZONE_WORD, "/api/user/refresh-token"),
    ).toBe("");
  });

  it("spares logging out the sign-in budget", () => {
    expect(evaluatedKey(AUTHENTICATION_ZONE_WORD, "/api/user/logout")).toBe(
      "",
    );
  });

  it("spares every account path the sign-in budget", () => {
    for (const path of ACCOUNT_PATHS) {
      expect(evaluatedKey(AUTHENTICATION_ZONE_WORD, path)).toBe("");
    }
  });

  it("counts a path that merely starts with an excluded name", () => {
    for (const path of PATHS_MERELY_STARTING_WITH_AN_EXCLUDED_NAME) {
      expect(evaluatedKey(AUTHENTICATION_ZONE_WORD, path)).not.toBe("");
    }
  });
});

describe("what the paid-generation budget pays for", () => {
  it("counts each of the four paid routes against the cost budget", () => {
    for (const route of GENERATION_COST_LIMITED_ROUTES) {
      expect(evaluatedKey(GENERATION_COST_ZONE_WORD, route)).not.toBe("");
    }
  });

  it("spares a paid route written with a trailing slash", () => {
    expect(
      evaluatedKey(GENERATION_COST_ZONE_WORD, "/api/content/chat/"),
    ).toBe("");
  });

  it("spares a paid route written in mixed case", () => {
    expect(
      evaluatedKey(GENERATION_COST_ZONE_WORD, "/api/content/Chat"),
    ).toBe("");
  });
});

describe("what a query string and a poll cost", () => {
  it("counts a throttled route that carries a query string", () => {
    expect(
      evaluatedKey(AUTHENTICATION_ZONE_WORD, "/api/user/login?next=/library"),
    ).not.toBe("");
    expect(
      evaluatedKey(GENERATION_COST_ZONE_WORD, "/api/content/chat?stream=1"),
    ).not.toBe("");
  });

  it("charges the generation-watcher poll to neither throttled budget", () => {
    expect(
      evaluatedKey(AUTHENTICATION_ZONE_WORD, GENERATION_WATCHER_POLL),
    ).toBe("");
    expect(
      evaluatedKey(GENERATION_COST_ZONE_WORD, GENERATION_WATCHER_POLL),
    ).toBe("");
  });
});
