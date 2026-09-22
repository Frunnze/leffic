import { describe, expect, it } from "vitest";
import {
  ConfigDirective,
  argumentText,
  directivesNamed,
  gatewayConfigurationText,
  njsModuleText,
} from "./nginx-config-support";
import {
  ACCESS_GUARD_DIRECTIVE,
  LOCATION_DIRECTIVE,
  PROTECTED_LOCATIONS,
  PROXIED_LOCATIONS,
  PUBLIC_USER_LOCATION,
  accessGuardsOf,
  requiredLocation,
} from "./gateway-location-support";
import {
  PREFLIGHT_METHOD,
  PREFLIGHT_STATUS,
  REFUSED_TOKEN_STATUS,
} from "./jwt-support";

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
const MAXIMUM_LINE_LENGTH = 80;
const HTTP_LEVEL = "http";
const SERVER_LEVEL = "http/server";
const PUBLIC_GUARD = "jwt.guardPublicRoute";
const PROTECTED_GUARD = "jwt.guardProtectedRoute";
const GUARDS = [PUBLIC_GUARD, PROTECTED_GUARD];
const GUARD_EXPORT =
  "export default { guardPublicRoute, guardProtectedRoute };";
const NAMED_GUARD_LITERALS = [
  PREFLIGHT_METHOD,
  String(PREFLIGHT_STATUS),
  String(REFUSED_TOKEN_STATUS),
];
const CONSTANT_DECLARATION = "const ";
const FINALIZING_DIRECTIVE = "return";
const BRANCHING_DIRECTIVE = "if";
const NGINX_VARIABLES_PROPERTY = "variables";
const SINGLE_OCCURRENCE = 1;

function overlongConfigurationLines(): readonly string[] {
  return gatewayConfigurationText().split("\n").filter((line) => {
    return line.length > MAXIMUM_LINE_LENGTH;
  });
}

function runsProtectedGuard(location: ConfigDirective): boolean {
  return accessGuardsOf(location).includes(PROTECTED_GUARD);
}

describe("gateway configuration invariants", () => {
  it("sends browsers exactly the response headers it already sent", () => {
    const sent = directivesNamed("add_header").map(argumentText);

    expect(sent).toEqual(EXPECTED_RESPONSE_HEADERS);
  });

  it("leaves a throttled response body to nginx, not a custom page", () => {
    expect(gatewayConfigurationText()).not.toContain("error_page");
  });

  it("keeps the whole gateway configuration under the line limit", () => {
    const lines = gatewayConfigurationText().split("\n").length;

    expect(lines).toBeLessThan(MAXIMUM_CONFIGURATION_LINES);
  });

  it("keeps every gateway configuration line inside eighty columns", () => {
    expect(overlongConfigurationLines()).toEqual([]);
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
});

describe("gateway early exits wait for the rate limits", () => {
  it("finalizes no request before the rate limits run", () => {
    expect(directivesNamed(FINALIZING_DIRECTIVE)).toEqual([]);
  });

  it("branches no location on the method or the token status", () => {
    expect(directivesNamed(BRANCHING_DIRECTIVE)).toEqual([]);
  });

  it("runs exactly one njs guard in every proxied location", () => {
    for (const signature of PROXIED_LOCATIONS) {
      const guards = accessGuardsOf(requiredLocation(signature));

      expect(guards.length).toBe(SINGLE_OCCURRENCE);
      expect(GUARDS).toContain(guards[0]);
    }
  });

  it("runs the public guard in the public user location", () => {
    const location = requiredLocation(PUBLIC_USER_LOCATION);

    expect(accessGuardsOf(location)).toEqual([PUBLIC_GUARD]);
  });

  it("runs the protected guard in exactly the protected locations", () => {
    const locations = directivesNamed(LOCATION_DIRECTIVE);
    const guarded = locations.filter(runsProtectedGuard);
    const accessGuards = directivesNamed(ACCESS_GUARD_DIRECTIVE);
    const protectedGuards = accessGuards.filter((guard) => {
      return argumentText(guard) === PROTECTED_GUARD;
    });

    expect(new Set(guarded.map(argumentText))).toEqual(
      new Set(PROTECTED_LOCATIONS),
    );
    expect(protectedGuards.length).toBe(PROTECTED_LOCATIONS.length);
  });
});

describe("the njs module the gateway runs", () => {
  it("exports exactly the two guards and nothing else", () => {
    const source = njsModuleText();

    expect(source.trim().endsWith(GUARD_EXPORT)).toBe(true);
    expect((source.match(/^export /gm) ?? []).length).toBe(1);
  });

  it("reads no nginx variable in either guard", () => {
    expect(njsModuleText()).not.toContain(NGINX_VARIABLES_PROPERTY);
  });

  it("names the preflight method and both statuses as constants", () => {
    const source = njsModuleText();

    for (const literal of NAMED_GUARD_LITERALS) {
      const occurrences = source.split(literal).length - 1;
      const namingLine = source.split("\n").find((line) => {
        return line.includes(literal);
      });

      expect(occurrences).toBe(SINGLE_OCCURRENCE);
      expect(namingLine?.startsWith(CONSTANT_DECLARATION)).toBe(true);
    }
  });
});
