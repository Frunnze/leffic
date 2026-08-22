import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { Json } from "../src/shared/api/json";
import { NOT_AN_OBJECT } from "./json-support";

describe("Json.object", () => {
  it("object property returns the very object it was given", () => {
    fc.assert(
      fc.property(fc.dictionary(fc.string(), fc.integer()), (payload) => {
        expect(Json.object(payload, "field")).toBe(payload);
      }),
    );
  });

  it("object property names the field it refused", () => {
    fc.assert(
      fc.property(
        NOT_AN_OBJECT,
        fc.string({ minLength: 1 }),
        (payload, field) => {
          expect(() => Json.object(payload, field)).toThrow(field);
        },
      ),
    );
  });
});

describe("Json.array", () => {
  it("array property returns the very array it was given", () => {
    fc.assert(
      fc.property(fc.array(fc.integer()), (payload) => {
        expect(Json.array(payload, "field")).toBe(payload);
      }),
    );
  });

  it("array property refuses anything that is not an array", () => {
    fc.assert(
      fc.property(
        fc.oneof(fc.string(), fc.integer(), fc.constant(null)),
        (payload) => {
          expect(() => Json.array(payload, "field")).toThrow("an array");
        },
      ),
    );
  });
});

describe("Json.string", () => {
  it("string property returns the very string it was given", () => {
    fc.assert(
      fc.property(fc.string(), (payload) => {
        expect(Json.string(payload, "field")).toBe(payload);
      }),
    );
  });

  it("string property refuses anything that is not a string", () => {
    fc.assert(
      fc.property(
        fc.oneof(fc.integer(), fc.constant(null), fc.boolean()),
        (payload) => {
          expect(() => Json.string(payload, "field")).toThrow("a string");
        },
      ),
    );
  });
});

describe("Json.number", () => {
  it("number property returns the very number it was given", () => {
    fc.assert(
      fc.property(fc.integer(), (payload) => {
        expect(Json.number(payload, "field")).toBe(payload);
      }),
    );
  });

  it("number property refuses anything that is not a real number", () => {
    fc.assert(
      fc.property(
        fc.oneof(fc.string(), fc.constant(null), fc.constant(NaN)),
        (payload) => {
          expect(() => Json.number(payload, "field")).toThrow("a number");
        },
      ),
    );
  });
});

describe("Json.optionalString", () => {
  it("optionalString property keeps a string as it is", () => {
    fc.assert(
      fc.property(fc.string(), (payload) => {
        expect(Json.optionalString(payload)).toBe(payload);
      }),
    );
  });

  it("optionalString property turns anything else into null", () => {
    fc.assert(
      fc.property(
        fc.oneof(fc.integer(), fc.constant(null), fc.boolean()),
        (payload) => {
          expect(Json.optionalString(payload)).toBeNull();
        },
      ),
    );
  });
});

describe("Json.strings", () => {
  it("strings property keeps every string it is given", () => {
    fc.assert(
      fc.property(fc.array(fc.string()), (payload) => {
        expect(Json.strings(payload)).toEqual(payload);
      }),
    );
  });

  it("strings property drops everything that is not a string", () => {
    fc.assert(
      fc.property(fc.array(fc.oneof(fc.string(), fc.integer())), (payload) => {
        const kept = Json.strings(payload);

        expect(kept.every((entry) => typeof entry === "string")).toBe(true);
      }),
    );
  });

  it("turns a non-array into an empty list", () => {
    expect(Json.strings("nope")).toEqual([]);
  });
});

describe("Json.optionalObject", () => {
  it("optionalObject property keeps an object as it is", () => {
    fc.assert(
      fc.property(fc.dictionary(fc.string(), fc.integer()), (payload) => {
        expect(Json.optionalObject(payload)).toBe(payload);
      }),
    );
  });

  it("optionalObject property turns anything else into null", () => {
    fc.assert(
      fc.property(NOT_AN_OBJECT, (payload) => {
        expect(Json.optionalObject(payload)).toBeNull();
      }),
    );
  });
});

describe("Json.optionalNumber", () => {
  it("optionalNumber property keeps a number as it is", () => {
    fc.assert(
      fc.property(fc.integer(), (payload) => {
        expect(Json.optionalNumber(payload)).toBe(payload);
      }),
    );
  });

  it("optionalNumber property turns anything else into null", () => {
    fc.assert(
      fc.property(
        fc.oneof(fc.string(), fc.constant(null), fc.constant(NaN)),
        (payload) => {
          expect(Json.optionalNumber(payload)).toBeNull();
        },
      ),
    );
  });
});
