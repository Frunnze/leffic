import fc from "fast-check";

export const NOT_AN_OBJECT = fc.oneof(
  fc.string(),
  fc.integer(),
  fc.boolean(),
  fc.constant(null),
  fc.array(fc.integer()),
);
