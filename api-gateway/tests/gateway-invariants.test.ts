import { describe, expect, it } from "vitest";
import {
  directivesNamed,
  gatewayConfigurationText,
  njsModuleText,
} from "./nginx-config-support";

const EXPECTED_RESPONSE_HEADERS = [
  "Access-Control-Allow-Origin $allowed_origin always",
  "Access-Control-Allow-Credentials true always",
  "Access-Control-Allow-Headers Authorization, Content-Type, Range always",
  "Access-Control-Expose-Headers "
    + "Accept-Ranges, Content-Range, Content-Length always",
  "Access-Control-Allow-Methods "
    + "GET, POST, PUT, PATCH, DELETE, OPTIONS always",
  "Access-Control-Max-Age 3600 always",
  "Vary Origin always",
];

const MAXIMUM_CONFIGURATION_LINES = 200;
const HTTP_LEVEL = "http";
const SERVER_LEVEL = "http/server";
const PREFLIGHT_GUARD_COUNT = 4;
const JWT_GUARD_COUNT = 3;

function occurrences(pattern: RegExp): number {
  return (gatewayConfigurationText().match(pattern) ?? []).length;
}

describe("gateway configuration invariants", () => {
  it("sends browsers exactly the response headers it already sent", () => {
    const sent = directivesNamed("add_header").map((directive) => {
      return directive.arguments.join(" ");
    });

    expect(sent).toEqual(EXPECTED_RESPONSE_HEADERS);
  });

  it("leaves a throttled response body to nginx, not a custom page", () => {
    expect(gatewayConfigurationText()).not.toContain("error_page");
  });

  it("keeps the whole gateway configuration under the line limit", () => {
    const lines = gatewayConfigurationText().split("\n").length;

    expect(lines).toBeLessThan(MAXIMUM_CONFIGURATION_LINES);
  });

  it("declares every shared rate-limit counter once for all servers", () => {
    const zones = directivesNamed("limit_req_zone");

    expect(zones.length).toBeGreaterThan(0);

    for (const zone of zones) {
      expect(zone.level).toBe(HTTP_LEVEL);
    }
  });

  it("declares every selector map where nginx allows a map", () => {
    const maps = directivesNamed("map");

    expect(maps.length).toBeGreaterThan(0);

    for (const declared of maps) {
      expect(declared.level).toBe(HTTP_LEVEL);
    }
  });

  it("applies the limits and the rejection status inside the server", () => {
    const applied = directivesNamed("limit_req")
      .concat(directivesNamed("limit_req_status"));

    expect(applied.length).toBeGreaterThan(0);

    for (const directive of applied) {
      expect(directive.level).toBe(SERVER_LEVEL);
    }
  });

  it("still answers every CORS preflight with 204 before any proxying", () => {
    const guard = /if \(\$request_method = OPTIONS\) \{\s*return 204;\s*\}/g;

    expect(occurrences(guard)).toBe(PREFLIGHT_GUARD_COUNT);
  });

  it("still refuses an unverified token with 401 where it did", () => {
    const guard = /if \(\$jwt_status != "ok"\) \{\s*return 401;\s*\}/g;

    expect(occurrences(guard)).toBe(JWT_GUARD_COUNT);
  });

  it("still hands nginx the token status and nothing else", () => {
    const source = njsModuleText();

    expect(source.trim().endsWith("export default { status };")).toBe(true);
    expect((source.match(/^export /gm) ?? []).length).toBe(1);
  });
});
