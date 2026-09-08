const PERCENT_SIGN = "%";
const PERCENT_ESCAPE_PATTERN = /%[0-9a-fA-F]{2}/g;
const ESCAPE_DIGITS_PATTERN = /^[0-9a-fA-F]{2}/;
const ENCODED_NULL_BYTE_PATTERN = /%00/;

const PATH_SEPARATOR = "/";
const QUERY_SEPARATOR = "?";
const FRAGMENT_SEPARATOR = "#";
const CURRENT_DIRECTORY_SEGMENT = ".";
const PARENT_DIRECTORY_SEGMENT = "..";
const EMPTY_SEGMENT = "";
const SEPARATOR_NOT_PRESENT = -1;

export const HEXADECIMAL_BASE = 16;

type WalkedPath = {
  readonly segments: readonly string[];
  readonly endedAtDirectory: boolean;
};

function pathPortionOf(requestUri: string): string {
  const separatorPositions = [QUERY_SEPARATOR, FRAGMENT_SEPARATOR]
    .map((separator) => requestUri.indexOf(separator))
    .filter((position) => position !== SEPARATOR_NOT_PRESENT);

  if (separatorPositions.length === 0) return requestUri;

  return requestUri.slice(0, Math.min(...separatorPositions));
}

function rejectMalformedEscapes(rawPath: string): void {
  const textsFollowingPercentSigns = rawPath.split(PERCENT_SIGN).slice(1);

  for (const textFollowingPercentSign of textsFollowingPercentSigns) {
    if (!ESCAPE_DIGITS_PATTERN.test(textFollowingPercentSign)) {
      throw new Error(`malformed percent-escape in "${rawPath}"`);
    }
  }
}

function rejectEncodedNullByte(rawPath: string): void {
  if (ENCODED_NULL_BYTE_PATTERN.test(rawPath)) {
    throw new Error(`encoded null byte in "${rawPath}"`);
  }
}

function characterEscapedBy(escape: string): string {
  return String.fromCharCode(parseInt(escape.slice(1), HEXADECIMAL_BASE));
}

function decodedPath(rawPath: string): string {
  rejectMalformedEscapes(rawPath);
  rejectEncodedNullByte(rawPath);

  return rawPath.replace(PERCENT_ESCAPE_PATTERN, characterEscapedBy);
}

function walkedPath(decodedPathText: string): WalkedPath {
  const segments: string[] = [];
  let endedAtDirectory = true;

  for (const segment of decodedPathText.split(PATH_SEPARATOR)) {
    endedAtDirectory = true;

    if (segment === EMPTY_SEGMENT) continue;

    if (segment === CURRENT_DIRECTORY_SEGMENT) continue;

    if (segment === PARENT_DIRECTORY_SEGMENT) {
      if (segments.length === 0) {
        throw new Error(`path climbs above the root in "${decodedPathText}"`);
      }

      segments.pop();
      continue;
    }

    segments.push(segment);
    endedAtDirectory = false;
  }

  return { segments, endedAtDirectory };
}

export function normalisedRequestPath(requestUri: string): string {
  const walked = walkedPath(decodedPath(pathPortionOf(requestUri)));

  if (walked.segments.length === 0) return PATH_SEPARATOR;

  const trailingSeparator = walked.endedAtDirectory
    ? PATH_SEPARATOR
    : EMPTY_SEGMENT;

  return PATH_SEPARATOR
    + walked.segments.join(PATH_SEPARATOR)
    + trailingSeparator;
}

export function isClassifiablePath(requestUri: string): boolean {
  try {
    normalisedRequestPath(requestUri);
  } catch {
    return false;
  }

  return true;
}
