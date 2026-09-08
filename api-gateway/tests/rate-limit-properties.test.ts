import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { mappedValueFor } from "./nginx-selector-support";
import {
  AUTHENTICATION_LIMITED_ROUTES,
  AUTHENTICATION_ZONE_WORD,
  CLIENT_ADDRESS_BYTES,
  GENERAL_ZONE_WORD,
  GENERATION_COST_LIMITED_ROUTES,
  GENERATION_COST_ZONE_WORD,
  UNCOUNTED_ROUTES,
  evaluatedKey,
  requiredApplication,
  requiredZone,
  selectorOf,
  selectorValueFor,
} from "./rate-limit-support";
import {
  isClassifiablePath,
  normalisedRequestPath,
} from "./uri-normalisation-support";

const ZONE_WORDS = [
  AUTHENTICATION_ZONE_WORD,
  GENERATION_COST_ZONE_WORD,
  GENERAL_ZONE_WORD,
];

const SELECTOR_ZONE_WORDS = [
  AUTHENTICATION_ZONE_WORD,
  GENERATION_COST_ZONE_WORD,
];

const EVERY_KNOWN_ROUTE = AUTHENTICATION_LIMITED_ROUTES
  .concat(GENERATION_COST_LIMITED_ROUTES)
  .concat(UNCOUNTED_ROUTES);

const PATH_SEPARATOR = "/";
const SEPARATOR_POOL = ["/", "//", "///", "/./", "//./"];
const CONTENT_WORD_LETTERS = ["a", "c", "h", "t", "-", "s"];
const MAXIMUM_WORD_LENGTH = 12;

const LIMITED_ROUTE_MARKERS = [
  "/api/user/",
  "chat",
  "generate-study-units",
  "extract-text",
  "upload-files",
];

function namesLimitedRoute(classificationPath: string): boolean {
  return LIMITED_ROUTE_MARKERS.some((marker) => {
    return classificationPath.indexOf(marker) !== -1;
  });
}

function spelledWithSeparator(route: string, separator: string): string {
  return route.split(PATH_SEPARATOR).join(separator);
}

const zoneWordArbitrary = fc.constantFrom(...SELECTOR_ZONE_WORDS);
const routeArbitrary = fc.constantFrom(...EVERY_KNOWN_ROUTE);
const separatorArbitrary = fc.constantFrom(...SEPARATOR_POOL);

const contentWordArbitrary = fc
  .array(fc.constantFrom(...CONTENT_WORD_LETTERS), {
    maxLength: MAXIMUM_WORD_LENGTH,
  })
  .map((letters) => letters.join(""));

describe("rate-limit selector properties", () => {
  it("mappedValueFor property invents no value the map never declared", () => {
    fc.assert(
      fc.property(zoneWordArbitrary, fc.string(), (zoneWord, probedPath) => {
        const selectorMap = selectorOf(zoneWord);
        const declared = selectorMap.entries.map((entry) => entry.value);

        expect(declared.concat([""])).toContain(
          mappedValueFor(selectorMap, probedPath),
        );
      }),
    );
  });

  it("selectorValueFor property reads one value for every spelling", () => {
    fc.assert(
      fc.property(
        zoneWordArbitrary,
        routeArbitrary,
        separatorArbitrary,
        (zoneWord, route, separator) => {
          const requestUri = spelledWithSeparator(route, separator);

          expect(selectorValueFor(zoneWord, requestUri)).toBe(
            selectorValueFor(zoneWord, route),
          );
        },
      ),
    );
  });

  it("evaluatedKey property spares a route no selector map names", () => {
    fc.assert(
      fc.property(fc.string(), (tail) => {
        const requestUri = `/${tail}`;

        fc.pre(isClassifiablePath(requestUri));
        fc.pre(!namesLimitedRoute(normalisedRequestPath(requestUri)));

        expect(evaluatedKey(AUTHENTICATION_ZONE_WORD, requestUri)).toBe("");
        expect(evaluatedKey(GENERATION_COST_ZONE_WORD, requestUri)).toBe("");
      }),
    );
  });

  it("evaluatedKey property spares a content path that is not paid", () => {
    fc.assert(
      fc.property(contentWordArbitrary, (word) => {
        const requestUri = `/api/content/${word}`;

        fc.pre(GENERATION_COST_LIMITED_ROUTES.indexOf(requestUri) === -1);

        expect(evaluatedKey(GENERATION_COST_ZONE_WORD, requestUri)).toBe("");
      }),
    );
  });
});

describe("rate-limit zone properties", () => {
  it("requiredZone property gives every zone a rate a client can reach", () => {
    fc.assert(
      fc.property(fc.constantFrom(...ZONE_WORDS), (zoneWord) => {
        expect(requiredZone(zoneWord).ratePerSecond).toBeGreaterThan(0);
      }),
    );
  });

  it("evaluatedKey property charges a counted request to one client", () => {
    fc.assert(
      fc.property(fc.webQueryParameters(), (query) => {
        const requestUri = `/api/user/login?${query}`;

        expect(evaluatedKey(AUTHENTICATION_ZONE_WORD, requestUri)).toBe(
          CLIENT_ADDRESS_BYTES,
        );
      }),
    );
  });

  it("requiredApplication property absorbs a short burst undelayed", () => {
    fc.assert(
      fc.property(fc.constantFrom(...ZONE_WORDS), (zoneWord) => {
        const application = requiredApplication(zoneWord);

        expect(application.burst).not.toBeNull();
        expect(application.burst ?? 0).toBeGreaterThan(0);
        expect(application.hasNoDelay).toBe(true);
      }),
    );
  });

  it("requiredZone property widens a cheaper route's budget", () => {
    const widening = [
      [AUTHENTICATION_ZONE_WORD, GENERATION_COST_ZONE_WORD],
      [GENERATION_COST_ZONE_WORD, GENERAL_ZONE_WORD],
    ] as const;

    fc.assert(
      fc.property(fc.constantFrom(...widening), ([narrower, wider]) => {
        expect(requiredZone(wider).ratePerSecond).toBeGreaterThan(
          requiredZone(narrower).ratePerSecond,
        );
        expect(requiredApplication(wider).burst ?? 0).toBeGreaterThan(
          requiredApplication(narrower).burst ?? 0,
        );
      }),
    );
  });
});
