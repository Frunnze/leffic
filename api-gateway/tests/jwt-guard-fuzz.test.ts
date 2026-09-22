import { describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import {
  EMPTY_SECRET,
  PREFLIGHT_METHOD,
  PREFLIGHT_STATUS,
  REFUSED_TOKEN_STATUS,
  SECRET_VARIABLE,
  VERIFIED_AUTHORIZATION,
  bearerAuthorization,
  expectNoResponseBody,
  protectedGuardAnswers,
  publicGuardAnswers,
  requestUsing,
} from "./jwt-support";

const OVERSIZED_LENGTH = 65_536;
const TOKEN_SEGMENT_COUNT = 3;
const TOKEN_SEGMENT_PATTERN = /^[A-Za-z0-9_-]{0,48}$/;
const TOKEN_SEGMENT_SEPARATOR = ".";
const OVERSIZED_TOKEN = "A".repeat(OVERSIZED_LENGTH);

const NEAR_MISS_PREFLIGHT_METHODS = [
  "options",
  "Options",
  " OPTIONS",
  "OPTIONS ",
  "OPTIONS\u0000",
  "OPTIONS\r\n",
  "OPTION",
  "OPTIONSS",
  "\u041EPTIONS",
  "\uFF2F\uFF30\uFF34\uFF29\uFF2F\uFF2E\uFF33",
  "",
];

const MALFORMED_AUTHORIZATIONS = [
  "",
  "Bearer",
  "Bearer ",
  "Bearer ..",
  "Bearer a.b.c",
  "Bearer \u0000.\u0000.\u0000",
  bearerAuthorization(OVERSIZED_TOKEN),
  `${VERIFIED_AUTHORIZATION}${OVERSIZED_TOKEN}`,
];

const tokenSegmentArbitrary = fc.stringMatching(TOKEN_SEGMENT_PATTERN);
const binaryTextArbitrary = fc.string({ unit: "binary" });

const forgedAuthorizationArbitrary = fc
  .array(tokenSegmentArbitrary, {
    minLength: TOKEN_SEGMENT_COUNT,
    maxLength: TOKEN_SEGMENT_COUNT,
  })
  .map((segments) => segments.join(TOKEN_SEGMENT_SEPARATOR))
  .map(bearerAuthorization);

const hostileAuthorizationArbitrary = fc.oneof(
  binaryTextArbitrary,
  binaryTextArbitrary.map(bearerAuthorization),
  fc.constantFrom(...MALFORMED_AUTHORIZATIONS),
  forgedAuthorizationArbitrary,
);

const nearMissMethodArbitrary = fc.constantFrom(
  ...NEAR_MISS_PREFLIGHT_METHODS,
);

const hostileMethodArbitrary = fc
  .oneof(nearMissMethodArbitrary, binaryTextArbitrary)
  .filter((method) => method !== PREFLIGHT_METHOD);

const hostileRequestArbitrary = fc.tuple(
  fc.oneof(fc.constant(PREFLIGHT_METHOD), hostileMethodArbitrary),
  hostileAuthorizationArbitrary,
);

describe("guardPublicRoute", () => {
  it("guardPublicRoute property passes any hostile method", () => {
    fc.assert(
      fc.property(
        hostileMethodArbitrary,
        hostileAuthorizationArbitrary,
        (method, authorization) => {
          const request = requestUsing(method, authorization);

          expect(publicGuardAnswers(request)).toEqual([]);
        },
      ),
    );
  });

  it("guardPublicRoute property passes every near miss of OPTIONS", () => {
    fc.assert(
      fc.property(nearMissMethodArbitrary, (method) => {
        const request = requestUsing(method);

        expect(publicGuardAnswers(request)).toEqual([]);
      }),
    );
  });

  it("guardPublicRoute property answers 204 whatever the header", () => {
    fc.assert(
      fc.property(hostileAuthorizationArbitrary, (authorization) => {
        const preflight = requestUsing(PREFLIGHT_METHOD, authorization);

        expect(publicGuardAnswers(preflight)).toEqual([[PREFLIGHT_STATUS]]);
      }),
    );
  });

  it("guardPublicRoute property logs nothing and sends no body", () => {
    fc.assert(
      fc.property(hostileRequestArbitrary, ([method, authorization]) => {
        vi.stubEnv(SECRET_VARIABLE, undefined);
        const request = requestUsing(method, authorization);

        expectNoResponseBody(publicGuardAnswers(request));
        expect(request.error).not.toHaveBeenCalled();
      }),
    );
  });
});

describe("guardProtectedRoute", () => {
  it("guardProtectedRoute property refuses any hostile header", () => {
    fc.assert(
      fc.property(
        hostileMethodArbitrary,
        hostileAuthorizationArbitrary,
        (method, authorization) => {
          const request = requestUsing(method, authorization);
          const answers = protectedGuardAnswers(request);

          expect(answers).toEqual([[REFUSED_TOKEN_STATUS]]);
        },
      ),
    );
  });

  it("guardProtectedRoute property refuses a tokenless near miss", () => {
    fc.assert(
      fc.property(nearMissMethodArbitrary, (method) => {
        const request = requestUsing(method);
        const answers = protectedGuardAnswers(request);

        expect(answers).toEqual([[REFUSED_TOKEN_STATUS]]);
      }),
    );
  });

  it("guardProtectedRoute property passes a verified near miss", () => {
    fc.assert(
      fc.property(nearMissMethodArbitrary, (method) => {
        const request = requestUsing(method, VERIFIED_AUTHORIZATION);

        expect(protectedGuardAnswers(request)).toEqual([]);
      }),
    );
  });

  it("guardProtectedRoute property answers 204 whatever the header", () => {
    fc.assert(
      fc.property(hostileAuthorizationArbitrary, (authorization) => {
        vi.stubEnv(SECRET_VARIABLE, undefined);
        const preflight = requestUsing(PREFLIGHT_METHOD, authorization);
        const answers = protectedGuardAnswers(preflight);

        expect(answers).toEqual([[PREFLIGHT_STATUS]]);
        expect(preflight.error).not.toHaveBeenCalled();
      }),
    );
  });

  it("guardProtectedRoute property refuses any method with no secret", () => {
    fc.assert(
      fc.property(hostileMethodArbitrary, (method) => {
        vi.stubEnv(SECRET_VARIABLE, EMPTY_SECRET);
        const request = requestUsing(method, VERIFIED_AUTHORIZATION);
        const answers = protectedGuardAnswers(request);

        expect(answers).toEqual([[REFUSED_TOKEN_STATUS]]);
      }),
    );
  });

  it("guardProtectedRoute property sends no body when hostile", () => {
    fc.assert(
      fc.property(hostileRequestArbitrary, ([method, authorization]) => {
        const request = requestUsing(method, authorization);

        expectNoResponseBody(protectedGuardAnswers(request));
      }),
    );
  });
});
