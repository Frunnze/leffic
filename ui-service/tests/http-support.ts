import { afterEach, beforeEach, vi } from "vitest";
import { Session } from "../src/shared/api/session";

export const ENDPOINT = "/api/content/folders";

beforeEach(() => {
  Session.store("token");
});

afterEach(() => {
  vi.unstubAllGlobals();
  Session.store(null);
});
