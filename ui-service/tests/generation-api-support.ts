import { afterEach, beforeEach, vi } from "vitest";
import { Session } from "../src/shared/api/session";
import { requestedInit, stubFetch } from "./support";

export const FILE_SOURCE = {
  kind: "file",
  fileId: "9",
  extension: "pdf",
  firstPage: null,
  lastPage: null,
} as const;

export const ORIGIN = { kind: "file", reference: "notes.pdf" } as const;

export function sentBody(
  fetching: ReturnType<typeof stubFetch>,
  call = 0,
): unknown {
  return JSON.parse(String(requestedInit(fetching, call).body));
}

beforeEach(() => {
  Session.store("token");
});

afterEach(() => {
  vi.unstubAllGlobals();
  Session.store(null);
});
