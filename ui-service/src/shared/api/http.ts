import { Session } from "./session";

export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export type RequestBody = Readonly<Record<string, unknown>> | FormData | null;

export type HttpRequest = {
  readonly endpoint: string;
  readonly method?: HttpMethod;
  readonly headers?: Readonly<Record<string, string>>;
  readonly body?: RequestBody;
  readonly withToken?: boolean;
  readonly credentials?: RequestCredentials;
};

export class UnauthorizedError extends Error {
  constructor() {
    super("The session expired and could not be refreshed");
    this.name = "UnauthorizedError";
  }
}

export class HttpError extends Error {
  constructor(
    readonly status: number,
    readonly endpoint: string,
  ) {
    super(`Request to ${endpoint} failed with status ${status}`);
    this.name = "HttpError";
  }
}

export class HttpClient {
  static async send(request: HttpRequest): Promise<Response> {
    const needsToken = request.withToken !== false;

    if (needsToken && Session.currentToken() === null) {
      const refreshed = await Session.refresh();
      if (refreshed === null) throw new UnauthorizedError();
    }

    const response = await HttpClient.dispatch(request, needsToken);
    if (response.status !== 401 || !needsToken) return response;

    const refreshed = await Session.refresh();
    if (refreshed === null) throw new UnauthorizedError();

    return HttpClient.dispatch(request, needsToken);
  }

  static async json(request: HttpRequest): Promise<unknown> {
    const response = await HttpClient.send(request);

    if (!response.ok) {
      throw new HttpError(response.status, request.endpoint);
    }

    const payload: unknown = await response.json();

    return payload;
  }

  static async blob(request: HttpRequest): Promise<Blob> {
    const response = await HttpClient.send(request);

    if (!response.ok) {
      throw new HttpError(response.status, request.endpoint);
    }

    return response.blob();
  }

  private static dispatch(
    request: HttpRequest,
    needsToken: boolean,
  ): Promise<Response> {
    const headers: Record<string, string> = { ...request.headers };
    const token = Session.currentToken();

    if (needsToken && token !== null) {
      headers.Authorization = `Bearer ${token}`;
    }

    return fetch(`${Session.baseUrl}${request.endpoint}`, {
      method: request.method ?? "GET",
      headers,
      credentials: request.credentials ?? "same-origin",
      body: HttpClient.encodeBody(request.body ?? null, headers),
    });
  }

  private static encodeBody(
    body: RequestBody,
    headers: Record<string, string>,
  ): BodyInit | null {
    if (body === null) return null;

    if (body instanceof FormData) return body;

    headers["Content-Type"] = "application/json";

    return JSON.stringify(body);
  }
}
