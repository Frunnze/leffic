import {
  ConfigDirective,
  argumentText,
  directivesNamed,
} from "./nginx-config-support";

export const LOCATION_DIRECTIVE = "location";
export const ACCESS_GUARD_DIRECTIVE = "js_access";

export const PUBLIC_USER_LOCATION = "/api/user/";
export const ACCOUNT_LOCATION = "/api/user/account";
export const CONTENT_LOCATION = "/api/content/";
export const DOCUMENTS_LOCATION =
  "~ ^/api/content/(upload-files|file|extract-text)$";
export const CATCH_ALL_LOCATION = "/";

export const PROTECTED_LOCATIONS: readonly string[] = [
  ACCOUNT_LOCATION,
  CONTENT_LOCATION,
  DOCUMENTS_LOCATION,
];

export const PROXIED_LOCATIONS: readonly string[] = [
  PUBLIC_USER_LOCATION,
  ...PROTECTED_LOCATIONS,
];

export function requiredLocation(signature: string): ConfigDirective {
  const location = directivesNamed(LOCATION_DIRECTIVE).find((candidate) => {
    return argumentText(candidate) === signature;
  });

  if (location === undefined) {
    throw new Error(`no location block "${signature}"`);
  }

  return location;
}

export function childrenNamed(
  location: ConfigDirective,
  name: string,
): readonly ConfigDirective[] {
  return location.children.filter((child) => child.name === name);
}

export function accessGuardsOf(location: ConfigDirective): readonly string[] {
  return childrenNamed(location, ACCESS_GUARD_DIRECTIVE).map(argumentText);
}
