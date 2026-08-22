import { afterEach, describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import { AuthApi } from "../src/features/authentication/authentication-api";
import { Session } from "../src/shared/api/session";
import {
  jsonResponse,
  requestedInit,
  requestedUrl,
  stubFetch,
} from "./support";

const CREDENTIALS = { email: "learner@example.test", password: "secret" };
const REGISTRATION = { ...CREDENTIALS, username: "learner" };

afterEach(() => {
  vi.unstubAllGlobals();
  Session.store(null);
});

describe("AuthApi.logIn", () => {
  it("logIn property stores the token the gateway handed back", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string({ minLength: 1 }), async (token) => {
        stubFetch(jsonResponse({ access_token: token }));

        await expect(AuthApi.logIn(CREDENTIALS)).resolves.toEqual({ ok: true });
        expect(Session.currentToken()).toBe(token);
      }),
    );
  });

  it("logIn property sends the credentials it was given, and no token", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.emailAddress(),
        fc.string({ minLength: 1 }),
        async (email, password) => {
          const fetching = stubFetch(jsonResponse({ access_token: "t" }));

          await AuthApi.logIn({ email, password });

          expect(requestedUrl(fetching)).toContain("/api/user/login");
          expect(requestedInit(fetching).body).toBe(
            JSON.stringify({ email, password }),
          );
          expect(requestedInit(fetching).credentials).toBe("include");
        },
      ),
    );
  });

  it("blames the form when the credentials do not match", async () => {
    stubFetch(jsonResponse({ detail: "no" }, 401));

    await expect(AuthApi.logIn(CREDENTIALS)).resolves.toEqual({
      ok: false,
      field: "form",
      message:
        "That email and password don't match. Try again, or reset your password.",
    });
  });
});

describe("AuthApi.signUp", () => {
  it("signUp property stores the token a new account was given", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string({ minLength: 1 }), async (token) => {
        stubFetch(jsonResponse({ access_token: token }));

        await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual({
          ok: true,
        });
        expect(Session.currentToken()).toBe(token);
      }),
    );
  });

  it("sends the whole registration to the sign-up endpoint", async () => {
    const fetching = stubFetch(jsonResponse({ access_token: "t" }));

    await AuthApi.signUp(REGISTRATION);

    expect(requestedUrl(fetching)).toContain("/api/user/sign-up");
    expect(requestedInit(fetching).body).toBe(
      JSON.stringify({
        username: REGISTRATION.username,
        email: REGISTRATION.email,
        password: REGISTRATION.password,
      }),
    );
  });
});

describe("AuthApi.toSignUpFailure", () => {
  it("toSignUpFailure property always blames a field the form can show", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string(), async (detail) => {
        stubFetch(jsonResponse(detail, 400));

        const outcome = await AuthApi.signUp(REGISTRATION);

        expect(outcome.ok).toBe(false);
        expect(["username", "email", "form"]).toContain(
          outcome.ok ? "form" : outcome.field,
        );
      }),
    );
  });

  it("blames the username when it is already registered", async () => {
    stubFetch(jsonResponse("Username already registered", 400));

    await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual({
      ok: false,
      field: "username",
      message: "That username is taken. Try another one.",
    });
  });

  it("blames the email when it is already registered", async () => {
    stubFetch(jsonResponse("Email already registered", 400));

    await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual({
      ok: false,
      field: "email",
      message: "An account already uses that email. Log in instead.",
    });
  });

  it("blames the form when the reason is not a plain sentence", async () => {
    stubFetch(jsonResponse({ detail: "odd" }, 400));

    await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual({
      ok: false,
      field: "form",
      message: "We couldn't create the account. Try again.",
    });
  });
});

describe("AuthApi.logOut", () => {
  it("logOut property always leaves the session empty", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string({ minLength: 1 }), async (token) => {
        Session.store(token);
        stubFetch(jsonResponse({}));

        await AuthApi.logOut();

        expect(Session.currentToken()).toBeNull();
      }),
    );
  });

  it("tells the gateway to drop the refresh cookie", async () => {
    Session.store("token");
    const fetching = stubFetch(jsonResponse({}));

    await AuthApi.logOut();

    expect(requestedUrl(fetching)).toContain("/api/user/logout");
    expect(requestedInit(fetching).credentials).toBe("include");
  });
});
