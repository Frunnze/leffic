import {
  ConfigDirective,
  directivesNamed,
  rateLimitZones,
  unquote,
} from "./nginx-config-support";

type SelectorEntry = {
  readonly pattern: string;
  readonly value: string;
};

export type SelectorMap = {
  readonly sourceVariable: string;
  readonly targetVariable: string;
  readonly defaultValue: string;
  readonly entries: readonly SelectorEntry[];
};

function toSelectorMap(directive: ConfigDirective): SelectorMap {
  const entries: SelectorEntry[] = [];
  let defaultValue = "";

  for (const child of directive.children) {
    if (child.name === "default") {
      defaultValue = child.arguments[0] ?? "";
    } else {
      entries.push({
        pattern: unquote(child.name),
        value: child.arguments[0] ?? "",
      });
    }
  }

  return {
    sourceVariable: directive.arguments[0] ?? "",
    targetVariable: directive.arguments[1] ?? "",
    defaultValue,
    entries,
  };
}

export function declaredMaps(): readonly SelectorMap[] {
  return directivesNamed("map").map(toSelectorMap);
}

export function rateLimitSelectorMaps(): readonly SelectorMap[] {
  const keys = rateLimitZones().map((zone) => zone.key);

  return declaredMaps().filter((selectorMap) => {
    return keys.some((key) => key.indexOf(selectorMap.targetVariable) !== -1);
  });
}

export function selectorMapFeeding(zoneName: string): SelectorMap | null {
  const zone = rateLimitZones().find((candidate) => {
    return candidate.zoneName.toLowerCase().indexOf(zoneName) !== -1;
  });

  if (zone === undefined) return null;

  const feeding = rateLimitSelectorMaps().filter((selectorMap) => {
    return zone.key.indexOf(selectorMap.targetVariable) !== -1;
  });

  return feeding[0] ?? null;
}

function patternMatches(pattern: string, requestUri: string): boolean {
  if (pattern.indexOf("~") === 0) {
    return new RegExp(pattern.slice(1)).test(requestUri);
  }

  return pattern === requestUri;
}

export function mappedValueFor(
  selectorMap: SelectorMap,
  requestUri: string,
): string {
  const exact = selectorMap.entries.find((entry) => {
    return entry.pattern.indexOf("~") !== 0 && entry.pattern === requestUri;
  });

  if (exact !== undefined) return exact.value;

  const matched = selectorMap.entries.find((entry) => {
    return entry.pattern.indexOf("~") === 0
      && patternMatches(entry.pattern, requestUri);
  });

  if (matched !== undefined) return matched.value;

  return selectorMap.defaultValue;
}
