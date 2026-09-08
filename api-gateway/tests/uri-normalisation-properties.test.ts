import { describe, expect, it } from "vitest";
import fc from "fast-check";
import {
  isClassifiablePath,
  normalisedRequestPath,
} from "./uri-normalisation-support";

const PATH_SEPARATOR = "/";
const PADDING_SEGMENT = "root";
const REPEATED_SLASH = "//";
const DOT_SEGMENT = ".";
const ASCENT_SEGMENT = "..";
const ENCODED_NULL_BYTE = "%00";

const PATH_SEGMENT_POOL = [
  "api",
  "user",
  "content",
  "login",
  "sign-up",
  "chat",
  "extract-text",
  "%63hat",
  "%6cogin",
  "%2541",
  "%3f",
  "%23",
  "",
  DOT_SEGMENT,
  ASCENT_SEGMENT,
];

const PLAIN_SEGMENT_POOL = ["api", "user", "content", "login", "chat"];
const QUERY_PARAMETER_POOL = ["a=1", "stream=1", "next=/library", "b=2"];
const MALFORMED_ESCAPE_POOL = ["%zz", "%g1", "%-2", "%z0"];
const PLAIN_ROUTE_POOL = ["/api/user/login", "/api/content/chat"];
const TRAILING_SEPARATOR_POOL = ["", PATH_SEPARATOR];
const MAXIMUM_SEGMENTS = 8;
const MAXIMUM_RISKY_SEGMENTS = 4;
const MAXIMUM_QUERY_PARAMETERS = 3;

const RISKY_SEGMENT_POOL = PATH_SEGMENT_POOL.concat([
  "%zz",
  ENCODED_NULL_BYTE,
  "chat%",
]);

function rootedPathFrom(segments: readonly string[]): string {
  const ascents = segments.filter((segment) => {
    return segment === ASCENT_SEGMENT;
  }).length;
  const padding = new Array<string>(ascents).fill(PADDING_SEGMENT);

  return PATH_SEPARATOR + padding.concat(segments).join(PATH_SEPARATOR);
}

const requestPathArbitrary = fc
  .array(fc.constantFrom(...PATH_SEGMENT_POOL), {
    maxLength: MAXIMUM_SEGMENTS,
  })
  .map(rootedPathFrom);

const normalisedPathArbitrary = fc
  .tuple(
    fc.array(fc.constantFrom(...PLAIN_SEGMENT_POOL), {
      maxLength: MAXIMUM_SEGMENTS,
    }),
    fc.constantFrom(...TRAILING_SEPARATOR_POOL),
  )
  .map(([segments, trailing]) => {
    if (segments.length === 0) return PATH_SEPARATOR;

    return PATH_SEPARATOR + segments.join(PATH_SEPARATOR) + trailing;
  });

const riskyRequestUriArbitrary = fc
  .array(fc.constantFrom(...RISKY_SEGMENT_POOL), {
    maxLength: MAXIMUM_RISKY_SEGMENTS,
  })
  .map((segments) => PATH_SEPARATOR + segments.join(PATH_SEPARATOR));

const queryStringArbitrary = fc
  .array(fc.constantFrom(...QUERY_PARAMETER_POOL), {
    maxLength: MAXIMUM_QUERY_PARAMETERS,
  })
  .map((parameters) => parameters.join("&"));

describe("guarantees the normalisation model owes every caller", () => {
  it("normalisedRequestPath property leaves a normalised path alone", () => {
    fc.assert(
      fc.property(normalisedPathArbitrary, (classificationPath) => {
        expect(normalisedRequestPath(classificationPath)).toBe(
          classificationPath,
        );
      }),
    );
  });

  it("normalisedRequestPath property leaves no repeated slash", () => {
    fc.assert(
      fc.property(requestPathArbitrary, (requestUri) => {
        expect(normalisedRequestPath(requestUri)).not.toContain(
          REPEATED_SLASH,
        );
      }),
    );
  });

  it("normalisedRequestPath property leaves no dot segment", () => {
    fc.assert(
      fc.property(requestPathArbitrary, (requestUri) => {
        const segments = normalisedRequestPath(requestUri).split(
          PATH_SEPARATOR,
        );

        expect(segments).not.toContain(DOT_SEGMENT);
        expect(segments).not.toContain(ASCENT_SEGMENT);
      }),
    );
  });

  it("normalisedRequestPath property leaves no query string", () => {
    fc.assert(
      fc.property(
        requestPathArbitrary,
        queryStringArbitrary,
        (path, query) => {
          expect(normalisedRequestPath(`${path}?${query}`)).toBe(
            normalisedRequestPath(path),
          );
        },
      ),
    );
  });

  it("normalisedRequestPath property roots every path at a slash", () => {
    fc.assert(
      fc.property(requestPathArbitrary, (requestUri) => {
        expect(
          normalisedRequestPath(requestUri).startsWith(PATH_SEPARATOR),
        ).toBe(true);
      }),
    );
  });

  it("normalisedRequestPath property refuses any encoded null byte", () => {
    fc.assert(
      fc.property(
        fc.constantFrom(...PLAIN_ROUTE_POOL),
        fc.nat(),
        (route, offset) => {
          const cut = offset % (route.length + 1);
          const smuggled = route.slice(0, cut)
            + ENCODED_NULL_BYTE
            + route.slice(cut);

          expect(() => normalisedRequestPath(smuggled)).toThrow();
        },
      ),
    );
  });

  it("normalisedRequestPath property refuses any malformed escape", () => {
    fc.assert(
      fc.property(
        fc.constantFrom(...PLAIN_ROUTE_POOL),
        fc.constantFrom(...MALFORMED_ESCAPE_POOL),
        fc.nat(),
        (route, escape, offset) => {
          const cut = offset % (route.length + 1);
          const broken = route.slice(0, cut) + escape + route.slice(cut);

          expect(() => normalisedRequestPath(broken)).toThrow();
        },
      ),
    );
  });

  it("isClassifiablePath property admits only paths it can normalise", () => {
    fc.assert(
      fc.property(riskyRequestUriArbitrary, (requestUri) => {
        fc.pre(isClassifiablePath(requestUri));

        expect(
          normalisedRequestPath(requestUri).startsWith(PATH_SEPARATOR),
        ).toBe(true);
      }),
    );
  });
});
