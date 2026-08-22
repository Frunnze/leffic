import { describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import crypto from "crypto";
import { SECRET, requestWith, signedWith, statusOf } from "./jwt-support";

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
