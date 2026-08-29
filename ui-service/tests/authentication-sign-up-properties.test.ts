import { afterEach, describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import { AuthApi } from "../src/features/authentication/authentication-api";
import { Session } from "../src/shared/api/session";
import { blobResponse, jsonResponse, stubFetch } from "./support";

const REGISTRATION = {
  email: "learner@example.test",
  password: "secret",
  username: "learner",
};

const EMAIL_TAKEN_FAILURE = {
  ok: false,
  field: "email",
  message: "An account already uses that email. Log in instead.",
};

const GENERIC_SIGN_UP_FAILURE = {
  ok: false,
  field: "form",
  message: "We couldn't create the account. Try again.",
};


const FIRST_ERROR_STATUS = 400;
const LAST_ERROR_STATUS = 599;

const errorStatus = fc.integer({
  min: FIRST_ERROR_STATUS,
  max: LAST_ERROR_STATUS,
});

function isUnparseableAsJson(body: string): boolean {
  try {
    JSON.parse(body);

    return false;
  } catch {
    return true;
  }
}

afterEach(() => {
  vi.unstubAllGlobals();
  Session.store(null);
});


describe("sign-up failure properties", () => {
  it("signUp property never throws on an unreadable error body", async () => {
    await fc.assert(
      fc.asyncProperty(
        errorStatus,
        fc.string().filter(isUnparseableAsJson),
        async (status, body) => {
          stubFetch(blobResponse(body, status));

          await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual(
            GENERIC_SIGN_UP_FAILURE,
          );
        },
      ),
    );
  });

  it("readPayload property yields null for every unreadable body", async () => {
    await fc.assert(
      fc.asyncProperty(
        errorStatus,
        fc.string().filter(isUnparseableAsJson),
        async (status, body) => {
          stubFetch(blobResponse(body, status));

          await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual(
            GENERIC_SIGN_UP_FAILURE,
          );
        },
      ),
    );
  });

  it("signUp property resolves to a field the form can mark", async () => {
    await fc.assert(
      fc.asyncProperty(
        errorStatus,
        fc.string(),
        async (status, body) => {
          stubFetch(blobResponse(body, status));

          const outcome = await AuthApi.signUp(REGISTRATION);

          expect(outcome.ok).toBe(false);
          expect(["username", "email", "form"]).toContain(
            outcome.ok ? "form" : outcome.field,
          );
        },
      ),
    );
  });

  it("signUp property reads the code whatever the status", async () => {
    await fc.assert(
      fc.asyncProperty(
        errorStatus,
        async (status) => {
          stubFetch(jsonResponse({ code: "email_registered" }, status));

          await expect(AuthApi.signUp(REGISTRATION)).resolves.toEqual(
            EMAIL_TAKEN_FAILURE,
          );
        },
      ),
    );
  });
});
