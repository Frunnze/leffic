import { describe, expect, it } from "vitest";
import { ConfigDirective, directivesNamed } from "./nginx-config-support";
import {
  declaredMaps,
  rateLimitSelectorMaps,
} from "./nginx-selector-support";
import {
  AUTHENTICATION_ZONE_WORD,
  GENERATION_COST_ZONE_WORD,
  SELECTOR_MAP_COUNT,
  evaluatedKey,
  selectorValueFor,
} from "./rate-limit-support";

const CLASSIFICATION_VARIABLE = "$classification_path";
const NORMALISED_URI_VARIABLE = "$uri";
const REQUEST_URI_VARIABLE = "$request_uri";
const SERVER_LEVEL = "http/server";
const SINGLE_ASSIGNMENT = 1;
const PLAIN_LOGIN_REQUEST_URI = "/api/user/login";
const EVASIVE_LOGIN_REQUEST_URI = "/api/user/%6cogin";
const EVASIVE_CHAT_REQUEST_URI = "/api/content/ch%61t";

const PREFIX_STRIPPING_REWRITES = [
  ["^/api/user/(.*)$", "/$1", "break"],
  ["^/api/user/(.*)$", "/$1", "break"],
  ["^/api/content/(.*)$", "/$1", "break"],
  ["^/api/content/(.*)$", "/$1", "break"],
];

function classificationAssignments(): readonly ConfigDirective[] {
  return directivesNamed("set").filter((directive) => {
    return directive.arguments[0] === CLASSIFICATION_VARIABLE;
  });
}

describe("the path the gateway classifies a request on", () => {
  it("is captured once, before any location is chosen", () => {
    const assignments = classificationAssignments();

    expect(assignments.length).toBe(SINGLE_ASSIGNMENT);
    expect(assignments[0]?.arguments).toEqual([
      CLASSIFICATION_VARIABLE,
      NORMALISED_URI_VARIABLE,
    ]);
    expect(assignments[0]?.level).toBe(SERVER_LEVEL);
  });

  it("still strips the route prefix in every location it did", () => {
    const rewrites = directivesNamed("rewrite").map((directive) => {
      return directive.arguments;
    });

    expect(rewrites).toEqual(PREFIX_STRIPPING_REWRITES);
  });

  it("is what both throttled selectors classify", () => {
    const selectorMaps = rateLimitSelectorMaps();

    expect(selectorMaps.length).toBe(SELECTOR_MAP_COUNT);

    for (const selectorMap of selectorMaps) {
      expect(selectorMap.sourceVariable).toBe(CLASSIFICATION_VARIABLE);
    }
  });
});

describe("what the gateway never classifies a request on", () => {
  it("classifies no selector on the raw request line the client sent", () => {
    for (const selectorMap of declaredMaps()) {
      expect(selectorMap.sourceVariable).not.toBe(REQUEST_URI_VARIABLE);
    }
  });

  it("classifies no selector on a variable a rewrite can change", () => {
    for (const selectorMap of declaredMaps()) {
      expect(selectorMap.sourceVariable).not.toBe(NORMALISED_URI_VARIABLE);
    }
  });
});

describe("asking the harness what a request costs", () => {
  it("counts a paid request spelled to dodge the selector pattern", () => {
    expect(
      evaluatedKey(GENERATION_COST_ZONE_WORD, EVASIVE_CHAT_REQUEST_URI),
    ).not.toBe("");
  });

  it("reads one selector value for every spelling of one route", () => {
    const evasive = selectorValueFor(
      AUTHENTICATION_ZONE_WORD,
      EVASIVE_LOGIN_REQUEST_URI,
    );

    expect(evasive).toBe(
      selectorValueFor(AUTHENTICATION_ZONE_WORD, PLAIN_LOGIN_REQUEST_URI),
    );
    expect(evasive).not.toBe("");
  });
});
