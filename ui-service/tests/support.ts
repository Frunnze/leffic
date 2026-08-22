import { vi } from "vitest";

type Stubbed = ReturnType<typeof vi.fn>;

export function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

export function blobResponse(body: string, status = 200): Response {
  return new Response(body, { status });
}

export function emptyResponse(status: number): Response {
  return new Response(null, { status });
}

export function stubFetch(...responses: readonly Response[]): Stubbed {
  const fetching = vi.fn();

  for (const response of responses) {
    fetching.mockResolvedValueOnce(response);
  }

  vi.stubGlobal("fetch", fetching);

  return fetching;
}

export function requestedUrl(fetching: Stubbed, call = 0): string {
  return String(fetching.mock.calls[call]?.[0]);
}

export function requestedInit(fetching: Stubbed, call = 0): RequestInit {
  return (fetching.mock.calls[call]?.[1] ?? {}) as RequestInit;
}

export function sentHeaders(
  fetching: Stubbed,
  call = 0,
): Record<string, string> {
  return (requestedInit(fetching, call).headers ?? {}) as Record<
    string,
    string
  >;
}
