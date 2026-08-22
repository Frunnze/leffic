import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { Json } from "../src/shared/api/json";
import "./json-support";

describe("Json.numberOr", () => {
  it("numberOr property prefers the value over the fallback", () => {
    fc.assert(
      fc.property(fc.integer(), fc.integer(), (payload, fallback) => {
        expect(Json.numberOr(payload, fallback)).toBe(payload);
      }),
    );
  });

  it("numberOr property falls back when the value is not a number", () => {
    fc.assert(
      fc.property(
        fc.oneof(fc.string(), fc.constant(NaN)),
        fc.integer(),
        (payload, fallback) => {
          expect(Json.numberOr(payload, fallback)).toBe(fallback);
        },
      ),
    );
  });
});

describe("Json.stringOr", () => {
  it("stringOr property prefers the value over the fallback", () => {
    fc.assert(
      fc.property(fc.string(), fc.string(), (payload, fallback) => {
        expect(Json.stringOr(payload, fallback)).toBe(payload);
      }),
    );
  });

  it("stringOr property falls back when the value is not a string", () => {
    fc.assert(
      fc.property(fc.integer(), fc.string(), (payload, fallback) => {
        expect(Json.stringOr(payload, fallback)).toBe(fallback);
      }),
    );
  });
});

describe("Json.identifier", () => {
  it("identifier property always reads back as a string", () => {
    fc.assert(
      fc.property(fc.oneof(fc.string(), fc.integer()), (payload) => {
        expect(Json.identifier(payload, "id")).toBe(String(payload));
      }),
    );
  });

  it("identifier property refuses what cannot name a row", () => {
    fc.assert(
      fc.property(fc.oneof(fc.constant(null), fc.boolean()), (payload) => {
        expect(() => Json.identifier(payload, "id")).toThrow("id");
      }),
    );
  });
});
