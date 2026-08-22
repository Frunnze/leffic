import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import { AccountApi } from "../src/features/settings/account-api";
import { Session } from "../src/shared/api/session";
import type { ThemeChoice } from "../src/shared/ui/theme";
import {
  jsonResponse,
  requestedInit,
  requestedUrl,
  stubFetch,
} from "./support";

const THEME = fc.constantFrom<ThemeChoice>("system", "light", "dark");

beforeEach(() => {
  Session.store("token");
});

afterEach(() => {
  vi.unstubAllGlobals();
  Session.store(null);
});

describe("AccountApi.read", () => {
  it("read property carries the whole account through untouched", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.string(),
        fc.emailAddress(),
        THEME,
        async (username, email, theme) => {
          stubFetch(jsonResponse({ username, email, theme }));

          await expect(AccountApi.read()).resolves.toEqual({
            username,
            email,
            theme,
          });
        },
      ),
    );
  });

  it("falls back to the system theme when the account names none", async () => {
    stubFetch(jsonResponse({ username: "u", email: "e" }));

    await expect(AccountApi.read()).resolves.toMatchObject({ theme: "system" });
  });
});

describe("AccountApi.chooseTheme", () => {
  it("chooseTheme property reads back the theme the account settled on", async () => {
    await fc.assert(
      fc.asyncProperty(THEME, async (theme) => {
        const fetching = stubFetch(jsonResponse({ theme }));

        await expect(AccountApi.chooseTheme(theme)).resolves.toBe(theme);
        expect(requestedInit(fetching).body).toBe(JSON.stringify({ theme }));
      }),
    );
  });

  it("falls back to the system theme when the reply names none", async () => {
    stubFetch(jsonResponse({}));

    await expect(AccountApi.chooseTheme("dark")).resolves.toBe("system");
  });
});

describe("AccountApi.changeUsername", () => {
  it("changeUsername property patches the account with the new name", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string(), async (username) => {
        const fetching = stubFetch(jsonResponse({}));

        await AccountApi.changeUsername(username);

        expect(requestedUrl(fetching)).toContain("/account/username");
        expect(requestedInit(fetching).body).toBe(JSON.stringify({ username }));
      }),
    );
  });
});

describe("AccountApi.changePassword", () => {
  it("changePassword property sends both passwords together", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.string(),
        fc.string(),
        async (currentPassword, newPassword) => {
          const fetching = stubFetch(jsonResponse({}));

          await AccountApi.changePassword(currentPassword, newPassword);

          expect(requestedInit(fetching).body).toBe(
            JSON.stringify({
              current_password: currentPassword,
              new_password: newPassword,
            }),
          );
        },
      ),
    );
  });
});

describe("AccountApi.deleteAccount", () => {
  it("deleteAccount property proves who is asking with a password", async () => {
    await fc.assert(
      fc.asyncProperty(fc.string(), async (password) => {
        const fetching = stubFetch(jsonResponse({}));

        await AccountApi.deleteAccount(password);

        expect(requestedInit(fetching).method).toBe("DELETE");
        expect(requestedInit(fetching).body).toBe(JSON.stringify({ password }));
      }),
    );
  });
});

describe("AccountApi.providerKeys and AccountApi.toProviderKey", () => {
  it("providerKeys property lists every key the account holds", async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer({ min: 0, max: 5 }), async (count) => {
        const provider_keys = Array.from({ length: count }, (_, index) => ({
          provider: `provider-${index}`,
        }));
        stubFetch(jsonResponse({ provider_keys }));

        await expect(AccountApi.providerKeys()).resolves.toHaveLength(count);
      }),
    );
  });

  it("toProviderKey property reads the money already spent", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 0, max: 100_000 }),
        async (spentCents) => {
          stubFetch(
            jsonResponse({
              provider_keys: [{ provider: "openai", spent_cents: spentCents }],
            }),
          );

          await expect(AccountApi.providerKeys()).resolves.toEqual([
            {
              provider: "openai",
              hint: "",
              monthlyLimitCents: null,
              spentCents,
            },
          ]);
        },
      ),
    );
  });

  it("reads a fully described key", async () => {
    stubFetch(
      jsonResponse({
        provider_keys: [
          {
            provider: "openai",
            hint: "sk-…7f",
            monthly_limit_cents: 2000,
            spent_cents: 125,
          },
        ],
      }),
    );

    await expect(AccountApi.providerKeys()).resolves.toEqual([
      {
        provider: "openai",
        hint: "sk-…7f",
        monthlyLimitCents: 2000,
        spentCents: 125,
      },
    ]);
  });
});
