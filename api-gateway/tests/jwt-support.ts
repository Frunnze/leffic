import { beforeEach, vi } from "vitest";
import crypto from "crypto";
import jwt from "../src/jwt";

export const SECRET = "a-very-secret-key";

type FakeRequest = {
  headersIn: { Authorization?: string };
  error: ReturnType<typeof vi.fn>;
};

export function requestWith(authorization?: string): FakeRequest {
  return {
    headersIn:
      authorization === undefined ? {} : { Authorization: authorization },
    error: vi.fn(),
  };
}

export function signedWith(
  claims: Record<string, unknown>,
  secret = SECRET,
): string {
  const header = Buffer.from(JSON.stringify({ alg: "HS256" })).toString(
    "base64url",
  );
  const body = Buffer.from(JSON.stringify(claims)).toString("base64url");
  const signature = crypto
    .createHmac("sha256", secret)
    .update(`${header}.${body}`)
    .digest("base64url");

  return `${header}.${body}.${signature}`;
}

export function statusOf(request: FakeRequest): string {
  return jwt.status(request as unknown as NginxHTTPRequest);
}

export const FAR_FUTURE = 4102444800;
export const LONG_PAST = 946684800;

beforeEach(() => {
  vi.stubEnv("JWT_SECRET_KEY", SECRET);
});
