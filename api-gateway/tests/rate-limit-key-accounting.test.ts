import { describe, expect, it } from "vitest";
import {
  AUTHENTICATION_ZONE_WORD,
  GENERATION_COST_ZONE_WORD,
  GENERATION_WATCHER_POLL,
  evaluatedKey,
  selectorValueFor,
} from "./rate-limit-support";

describe("a request counts only when its whole key is non-empty", () => {
  it("leaves the refresh-token route out of the auth zone", () => {
    expect(
      evaluatedKey(AUTHENTICATION_ZONE_WORD, "/api/user/refresh-token"),
    ).toBe("");
  });

  it("leaves the generation-watcher poll out of the auth zone", () => {
    expect(
      evaluatedKey(AUTHENTICATION_ZONE_WORD, GENERATION_WATCHER_POLL),
    ).toBe("");
  });

  it("leaves an ordinary read out of the generation-cost zone", () => {
    expect(
      evaluatedKey(GENERATION_COST_ZONE_WORD, "/api/content/folders"),
    ).toBe("");
  });

  it("keeps the login route inside the auth zone", () => {
    expect(evaluatedKey(AUTHENTICATION_ZONE_WORD, "/api/user/login")).not.toBe(
      "",
    );
  });

  it("keeps a paid generation request inside the cost zone", () => {
    expect(
      evaluatedKey(GENERATION_COST_ZONE_WORD, "/api/content/chat"),
    ).not.toBe("");
  });

  it("counts a login attempt nginx normalises back to the login route", () => {
    expect(
      selectorValueFor(AUTHENTICATION_ZONE_WORD, "//api/user/login"),
    ).not.toBe("");
  });

  it("counts a login attempt written with a percent-encoded letter", () => {
    expect(
      selectorValueFor(AUTHENTICATION_ZONE_WORD, "/api/user/%6cogin"),
    ).not.toBe("");
  });
});
