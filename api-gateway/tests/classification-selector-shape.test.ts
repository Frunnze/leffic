import { describe, expect, it } from "vitest";
import { rateLimitSelectorMaps } from "./nginx-selector-support";
import {
  AUTHENTICATION_ZONE_WORD,
  GENERATION_COST_ZONE_WORD,
  selectorOf,
} from "./rate-limit-support";

const SINGLE_PATTERN_ENTRY = 1;
const CASE_SENSITIVE_PREFIX = "~";
const CASE_INSENSITIVE_PREFIX = "~*";
const ENCODED_CHARACTER_SPELLING = "%";
const REPEATED_SLASH_SPELLING = "/+";
const DOT_SEGMENT_SPELLING = "\\.";

function firstPatternOf(zoneWord: string): string {
  return selectorOf(zoneWord).entries[0]?.pattern ?? "";
}

function selectorPatterns(): readonly string[] {
  return rateLimitSelectorMaps().flatMap((selectorMap) => {
    return selectorMap.entries.map((entry) => entry.pattern);
  });
}

describe("the sign-in selector", () => {
  it("names every throttled sign-in route in one pattern", () => {
    expect(selectorOf(AUTHENTICATION_ZONE_WORD).entries.length).toBe(
      SINGLE_PATTERN_ENTRY,
    );
  });

  it("tells an upper-case sign-in spelling from a lower-case one", () => {
    const pattern = firstPatternOf(AUTHENTICATION_ZONE_WORD);

    expect(pattern.startsWith(CASE_SENSITIVE_PREFIX)).toBe(true);
    expect(pattern.startsWith(CASE_INSENSITIVE_PREFIX)).toBe(false);
  });

  it("counts no sign-in path it has not named", () => {
    expect(selectorOf(AUTHENTICATION_ZONE_WORD).defaultValue).toBe("");
  });
});

describe("the paid-generation selector", () => {
  it("names every paid generation route in one pattern", () => {
    expect(selectorOf(GENERATION_COST_ZONE_WORD).entries.length).toBe(
      SINGLE_PATTERN_ENTRY,
    );
  });

  it("tells an upper-case paid-route spelling from a lower-case one", () => {
    const pattern = firstPatternOf(GENERATION_COST_ZONE_WORD);

    expect(pattern.startsWith(CASE_SENSITIVE_PREFIX)).toBe(true);
    expect(pattern.startsWith(CASE_INSENSITIVE_PREFIX)).toBe(false);
  });

  it("counts no content path it has not named", () => {
    expect(selectorOf(GENERATION_COST_ZONE_WORD).defaultValue).toBe("");
  });
});

describe("selector patterns chase no spelling of their own", () => {
  it("spells out no percent-encoded variant of a throttled route", () => {
    for (const pattern of selectorPatterns()) {
      expect(pattern).not.toContain(ENCODED_CHARACTER_SPELLING);
    }
  });

  it("spells out no repeated-slash variant of a throttled route", () => {
    for (const pattern of selectorPatterns()) {
      expect(pattern).not.toContain(REPEATED_SLASH_SPELLING);
    }
  });

  it("spells out no dot-segment variant of a throttled route", () => {
    for (const pattern of selectorPatterns()) {
      expect(pattern).not.toContain(DOT_SEGMENT_SPELLING);
    }
  });
});
