import {
  RateLimitApplication,
  RateLimitZone,
  rateLimitApplications,
  rateLimitZones,
} from "./nginx-config-support";
import {
  SelectorMap,
  declaredMaps,
  mappedValueFor,
  selectorMapFeeding,
} from "./nginx-selector-support";

export const AUTHENTICATION_ZONE_WORD = "auth";
export const GENERATION_COST_ZONE_WORD = "cost";
export const GENERAL_ZONE_WORD = "general";

export const CLIENT_ADDRESS_KEY = "$binary_remote_addr";
export const SELECTOR_MAP_COUNT = 2;

export const CLIENT_ADDRESS_BYTES = "\x7f\x00\x00\x01";

export const AUTHENTICATION_LIMITED_ROUTES: readonly string[] = [
  "/api/user/login",
  "/api/user/sign-up",
];

export const AUTHENTICATION_UNLIMITED_ROUTES: readonly string[] = [
  "/api/user/refresh-token",
  "/api/user/logout",
];

export const GENERATION_COST_LIMITED_ROUTES: readonly string[] = [
  "/api/content/chat",
  "/api/content/generate-study-units",
  "/api/content/extract-text",
  "/api/content/upload-files",
];

export const UNCOUNTED_ROUTES: readonly string[] = [
  "/api/user/account",
  "/api/content/folders",
  "/api/content/file",
  "/api/content/flashcards",
  "/healthz",
  "/",
];

export function requiredZone(word: string): RateLimitZone {
  const matching = rateLimitZones().filter((zone) => {
    return zone.zoneName.toLowerCase().indexOf(word) !== -1;
  });
  const zone = matching[0];

  if (zone === undefined) {
    throw new Error(`no limit_req_zone whose name contains "${word}"`);
  }

  return zone;
}

export function requiredApplication(word: string): RateLimitApplication {
  const matching = rateLimitApplications().filter((application) => {
    return application.zoneName.toLowerCase().indexOf(word) !== -1;
  });
  const application = matching[0];

  if (application === undefined) {
    throw new Error(`no limit_req naming a zone that contains "${word}"`);
  }

  return application;
}

export function selectorOf(zoneWord: string): SelectorMap {
  const selectorMap = selectorMapFeeding(zoneWord);

  if (selectorMap === null) {
    throw new Error(`no selector map feeds the "${zoneWord}" zone key`);
  }

  return selectorMap;
}

export function evaluatedKey(zoneWord: string, requestUri: string): string {
  let key = requiredZone(zoneWord).key;

  for (const selectorMap of declaredMaps()) {
    const mapped = mappedValueFor(selectorMap, requestUri);

    key = key.split(selectorMap.targetVariable).join(mapped);
  }

  return key.split(CLIENT_ADDRESS_KEY).join(CLIENT_ADDRESS_BYTES);
}
