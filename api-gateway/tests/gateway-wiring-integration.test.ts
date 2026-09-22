import { describe, expect, it } from "vitest";
import {
  argumentText,
  directivesNamed,
  gatewayConfigurationText,
  rateLimitApplications,
  rateLimitZones,
} from "./nginx-config-support";
import {
  declaredMaps,
  rateLimitSelectorMaps,
} from "./nginx-selector-support";
import {
  CLIENT_ADDRESS_KEY,
  SELECTOR_MAP_COUNT,
} from "./rate-limit-support";
import {
  ACCESS_GUARD_DIRECTIVE,
  ACCOUNT_LOCATION,
  CATCH_ALL_LOCATION,
  CONTENT_LOCATION,
  DOCUMENTS_LOCATION,
  LOCATION_DIRECTIVE,
  PUBLIC_USER_LOCATION,
  accessGuardsOf,
  childrenNamed,
  requiredLocation,
} from "./gateway-location-support";

const CORS_ORIGIN_SOURCE = "$http_origin";
const CORS_ORIGIN_TARGET = "$allowed_origin";
const ALLOWED_BROWSER_ORIGIN = "http://localhost:3009";
const LOCATION_LEVEL = "http/server/location";
const CATCH_ALL_FALLBACK = 'try_files "" =404;';
const CATCH_ALL_CHILDREN = [["try_files", "", "=404"]];
const PROXY_DIRECTIVE = "proxy_pass";
const TOKEN_STATUS_DIRECTIVE = "js_set";
const NJS_MODULE_IMPORT = "js_import jwt from jwt.js;";
const NJS_MODULE_PATH = "js_path /etc/nginx/njs/;";

const PROXIED_ROUTES = [
  [PUBLIC_USER_LOCATION, "http://$user_service:8000"],
  [ACCOUNT_LOCATION, "http://$account_service:8000"],
  [CONTENT_LOCATION, "http://$content_service:8000"],
  [DOCUMENTS_LOCATION, "http://$documents_service:8000"],
];

function locationSignatures(): readonly string[] {
  return directivesNamed(LOCATION_DIRECTIVE).map(argumentText);
}

function proxyTargetOf(signature: string): string {
  const location = requiredLocation(signature);
  const proxying = childrenNamed(location, PROXY_DIRECTIVE)[0];

  return proxying?.arguments[0] ?? "";
}

describe("gateway rate-limit wiring", () => {
  it("applies no limit against a counter that was never declared", () => {
    const declared = rateLimitZones().map((zone) => zone.zoneName);
    const applications = rateLimitApplications();

    expect(applications.length).toBeGreaterThan(0);

    for (const application of applications) {
      expect(declared).toContain(application.zoneName);
    }
  });

  it("declares no counter that never throttles anything", () => {
    const applied = rateLimitApplications().map((application) => {
      return application.zoneName;
    });
    const zones = rateLimitZones();

    expect(zones.length).toBeGreaterThan(0);

    for (const zone of zones) {
      expect(applied).toContain(zone.zoneName);
    }
  });

  it("builds every counter key from variables the file itself defines", () => {
    const targets = declaredMaps().map((selectorMap) => {
      return selectorMap.targetVariable;
    });
    const zones = rateLimitZones();

    expect(zones.length).toBeGreaterThan(0);

    for (const zone of zones) {
      const selectors = zone.key.split(CLIENT_ADDRESS_KEY).join("");

      if (selectors === "") continue;

      expect(targets).toContain(selectors);
    }
  });

  it("gives the two throttled route groups separate counters", () => {
    const targets = rateLimitSelectorMaps().map((selectorMap) => {
      return selectorMap.targetVariable;
    });

    expect(targets.length).toBe(SELECTOR_MAP_COUNT);
    expect(new Set(targets).size).toBe(targets.length);
  });

  it("names the rejection status once for the whole server", () => {
    const statuses = directivesNamed("limit_req_status");

    expect(statuses.length).toBe(1);
    expect(statuses[0]?.arguments).toEqual(["429"]);
  });
});

describe("gateway routing left intact", () => {
  it("still proxies every route to the service that answers it", () => {
    for (const [signature, target] of PROXIED_ROUTES) {
      expect(locationSignatures()).toContain(signature);
      expect(proxyTargetOf(signature ?? "")).toBe(target);
    }
  });

  it("answers an unrouted path with 404 only after the limits run", () => {
    const catchAll = requiredLocation(CATCH_ALL_LOCATION);
    const answers = catchAll.children.map((child) => {
      return [child.name, ...child.arguments];
    });

    expect(answers).toEqual(CATCH_ALL_CHILDREN);
    expect(gatewayConfigurationText()).toContain(CATCH_ALL_FALLBACK);
  });

  it("runs no njs guard on an unrouted path, not even inherited", () => {
    const catchAll = requiredLocation(CATCH_ALL_LOCATION);
    const accessGuards = directivesNamed(ACCESS_GUARD_DIRECTIVE);
    const inherited = accessGuards.filter((guard) => {
      return guard.level !== LOCATION_LEVEL;
    });

    expect(accessGuardsOf(catchAll)).toEqual([]);
    expect(inherited).toEqual([]);
  });

  it("no longer computes a token status into a variable", () => {
    expect(gatewayConfigurationText()).not.toContain(TOKEN_STATUS_DIRECTIVE);
  });

  it("still imports the njs module under the name jwt", () => {
    expect(gatewayConfigurationText()).toContain(NJS_MODULE_IMPORT);
  });

  it("still looks for the njs module where the image installs it", () => {
    expect(gatewayConfigurationText()).toContain(NJS_MODULE_PATH);
  });

  it("still allows exactly the one browser origin it allowed before", () => {
    const corsMap = declaredMaps().find((selectorMap) => {
      return selectorMap.targetVariable === CORS_ORIGIN_TARGET;
    });

    expect(corsMap?.sourceVariable).toBe(CORS_ORIGIN_SOURCE);
    expect(corsMap?.defaultValue).toBe("");
    expect(corsMap?.entries).toEqual([
      { pattern: ALLOWED_BROWSER_ORIGIN, value: CORS_ORIGIN_SOURCE },
    ]);
  });

  it("still lets a learner upload a body of up to a hundred megabytes", () => {
    const bodySize = directivesNamed("client_max_body_size");

    expect(bodySize.length).toBe(1);
    expect(bodySize[0]?.arguments).toEqual(["100m"]);
  });
});
