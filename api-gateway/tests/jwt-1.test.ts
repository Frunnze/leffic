import { describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import crypto from "crypto";
import {
  FAR_FUTURE,
  LONG_PAST,
  SECRET,
  requestWith,
  signedWith,
  statusOf,
} from "./jwt-support";

describe("status", () => {
  it("status property accepts every token signed with the shared secret", () => {
    fc.assert(
      fc.property(fc.dictionary(fc.string(), fc.integer()), (claims) => {
        const token = signedWith({ ...claims, exp: FAR_FUTURE });

        expect(statusOf(requestWith(`Bearer ${token}`))).toBe("ok");
      }),
    );
  });

  it("status property refuses every token signed with another secret", () => {
    fc.assert(
      fc.property(fc.string({ minLength: 1 }), (otherSecret) => {
        fc.pre(otherSecret !== SECRET);
        const token = signedWith({ exp: FAR_FUTURE }, otherSecret);

        expect(statusOf(requestWith(`Bearer ${token}`))).toBe("invalid");
      }),
    );
  });

  it("refuses every request when no secret is configured", () => {
    vi.stubEnv("JWT_SECRET_KEY", "");
    const request = requestWith(`Bearer ${signedWith({ exp: FAR_FUTURE })}`);

    expect(statusOf(request)).toBe("invalid");
    expect(request.error).toHaveBeenCalledWith("JWT_SECRET_KEY is not set");
  });

  it("refuses every request when the secret variable is unset", () => {
    vi.stubEnv("JWT_SECRET_KEY", undefined);

    expect(statusOf(requestWith("Bearer x.y.z"))).toBe("invalid");
  });

  it("refuses a request with no authorization header", () => {
    expect(statusOf(requestWith())).toBe("invalid");
  });

  it("refuses an expired token", () => {
    const token = signedWith({ exp: LONG_PAST });

    expect(statusOf(requestWith(`Bearer ${token}`))).toBe("invalid");
  });

  it("accepts a token that carries no expiry", () => {
    const token = signedWith({ sub: "learner" });

    expect(statusOf(requestWith(`Bearer ${token}`))).toBe("ok");
  });
});

describe("bearerToken", () => {
  it("bearerToken property refuses any scheme that is not bearer", () => {
    fc.assert(
      fc.property(fc.stringMatching(/^[A-Za-z]{1,10}$/), (scheme) => {
        fc.pre(scheme.toLowerCase() !== "bearer");
        const token = signedWith({ exp: FAR_FUTURE });

        expect(statusOf(requestWith(`${scheme} ${token}`))).toBe("invalid");
      }),
    );
  });

  it("bearerToken property reads the scheme without minding its case", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("Bearer", "bearer", "BEARER", "BeArEr"),
        (scheme) => {
          const token = signedWith({ exp: FAR_FUTURE });

          expect(statusOf(requestWith(`${scheme} ${token}`))).toBe("ok");
        },
      ),
    );
  });

  it("refuses a header that names no scheme", () => {
    expect(statusOf(requestWith("Bearer"))).toBe("invalid");
  });

  it("refuses a scheme that only looks the right length", () => {
    const token = signedWith({ exp: FAR_FUTURE });

    expect(statusOf(requestWith(`Bearex ${token}`))).toBe("invalid");
  });
});

describe("signedToken", () => {
  it("signedToken property refuses any token that is not three parts", () => {
    fc.assert(
      fc.property(fc.integer({ min: 0, max: 6 }), (parts) => {
        fc.pre(parts !== 3);
        const token = Array.from({ length: parts }, () => "x").join(".");

        expect(statusOf(requestWith(`Bearer ${token}`))).toBe("invalid");
      }),
    );
  });

  it("refuses a token with no header segment", () => {
    const header = "";
    const body = Buffer.from(JSON.stringify({ exp: FAR_FUTURE })).toString(
      "base64url",
    );
    const signature = crypto
      .createHmac("sha256", SECRET)
      .update(`${header}.${body}`)
      .digest("base64url");

    expect(statusOf(requestWith(`Bearer ${header}.${body}.${signature}`))).toBe(
      "invalid",
    );
  });
});

describe("signatureMatches", () => {
  it("signatureMatches property refuses any signature that was not derived", () => {
    fc.assert(
      fc.property(fc.stringMatching(/^[A-Za-z0-9_-]{1,20}$/), (signature) => {
        const token = signedWith({ exp: FAR_FUTURE });
        const [header, body] = token.split(".");

        expect(
          statusOf(requestWith(`Bearer ${header}.${body}.${signature}`)),
        ).toBe("invalid");
      }),
    );
  });
});

describe("equalsInConstantTime", () => {
  it("equalsInConstantTime property refuses a signature of another length", () => {
    fc.assert(
      fc.property(fc.stringMatching(/^[A-Za-z0-9_-]{1,80}$/), (signature) => {
        const token = signedWith({ exp: FAR_FUTURE });
        const [header, body, real] = token.split(".");
        fc.pre(signature.length !== (real ?? "").length);

        expect(
          statusOf(requestWith(`Bearer ${header}.${body}.${signature}`)),
        ).toBe("invalid");
      }),
    );
  });

  it("refuses a signature that merely starts with the real one", () => {
    const token = signedWith({ exp: FAR_FUTURE });
    const [header, body, real] = token.split(".");

    expect(statusOf(requestWith(`Bearer ${header}.${body}.${real}extra`))).toBe(
      "invalid",
    );
  });

  it("refuses a signature that differs in its first character only", () => {
    const token = signedWith({ exp: FAR_FUTURE });
    const [header, body, real] = token.split(".");
    const head = real?.startsWith("a") === true ? "b" : "a";

    expect(
      statusOf(
        requestWith(`Bearer ${header}.${body}.${head}${real?.slice(1) ?? ""}`),
      ),
    ).toBe("invalid");
  });

  it("refuses a signature that differs in one character only", () => {
    const token = signedWith({ exp: FAR_FUTURE });
    const [header, body, real] = token.split(".");
    const flipped = `${real?.slice(0, -1) ?? ""}${real?.endsWith("a") ? "b" : "a"}`;

    expect(statusOf(requestWith(`Bearer ${header}.${body}.${flipped}`))).toBe(
      "invalid",
    );
  });
});
