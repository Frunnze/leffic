export type JsonObject = Readonly<Record<string, unknown>>;

class JsonDecodeError extends Error {
  constructor(field: string, expected: string, received: unknown) {
    super(`Field "${field}" should be ${expected} but was ${typeof received}`);
    this.name = "JsonDecodeError";
  }
}

export class Json {
  static object(value: unknown, field: string): JsonObject {
    if (typeof value !== "object" || value === null || Array.isArray(value)) {
      throw new JsonDecodeError(field, "an object", value);
    }

    return value as JsonObject;
  }

  static array(value: unknown, field: string): readonly unknown[] {
    if (!Array.isArray(value)) {
      throw new JsonDecodeError(field, "an array", value);
    }

    return value;
  }

  static string(value: unknown, field: string): string {
    if (typeof value !== "string") {
      throw new JsonDecodeError(field, "a string", value);
    }

    return value;
  }

  static number(value: unknown, field: string): number {
    if (typeof value !== "number" || Number.isNaN(value)) {
      throw new JsonDecodeError(field, "a number", value);
    }

    return value;
  }

  static optionalString(value: unknown): string | null {
    return typeof value === "string" ? value : null;
  }

  static strings(value: unknown): readonly string[] {
    if (!Array.isArray(value)) return [];

    return value.filter((entry): entry is string => typeof entry === "string");
  }

  static optionalObject(value: unknown): JsonObject | null {
    if (typeof value !== "object" || value === null || Array.isArray(value)) {
      return null;
    }

    return value as JsonObject;
  }

  static optionalNumber(value: unknown): number | null {
    return typeof value === "number" && !Number.isNaN(value) ? value : null;
  }

  static numberOr(value: unknown, fallback: number): number {
    return typeof value === "number" && !Number.isNaN(value) ? value : fallback;
  }

  static stringOr(value: unknown, fallback: string): string {
    return typeof value === "string" ? value : fallback;
  }

  static identifier(value: unknown, field: string): string {
    if (typeof value === "string") {
      return value;
    }

    if (typeof value === "number") {
      return String(value);
    }

    throw new JsonDecodeError(field, "a string or number id", value);
  }
}
