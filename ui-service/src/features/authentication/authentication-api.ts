import { HttpClient } from "../../shared/api/http";
import { Json } from "../../shared/api/json";
import { Session } from "../../shared/api/session";

export type Credentials = {
  readonly email: string;
  readonly password: string;
};

export type Registration = Credentials & {
  readonly username: string;
};

export type AuthOutcome =
  | { readonly ok: true }
  | { readonly ok: false; readonly field: "username" | "email" | "form"; readonly message: string };

const SIGN_IN_FAILED =
  "That email and password don't match. Try again, or reset your password.";

export class AuthApi {
  static async logIn(credentials: Credentials): Promise<AuthOutcome> {
    const response = await HttpClient.send({
      endpoint: "/api/user/login",
      method: "POST",
      body: { email: credentials.email, password: credentials.password },
      withToken: false,
      credentials: "include",
    });

    if (!response.ok) {
      return { ok: false, field: "form", message: SIGN_IN_FAILED };
    }

    const payload: unknown = await response.json();
    Session.store(Json.stringOrNull(Json.object(payload, "login").access_token));

    return { ok: true };
  }

  static async signUp(registration: Registration): Promise<AuthOutcome> {
    const response = await HttpClient.send({
      endpoint: "/api/user/sign-up",
      method: "POST",
      body: {
        username: registration.username,
        email: registration.email,
        password: registration.password,
      },
      withToken: false,
      credentials: "include",
    });
    const payload: unknown = await response.json();

    if (!response.ok) {
      return AuthApi.toSignUpFailure(payload);
    }

    Session.store(Json.stringOrNull(Json.object(payload, "signUp").access_token));

    return { ok: true };
  }

  static async logOut(): Promise<void> {
    await HttpClient.send({
      endpoint: "/api/user/logout",
      method: "POST",
      credentials: "include",
    });
    Session.store(null);
  }

  private static toSignUpFailure(payload: unknown): AuthOutcome {
    const detail = typeof payload === "string" ? payload : "";

    if (detail === "Username already registered") {
      return {
        ok: false,
        field: "username",
        message: "That username is taken. Try another one.",
      };
    }

    if (detail === "Email already registered") {
      return {
        ok: false,
        field: "email",
        message: "An account already uses that email. Log in instead.",
      };
    }

    return {
      ok: false,
      field: "form",
      message: "We couldn't create the account. Try again.",
    };
  }
}
