import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import { AccountApi } from "../src/features/settings/account-api";
import { Session } from "../src/shared/api/session";
import {
  jsonResponse,
  requestedInit,
  requestedUrl,
  stubFetch,
} from "./support";

beforeEach(() => {
  Session.store("token");
});

afterEach(() => {
  vi.unstubAllGlobals();
  Session.store(null);
});

describe("AccountApi.saveProviderKey", () => {
  it("saveProviderKey property sends the key and its limit together", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.string({ minLength: 1 }),
        fc.option(fc.integer({ min: 0, max: 9999 }), { nil: null }),
        async (key, monthlyLimitCents) => {
          const fetching = stubFetch(jsonResponse({}));

          await AccountApi.saveProviderKey({
            provider: "openai",
            key,
            password: "secret",
            monthlyLimitCents,
          });

          expect(requestedInit(fetching).method).toBe("PUT");
          expect(requestedInit(fetching).body).toBe(
            JSON.stringify({
              provider: "openai",
              key,
              password: "secret",
              monthly_limit_cents: monthlyLimitCents,
            }),
          );
        },
      ),
    );
  });
});

describe("AccountApi.removeProviderKey", () => {
  it("removeProviderKey property deletes exactly the provider it names", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom("openai", "anthropic"),
        async (provider) => {
          const fetching = stubFetch(jsonResponse({}));

          await AccountApi.removeProviderKey(provider);

          expect(requestedUrl(fetching)).toContain(
            `/provider-keys/${provider}`,
          );
          expect(requestedInit(fetching).method).toBe("DELETE");
        },
      ),
    );
  });
});
