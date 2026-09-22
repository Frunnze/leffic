import { describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import crypto from "crypto";
import {
  MISSING_SECRETS,
  MISSING_SECRET_ERROR,
  PREFLIGHT_METHOD,
  PREFLIGHT_STATUS,
  REFUSED_TOKEN_STATUS,
  SECRET,
  SECRET_VARIABLE,
  VERIFIED_AUTHORIZATION,
  authorizationOrNoneArbitrary,
  bearerAuthorization,
  expectNoResponseBody,
  foreignTokenArbitrary,
  nonPreflightMethodArbitrary,
  protectedGuardAnswers,
  publicGuardAnswers,
  requestPartsArbitrary,
  requestUsing,
  requestWith,
  signedWith,
  statusOf,
} from "./jwt-support";

describe("hasExpired", () => {
  it("hasExpired property accepts every expiry still ahead of now", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1_800_000_000, max: 4_102_444_800 }),
        (exp) => {
          const token = signedWith({ exp });

          expect(statusOf(requestWith(`Bearer ${token}`))).toBe("ok");
        },
      ),
    );
  });

  it("hasExpired property refuses every expiry already behind now", () => {
    fc.assert(
      fc.property(fc.integer({ min: 0, max: 1_600_000_000 }), (exp) => {
        const token = signedWith({ exp });

        expect(statusOf(requestWith(`Bearer ${token}`))).toBe("invalid");
      }),
    );
  });

  it("refuses a token whose claims are not readable json", () => {
    const header = Buffer.from("{}").toString("base64url");
    const body = "not-base64-json";
    const signature = crypto
      .createHmac("sha256", SECRET)
      .update(`${header}.${body}`)
      .digest("base64url");

    expect(statusOf(requestWith(`Bearer ${header}.${body}.${signature}`))).toBe(
      "invalid",
    );
  });

  it("accepts a token whose expiry is not a number", () => {
    const token = signedWith({ exp: "soon" });

    expect(statusOf(requestWith(`Bearer ${token}`))).toBe("ok");
  });

  it("accepts a token whose expiry is written as text", () => {
    const token = signedWith({ exp: "0" });

    expect(statusOf(requestWith(`Bearer ${token}`))).toBe("ok");
  });

  it("refuses a token that expires exactly now", () => {
    const now = 1_700_000_000;
    vi.spyOn(Date, "now").mockReturnValue(now * 1000);
    const token = signedWith({ exp: now });

    expect(statusOf(requestWith(`Bearer ${token}`))).toBe("invalid");
  });
});

describe("guardPublicRoute", () => {
  it("answers a preflight with 204 and no body", () => {
    const preflight = requestUsing(PREFLIGHT_METHOD);

    expect(publicGuardAnswers(preflight)).toEqual([[PREFLIGHT_STATUS]]);
  });

  it("guardPublicRoute property passes every non-preflight request", () => {
    fc.assert(
      fc.property(
        nonPreflightMethodArbitrary,
        authorizationOrNoneArbitrary,
        (method, authorization) => {
          const request = requestUsing(method, authorization);

          expect(publicGuardAnswers(request)).toEqual([]);
        },
      ),
    );
  });

  it("lets a request through without consulting a missing secret", () => {
    vi.stubEnv(SECRET_VARIABLE, undefined);
    const request = requestWith();

    expect(publicGuardAnswers(request)).toEqual([]);
    expect(request.error).not.toHaveBeenCalled();
  });

  it("guardPublicRoute property never sends a response body", () => {
    fc.assert(
      fc.property(requestPartsArbitrary, ([method, authorization]) => {
        const request = requestUsing(method, authorization);

        expectNoResponseBody(publicGuardAnswers(request));
      }),
    );
  });
});

describe("guardProtectedRoute", () => {
  it("answers a preflight with 204 without ever checking the secret", () => {
    vi.stubEnv(SECRET_VARIABLE, undefined);
    const preflight = requestUsing(PREFLIGHT_METHOD);

    expect(protectedGuardAnswers(preflight)).toEqual([[PREFLIGHT_STATUS]]);
    expect(preflight.error).not.toHaveBeenCalled();
  });

  it("guardProtectedRoute property refuses a foreign token with 401", () => {
    fc.assert(
      fc.property(
        nonPreflightMethodArbitrary,
        foreignTokenArbitrary,
        (method, token) => {
          const request = requestUsing(method, bearerAuthorization(token));
          const answers = protectedGuardAnswers(request);

          expect(answers).toEqual([[REFUSED_TOKEN_STATUS]]);
        },
      ),
    );
  });

  it("guardProtectedRoute property passes every verified request", () => {
    fc.assert(
      fc.property(nonPreflightMethodArbitrary, (method) => {
        const request = requestUsing(method, VERIFIED_AUTHORIZATION);

        expect(protectedGuardAnswers(request)).toEqual([]);
      }),
    );
  });

  it.each(MISSING_SECRETS)(
    "refuses a verified request with 401 when the secret is %j",
    (secret) => {
      vi.stubEnv(SECRET_VARIABLE, secret);
      const request = requestWith(VERIFIED_AUTHORIZATION);

      expect(protectedGuardAnswers(request)).toEqual([[REFUSED_TOKEN_STATUS]]);
    },
  );

  it.each(MISSING_SECRETS)(
    "logs the missing secret when the secret is %j",
    (secret) => {
      vi.stubEnv(SECRET_VARIABLE, secret);
      const request = requestWith(VERIFIED_AUTHORIZATION);

      protectedGuardAnswers(request);

      expect(request.error).toHaveBeenCalledWith(MISSING_SECRET_ERROR);
    },
  );

  it("guardProtectedRoute property never sends a response body", () => {
    fc.assert(
      fc.property(requestPartsArbitrary, ([method, authorization]) => {
        const request = requestUsing(method, authorization);

        expectNoResponseBody(protectedGuardAnswers(request));
      }),
    );
  });
});
