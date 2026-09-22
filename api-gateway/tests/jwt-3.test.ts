import { describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import {
  DELETE_METHOD,
  FAR_FUTURE,
  LONG_PAST,
  MISSING_SECRET_ERROR,
  POST_METHOD,
  PREFLIGHT_METHOD,
  PREFLIGHT_STATUS,
  PUT_METHOD,
  REFUSED_TOKEN_STATUS,
  SECRET_VARIABLE,
  VERIFIED_AUTHORIZATION,
  authorizationOrNoneArbitrary,
  bearerAuthorization,
  missingSecretArbitrary,
  nonPreflightMethodArbitrary,
  protectedGuardAnswers,
  publicGuardAnswers,
  requestPartsArbitrary,
  requestUsing,
  requestWith,
  signedWith,
} from "./jwt-support";

const ANOTHER_SECRET = "another-secret";

const pastExpiryArbitrary = fc.integer({ min: 0, max: LONG_PAST });

describe("guardPublicRoute", () => {
  it("guardPublicRoute property answers any preflight with 204", () => {
    fc.assert(
      fc.property(authorizationOrNoneArbitrary, (authorization) => {
        const preflight = requestUsing(PREFLIGHT_METHOD, authorization);

        expect(publicGuardAnswers(preflight)).toEqual([[PREFLIGHT_STATUS]]);
      }),
    );
  });

  it("guardPublicRoute property never consults the token secret", () => {
    fc.assert(
      fc.property(requestPartsArbitrary, ([method, authorization]) => {
        vi.stubEnv(SECRET_VARIABLE, undefined);
        const request = requestUsing(method, authorization);
        const answers = publicGuardAnswers(request);

        expect(answers).not.toContainEqual([REFUSED_TOKEN_STATUS]);
        expect(request.error).not.toHaveBeenCalled();
      }),
    );
  });
});

describe("guardProtectedRoute", () => {
  it("guardProtectedRoute property answers any preflight with 204", () => {
    fc.assert(
      fc.property(authorizationOrNoneArbitrary, (authorization) => {
        const preflight = requestUsing(PREFLIGHT_METHOD, authorization);

        expect(protectedGuardAnswers(preflight)).toEqual([[PREFLIGHT_STATUS]]);
      }),
    );
  });

  it("guardProtectedRoute property skips the secret on a preflight", () => {
    fc.assert(
      fc.property(
        missingSecretArbitrary,
        authorizationOrNoneArbitrary,
        (secret, authorization) => {
          vi.stubEnv(SECRET_VARIABLE, secret);
          const preflight = requestUsing(PREFLIGHT_METHOD, authorization);
          const answers = protectedGuardAnswers(preflight);

          expect(answers).toEqual([[PREFLIGHT_STATUS]]);
          expect(preflight.error).not.toHaveBeenCalled();
        },
      ),
    );
  });

  it("guardProtectedRoute property refuses all without a secret", () => {
    fc.assert(
      fc.property(
        missingSecretArbitrary,
        nonPreflightMethodArbitrary,
        (secret, method) => {
          vi.stubEnv(SECRET_VARIABLE, secret);
          const request = requestUsing(method, VERIFIED_AUTHORIZATION);
          const answers = protectedGuardAnswers(request);

          expect(answers).toEqual([[REFUSED_TOKEN_STATUS]]);
          expect(request.error).toHaveBeenCalledWith(MISSING_SECRET_ERROR);
        },
      ),
    );
  });

  it("guardProtectedRoute property refuses every expired token", () => {
    fc.assert(
      fc.property(
        nonPreflightMethodArbitrary,
        pastExpiryArbitrary,
        (method, expirySeconds) => {
          const token = signedWith({ exp: expirySeconds });
          const request = requestUsing(method, bearerAuthorization(token));
          const answers = protectedGuardAnswers(request);

          expect(answers).toEqual([[REFUSED_TOKEN_STATUS]]);
        },
      ),
    );
  });

  it("guardProtectedRoute property refuses every tokenless request", () => {
    fc.assert(
      fc.property(nonPreflightMethodArbitrary, (method) => {
        const request = requestUsing(method);
        const answers = protectedGuardAnswers(request);

        expect(answers).toEqual([[REFUSED_TOKEN_STATUS]]);
      }),
    );
  });

  it("refuses a tokenless request with 401 and no body", () => {
    const answers = protectedGuardAnswers(requestWith());

    expect(answers).toEqual([[REFUSED_TOKEN_STATUS]]);
  });

  it("lets a verified post through to the proxy", () => {
    const post = requestUsing(POST_METHOD, VERIFIED_AUTHORIZATION);

    expect(protectedGuardAnswers(post)).toEqual([]);
  });

  it("refuses a delete whose token has expired", () => {
    const token = signedWith({ exp: LONG_PAST });
    const deletion = requestUsing(DELETE_METHOD, bearerAuthorization(token));

    expect(protectedGuardAnswers(deletion)).toEqual([[REFUSED_TOKEN_STATUS]]);
  });

  it("refuses a put whose token was signed with another secret", () => {
    const token = signedWith({ exp: FAR_FUTURE }, ANOTHER_SECRET);
    const put = requestUsing(PUT_METHOD, bearerAuthorization(token));

    expect(protectedGuardAnswers(put)).toEqual([[REFUSED_TOKEN_STATUS]]);
  });

  it("answers a preflight bearing a verified token with 204 alone", () => {
    const preflight = requestUsing(PREFLIGHT_METHOD, VERIFIED_AUTHORIZATION);

    expect(protectedGuardAnswers(preflight)).toEqual([[PREFLIGHT_STATUS]]);
  });
});
