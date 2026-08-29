import fs from "fs";

export type ConfigDirective = {
  readonly name: string;
  readonly arguments: readonly string[];
  readonly level: string;
  readonly children: readonly ConfigDirective[];
};

export type RateLimitZone = {
  readonly key: string;
  readonly zoneName: string;
  readonly rateText: string;
  readonly ratePerSecond: number;
  readonly level: string;
};

export type RateLimitApplication = {
  readonly zoneName: string;
  readonly burst: number | null;
  readonly hasNoDelay: boolean;
  readonly level: string;
};

const CONFIGURATION_PATH = "nginx.conf";
const NJS_MODULE_PATH = "src/jwt.ts";

const SECONDS_PER_MINUTE = 60;

export function gatewayConfigurationText(): string {
  return fs.readFileSync(CONFIGURATION_PATH, "utf8");
}

export function njsModuleText(): string {
  return fs.readFileSync(NJS_MODULE_PATH, "utf8");
}

export function unquote(token: string): string {
  const quoted = /^"(.*)"$/.exec(token);

  if (quoted === null) return token;

  return quoted[1] ?? "";
}

function tokenize(text: string): readonly string[] {
  return text.match(/"[^"]*"|[^\s;{}]+|[;{}]/g) ?? [];
}

type ParsedBlock = {
  readonly directives: readonly ConfigDirective[];
  readonly nextIndex: number;
};

type NestedBlock = {
  readonly directive: ConfigDirective;
  readonly nextIndex: number;
};

function build(
  words: readonly string[],
  level: string,
  children: readonly ConfigDirective[],
): ConfigDirective {
  return {
    name: words[0] ?? "",
    arguments: words.slice(1).map(unquote),
    level,
    children,
  };
}

function consumeNestedBlock(
  tokens: readonly string[],
  startIndex: number,
  level: string,
  words: readonly string[],
): NestedBlock {
  const nestedLevel = level === "" ? words[0] ?? "" : `${level}/${words[0]}`;
  const inner = parseBlock(tokens, startIndex, nestedLevel);

  return {
    directive: build(words, level, inner.directives),
    nextIndex: inner.nextIndex,
  };
}

function parseBlock(
  tokens: readonly string[],
  startIndex: number,
  level: string,
): ParsedBlock {
  const directives: ConfigDirective[] = [];
  let words: string[] = [];
  let index = startIndex;

  while (index < tokens.length) {
    const token = tokens[index] ?? "";
    index += 1;

    if (token === "}") break;

    if (token === ";") {
      directives.push(build(words, level, []));
      words = [];
    } else if (token === "{") {
      const nested = consumeNestedBlock(tokens, index, level, words);

      directives.push(nested.directive);
      words = [];
      index = nested.nextIndex;
    } else {
      words.push(token);
    }
  }

  return { directives, nextIndex: index };
}

function flattenDirectives(
  directives: readonly ConfigDirective[],
  into: ConfigDirective[],
): void {
  for (const directive of directives) {
    into.push(directive);
    flattenDirectives(directive.children, into);
  }
}

function gatewayDirectives(): readonly ConfigDirective[] {
  const parsed = parseBlock(tokenize(gatewayConfigurationText()), 0, "");
  const flattened: ConfigDirective[] = [];

  flattenDirectives(parsed.directives, flattened);

  return flattened;
}

export function directivesNamed(name: string): readonly ConfigDirective[] {
  return gatewayDirectives().filter((directive) => directive.name === name);
}

function argumentValue(
  directive: ConfigDirective,
  prefix: string,
): string | null {
  for (const argument of directive.arguments) {
    if (argument.indexOf(prefix) === 0) return argument.slice(prefix.length);
  }

  return null;
}

function ratePerSecond(rateText: string): number {
  const parsed = /^([0-9]+)r\/(s|m)$/.exec(rateText);

  if (parsed === null) return Number.NaN;

  const amount = Number(parsed[1]);

  if (parsed[2] === "s") return amount;

  return amount / SECONDS_PER_MINUTE;
}

export function rateLimitZones(): readonly RateLimitZone[] {
  return directivesNamed("limit_req_zone").map((directive) => {
    const zoneSetting = argumentValue(directive, "zone=") ?? "";
    const rateText = argumentValue(directive, "rate=") ?? "";

    return {
      key: directive.arguments[0] ?? "",
      zoneName: zoneSetting.split(":")[0] ?? "",
      rateText,
      ratePerSecond: ratePerSecond(rateText),
      level: directive.level,
    };
  });
}

export function rateLimitApplications(): readonly RateLimitApplication[] {
  return directivesNamed("limit_req").map((directive) => {
    const burstText = argumentValue(directive, "burst=");

    return {
      zoneName: argumentValue(directive, "zone=") ?? "",
      burst: burstText === null ? null : Number(burstText),
      hasNoDelay: directive.arguments.indexOf("nodelay") !== -1,
      level: directive.level,
    };
  });
}
