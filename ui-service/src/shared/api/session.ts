import { Json } from "./json";

const REFRESH_ENDPOINT = "/api/user/refresh-token";
const LOGIN_ROUTE = "/login";

export class Session {
  private static accessToken: string | null = null;

  static readonly baseUrl: string =
    import.meta.env.VITE_GATEWAY_URL ?? "http://localhost:8888";

  static currentToken(): string | null {
    return Session.accessToken;
  }

  static store(token: string | null): void {
    Session.accessToken = token;
  }

  static async refresh(): Promise<string | null> {
    const response = await fetch(`${Session.baseUrl}${REFRESH_ENDPOINT}`, {
      method: "POST",
      credentials: "include",
    });

    if (response.status === 401) {
      Session.store(null);
      window.location.href = LOGIN_ROUTE;
      return null;
    }

    if (!response.ok) {
      return null;
    }

    const payload: unknown = await response.json();
    const token = Json.stringOrNull(Json.object(payload, "session").access_token);
    Session.store(token);

    return token;
  }
}
