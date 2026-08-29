import { describe, expect, it } from "vitest";
import {
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

const CORS_ORIGIN_SOURCE = "$http_origin";
const CORS_ORIGIN_TARGET = "$allowed_origin";
const ALLOWED_BROWSER_ORIGIN = "http://localhost:3009";

const PROXIED_ROUTES = [
  ["/api/user/", "http://$user_service:8000"],
  ["/api/user/account", "http://$account_service:8000"],
  ["/api/content/", "http://$content_service:8000"],
  [
    "~ ^/api/content/(upload-files|file|extract-text)$",
    "http://$documents_service:8000",
  ],
];

function locationSignatures(): readonly string[] {
  return directivesNamed("location").map((directive) => {
    return directive.arguments.join(" ");
  });
}

function proxyTargetOf(signature: string): string {
  const location = directivesNamed("location").find((directive) => {
    return directive.arguments.join(" ") === signature;
  });
  const proxying = location?.children.find((child) => {
    return child.name === "proxy_pass";
  });

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

  it("still answers an unrouted path with 404, not a proxy error", () => {
    const catchAll = directivesNamed("location").find((directive) => {
      return directive.arguments.join(" ") === "/";
    });
    const returning = catchAll?.children[0];

    expect(returning?.name).toBe("return");
    expect(returning?.arguments).toEqual(["404"]);
  });

  it("still resolves the token status through the njs module", () => {
    const configuration = gatewayConfigurationText();

    expect(configuration).toContain("js_import jwt from jwt.js;");
    expect(configuration).toContain("js_set $jwt_status jwt.status;");
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
