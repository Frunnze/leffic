import { describe, expect, it } from "vitest";
import {
  ConfigDirective,
  argumentText,
  directivesNamed,
} from "./nginx-config-support";
import {
  declaredMaps,
  rateLimitSelectorMaps,
} from "./nginx-selector-support";
import {
  AUTHENTICATION_SELECTOR_VARIABLE,
  AUTHENTICATION_ZONE_WORD,
  CLIENT_ADDRESS_KEY,
  GENERATION_COST_SELECTOR_VARIABLE,
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
const SIGN_IN_SELECTOR_PATTERN =
  "~^/api/user/(?!(refresh-token|logout|account)(/|$))";
const PAID_ROUTE_SELECTOR_PATTERN =
  "~^/api/content/(chat|extract-text|upload-files|generate-study-units)$";
const ASSIGNMENT_DIRECTIVE = "set";

const DECLARED_ASSIGNMENTS = [
  `${CLASSIFICATION_VARIABLE} ${NORMALISED_URI_VARIABLE}`,
  "$user_service user-service",
  "$account_service user-service",
  "$content_service content-management-service",
  "$documents_service content-documents",
];

const DECLARED_SELECTOR_MAPS = [
  {
    sourceVariable: CLASSIFICATION_VARIABLE,
    targetVariable: AUTHENTICATION_SELECTOR_VARIABLE,
    defaultValue: "",
    entries: [
      { pattern: SIGN_IN_SELECTOR_PATTERN, value: CLIENT_ADDRESS_KEY },
    ],
  },
  {
    sourceVariable: CLASSIFICATION_VARIABLE,
    targetVariable: GENERATION_COST_SELECTOR_VARIABLE,
    defaultValue: "",
    entries: [
      { pattern: PAID_ROUTE_SELECTOR_PATTERN, value: CLIENT_ADDRESS_KEY },
    ],
  },
];

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

  it("feeds both throttled selectors exactly as it fed them before", () => {
    expect(rateLimitSelectorMaps()).toEqual(DECLARED_SELECTOR_MAPS);
  });

  it("assigns no variable telling the njs module which guard to run", () => {
    const assignmentDirectives = directivesNamed(ASSIGNMENT_DIRECTIVE);
    const assignments = assignmentDirectives.map(argumentText);

    expect(assignments).toEqual(DECLARED_ASSIGNMENTS);
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
