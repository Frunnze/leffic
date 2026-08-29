import { afterEach, describe, expect, it, vi } from "vitest";
import { AuthApi } from "../src/features/authentication/authentication-api";
import { Session } from "../src/shared/api/session";
import {
  blobResponse,
  emptyResponse,
  jsonResponse,
  stubFetch,
} from "./support";

const REGISTRATION = {
  email: "learner@example.test",
  password: "secret",
  username: "learner",
};

const GENERIC_SIGN_UP_FAILURE = {
  ok: false,
  field: "form",
  message: "We couldn't create the account. Try again.",
};

const EMAIL_TAKEN_FAILURE = {
  ok: false,
  field: "email",
  message: "An account already uses that email. Log in instead.",
};

const THROTTLED = 429;
const BAD_REQUEST = 400;
const BAD_GATEWAY = 502;
const HUGE_BODY_LENGTH = 100_000;



afterEach(() => {
  vi.unstubAllGlobals();
  Session.store(null);
});

describe("sign-up against an error body that is not JSON", () => {
  it("blames the form when the gateway returns an HTML page", async () => {
    stubFetch(blobResponse("<html><body>502</body></html>", BAD_GATEWAY));

    await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual(
      GENERIC_SIGN_UP_FAILURE,
    );
  });

  it("blames the form when the error carries no body at all", async () => {
    stubFetch(emptyResponse(BAD_GATEWAY));

    await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual(
      GENERIC_SIGN_UP_FAILURE,
    );
  });

  it("blames the form when the error body is truncated JSON", async () => {
    stubFetch(blobResponse('{"code": "email_regis', BAD_REQUEST));

    await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual(
      GENERIC_SIGN_UP_FAILURE,
    );
  });

  it("still blames the email when a JSON body names it as taken", async () => {
    stubFetch(jsonResponse({ code: "email_registered" }, BAD_REQUEST));

    await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual(
      EMAIL_TAKEN_FAILURE,
    );
  });
});


describe("sign-up against a hostile error body", () => {
  it("blames the form when a throttled sign-up sends text", async () => {
    stubFetch(blobResponse("429 Too Many Requests", THROTTLED));

    await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual(
      GENERIC_SIGN_UP_FAILURE,
    );
  });

  it("blames the form when the error body is only whitespace", async () => {
    stubFetch(blobResponse("   \n\t  ", BAD_REQUEST));

    await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual(
      GENERIC_SIGN_UP_FAILURE,
    );
  });

  it("blames the form when the body is a lone opening brace", async () => {
    stubFetch(blobResponse("{", BAD_REQUEST));

    await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual(
      GENERIC_SIGN_UP_FAILURE,
    );
  });

  it("blames the form when the error body is unicode prose", async () => {
    stubFetch(blobResponse("Ошибка \u{1F4A5} 你好", BAD_REQUEST));

    await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual(
      GENERIC_SIGN_UP_FAILURE,
    );
  });

  it("blames the form when the error body is enormous", async () => {
    stubFetch(blobResponse("x".repeat(HUGE_BODY_LENGTH), BAD_REQUEST));

    await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual(
      GENERIC_SIGN_UP_FAILURE,
    );
  });

  it("blames the form when the error body is a bare JSON scalar", async () => {
    stubFetch(jsonResponse("email_registered", BAD_REQUEST));

    await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual(
      GENERIC_SIGN_UP_FAILURE,
    );
  });

  it("leaves no session behind when the body cannot be read", async () => {
    stubFetch(blobResponse("<html>429</html>", THROTTLED));

    await AuthApi.signUp(REGISTRATION);

    expect(Session.currentToken()).toBeNull();
  });
});
