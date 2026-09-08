import { describe, expect, it } from "vitest";
import { normalisedRequestPath } from "./uri-normalisation-support";

const CHAT_ROUTE = "/api/content/chat";
const LOGIN_ROUTE = "/api/user/login";

describe("the request path a rate-limit selector classifies", () => {
  it("reads a percent-encoded letter as the letter it stands for", () => {
    expect(normalisedRequestPath("/api/content/c%68at")).toBe(CHAT_ROUTE);
  });

  it("collapses a run of repeated slashes into one separator", () => {
    expect(normalisedRequestPath("/api//user///login")).toBe(LOGIN_ROUTE);
  });

  it("walks past a dot segment naming the current directory", () => {
    expect(normalisedRequestPath("/api/content/./chat")).toBe(CHAT_ROUTE);
  });

  it("walks back out of a dot-dot segment before classifying", () => {
    expect(normalisedRequestPath("/api/content/../content/chat")).toBe(
      CHAT_ROUTE,
    );
  });

  it("classifies on the path alone, never on the query string", () => {
    expect(normalisedRequestPath("/api/content/chat?stream=1")).toBe(
      CHAT_ROUTE,
    );
  });

  it("leaves a path that is already normalised exactly as it is", () => {
    expect(normalisedRequestPath(CHAT_ROUTE)).toBe(CHAT_ROUTE);
  });

  it("reduces every evasion in one spelling to the plain route", () => {
    expect(normalisedRequestPath("/api//content/./c%68at?stream=1")).toBe(
      CHAT_ROUTE,
    );
  });
});

describe("the request path nginx refuses to build at all", () => {
  it("refuses a path smuggling an encoded null byte", () => {
    expect(() => normalisedRequestPath("/api/content/ch%00at")).toThrow();
  });

  it("refuses a path whose percent-escape is not hexadecimal", () => {
    expect(() => normalisedRequestPath("/api/content/%zzhat")).toThrow();
    expect(() => normalisedRequestPath("/api/content/%0zhat")).toThrow();
  });

  it("refuses a path that stops in the middle of an escape", () => {
    expect(() => normalisedRequestPath("/api/content/chat%")).toThrow();
    expect(() => normalisedRequestPath("/api/content/chat%4")).toThrow();
  });

  it("refuses a path that climbs above the root it started at", () => {
    expect(() => normalisedRequestPath("/..")).toThrow();
    expect(() => normalisedRequestPath("/api/../../content/chat")).toThrow();
  });
});

describe("the characters nginx writes into the path but never reads", () => {
  it("stops the path at the first fragment marker the client sent", () => {
    expect(normalisedRequestPath("/api/content/chat#anchor")).toBe(CHAT_ROUTE);
    expect(normalisedRequestPath("/api/user/login#%")).toBe(LOGIN_ROUTE);
  });

  it("writes an encoded percent sign back without decoding it twice", () => {
    expect(normalisedRequestPath("/api/content/%2541")).toBe(
      "/api/content/%41",
    );
  });

  it("writes an encoded question mark back without starting a query", () => {
    expect(normalisedRequestPath("/api/content/chat%3Fstream=1")).toBe(
      "/api/content/chat?stream=1",
    );
  });
});
