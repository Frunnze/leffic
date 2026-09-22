import { beforeEach, expect, vi } from "vitest";
import crypto from "crypto";
import fc from "fast-check";
import jwt from "../src/jwt";

export const SECRET = "a-very-secret-key";
export const SECRET_VARIABLE = "JWT_SECRET_KEY";
export const MISSING_SECRET_ERROR = `${SECRET_VARIABLE} is not set`;
export const EMPTY_SECRET = "";
export const MISSING_SECRETS = [EMPTY_SECRET, undefined];

export const PREFLIGHT_METHOD = "OPTIONS";
export const PREFLIGHT_STATUS = 204;
export const REFUSED_TOKEN_STATUS = 401;

export const POST_METHOD = "POST";
export const PUT_METHOD = "PUT";
export const DELETE_METHOD = "DELETE";

const ORDINARY_METHOD = "GET";
const ORDINARY_METHODS = [
  ORDINARY_METHOD,
  POST_METHOD,
  PUT_METHOD,
  "PATCH",
  DELETE_METHOD,
  "HEAD",
];

const VERIFIED_TOKEN_STATUS = "ok";
const UNVERIFIED_TOKEN_STATUS = "invalid";
const STATUS_ONLY_ARGUMENT_COUNT = 1;

type FakeRequest = {
  method: string;
  headersIn: { Authorization?: string };
  error: ReturnType<typeof vi.fn>;
  return: ReturnType<typeof vi.fn>;
};

type RouteGuard = (request: NginxHTTPRequest) => void;

export function requestUsing(
  method: string,
  authorization?: string,
): FakeRequest {
  return {
    method,
    headersIn:
      authorization === undefined ? {} : { Authorization: authorization },
    error: vi.fn(),
    return: vi.fn(),
  };
}

export function requestWith(authorization?: string): FakeRequest {
  return requestUsing(ORDINARY_METHOD, authorization);
}

export function bearerAuthorization(token: string): string {
  return `Bearer ${token}`;
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

function guardAnswers(guard: RouteGuard, request: FakeRequest): unknown[][] {
  guard(request as unknown as NginxHTTPRequest);

  return request.return.mock.calls;
}

export function publicGuardAnswers(request: FakeRequest): unknown[][] {
  return guardAnswers(jwt.guardPublicRoute, request);
}

export function protectedGuardAnswers(request: FakeRequest): unknown[][] {
  return guardAnswers(jwt.guardProtectedRoute, request);
}

export function statusOf(request: FakeRequest): string {
  if (protectedGuardAnswers(request).length === 0) {
    return VERIFIED_TOKEN_STATUS;
  }

  return UNVERIFIED_TOKEN_STATUS;
}

export function expectNoResponseBody(answers: unknown[][]): void {
  for (const answer of answers) {
    expect(answer).toHaveLength(STATUS_ONLY_ARGUMENT_COUNT);
  }
}

export const FAR_FUTURE = 4102444800;
export const LONG_PAST = 946684800;

const VERIFIED_TOKEN = signedWith({ exp: FAR_FUTURE });

export const VERIFIED_AUTHORIZATION = bearerAuthorization(VERIFIED_TOKEN);

export const nonPreflightMethodArbitrary = fc
  .oneof(fc.constantFrom(...ORDINARY_METHODS), fc.string())
  .filter((method) => method !== PREFLIGHT_METHOD);

const methodArbitrary = fc.oneof(
  fc.constant(PREFLIGHT_METHOD),
  nonPreflightMethodArbitrary,
);

export const authorizationOrNoneArbitrary = fc.option(
  fc.oneof(fc.string(), fc.constant(VERIFIED_AUTHORIZATION)),
  { nil: undefined },
);

export const requestPartsArbitrary = fc.tuple(
  methodArbitrary,
  authorizationOrNoneArbitrary,
);

export const foreignTokenArbitrary = fc
  .string({ minLength: 1 })
  .filter((otherSecret) => otherSecret !== SECRET)
  .map((otherSecret) => signedWith({ exp: FAR_FUTURE }, otherSecret));

export const missingSecretArbitrary = fc.constantFrom(...MISSING_SECRETS);

beforeEach(() => {
  vi.stubEnv(SECRET_VARIABLE, SECRET);
});
