import { describe, expect, it } from "vitest";
import {
  gatewayConfigurationText,
  rateLimitZones,
} from "./nginx-config-support";
import { selectorMapFeeding } from "./nginx-selector-support";
import {
  AUTHENTICATION_ZONE_WORD,
  CLIENT_ADDRESS_BYTES,
  CLIENT_ADDRESS_KEY,
  GENERAL_ZONE_WORD,
  GENERATION_COST_ZONE_WORD,
  evaluatedKey,
  requiredApplication,
  requiredZone,
} from "./rate-limit-support";

const GENERATION_WATCHER_CEILING_PER_SECOND = 4;
const GENERATION_WATCHER_POLL = "/api/content/flashcards-status/7";
const SELECTOR_FED_ZONE_WORDS = [
  AUTHENTICATION_ZONE_WORD,
  GENERATION_COST_ZONE_WORD,
];

describe("gateway rate-limit zones", () => {
  it("admits ten sign-in attempts a minute from one client", () => {
    expect(requiredZone(AUTHENTICATION_ZONE_WORD).rateText).toBe("10r/m");
  });

  it("admits thirty paid-generation requests a minute from one client", () => {
    expect(requiredZone(GENERATION_COST_ZONE_WORD).rateText).toBe("30r/m");
  });

  it("admits twenty ordinary requests a second from one client", () => {
    expect(requiredZone(GENERAL_ZONE_WORD).rateText).toBe("20r/s");
  });

  it("never throttles the four-per-second generation-watcher poll", () => {
    const general = requiredZone(GENERAL_ZONE_WORD);

    expect(general.ratePerSecond).toBeGreaterThanOrEqual(
      GENERATION_WATCHER_CEILING_PER_SECOND,
    );

    for (const zoneWord of SELECTOR_FED_ZONE_WORDS) {
      expect(evaluatedKey(zoneWord, GENERATION_WATCHER_POLL)).toBe("");
    }
  });

  it("counts a throttled request against the caller's address alone", () => {
    const listedRoutes = {
      [AUTHENTICATION_ZONE_WORD]: "/api/user/login",
      [GENERATION_COST_ZONE_WORD]: "/api/content/chat",
      [GENERAL_ZONE_WORD]: GENERATION_WATCHER_POLL,
    };

    expect(rateLimitZones().length).toBe(Object.keys(listedRoutes).length);

    for (const [zoneWord, route] of Object.entries(listedRoutes)) {
      expect(evaluatedKey(zoneWord, route)).toBe(CLIENT_ADDRESS_BYTES);
    }
  });

  it("lets five sign-in attempts burst through without delay", () => {
    const application = requiredApplication(AUTHENTICATION_ZONE_WORD);

    expect(application.burst).toBe(5);
    expect(application.hasNoDelay).toBe(true);
  });

  it("lets ten paid-generation requests burst through without delay", () => {
    const application = requiredApplication(GENERATION_COST_ZONE_WORD);

    expect(application.burst).toBe(10);
    expect(application.hasNoDelay).toBe(true);
  });

  it("lets forty ordinary requests burst through without delay", () => {
    const application = requiredApplication(GENERAL_ZONE_WORD);

    expect(application.burst).toBe(40);
    expect(application.hasNoDelay).toBe(true);
  });

  it("rejects a throttled request with 429 rather than 503", () => {
    expect(gatewayConfigurationText()).toContain("limit_req_status 429;");
  });

  it("counts every route towards the general zone, not a chosen few", () => {
    expect(requiredZone(GENERAL_ZONE_WORD).key).toBe(CLIENT_ADDRESS_KEY);
    expect(selectorMapFeeding(GENERAL_ZONE_WORD)).toBeNull();
  });
});
