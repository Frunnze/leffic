import { beforeEach, describe, expect, it, vi } from "vitest";
import fc from "fast-check";
import { Theme, type ThemeChoice } from "../src/shared/ui/theme";

const CHOICE = fc.constantFrom<ThemeChoice>("system", "light", "dark");

async function reimportedTheme(): Promise<typeof Theme> {
  vi.resetModules();
  const reloaded = await import("../src/shared/ui/theme");

  return reloaded.Theme;
}

beforeEach(() => {
  localStorage.clear();
  delete document.documentElement.dataset.theme;
});

describe("Theme.apply and Theme.lastPainted", () => {
  it("apply property is read back by lastPainted", () => {
    fc.assert(
      fc.property(CHOICE, (choice) => {
        Theme.apply(choice);

        expect(Theme.lastPainted()).toBe(choice);
      }),
    );
  });

  it("apply property paints an explicit choice onto the document", () => {
    fc.assert(
      fc.property(fc.constantFrom<ThemeChoice>("light", "dark"), (choice) => {
        Theme.apply(choice);

        expect(document.documentElement.dataset.theme).toBe(choice);
      }),
    );
  });

  it("takes the painted theme off the document for the system choice", () => {
    Theme.apply("dark");
    Theme.apply("system");

    expect(document.documentElement.dataset.theme).toBeUndefined();
  });

  it("falls back to the system theme when nothing was painted", () => {
    expect(Theme.lastPainted()).toBe("system");
  });

  it("falls back to the system theme when the stored name is unknown", () => {
    localStorage.setItem("leffic-theme", "neon");

    expect(Theme.lastPainted()).toBe("system");
  });
});

describe("Theme.asChoice", () => {
  it("asChoice property keeps a name the app knows", () => {
    fc.assert(
      fc.property(fc.constantFrom("light", "dark"), (value) => {
        expect(Theme.asChoice(value)).toBe(value);
      }),
    );
  });

  it("asChoice property reads anything else as the system theme", () => {
    fc.assert(
      fc.property(
        fc.oneof(fc.integer(), fc.constant(null), fc.string()),
        (value) => {
          const choice = Theme.asChoice(value);

          expect(["system", "light", "dark"]).toContain(choice);
        },
      ),
    );
  });
});

describe("Theme.followAccount", () => {
  it("followAccount property paints whatever the account holds", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom<ThemeChoice>("light", "dark"),
        async (choice) => {
          const freshTheme = await reimportedTheme();

          freshTheme.followAccount(() => Promise.resolve(choice));

          await vi.waitFor(() =>
            expect(document.documentElement.dataset.theme).toBe(choice),
          );
        },
      ),
      { numRuns: 2 },
    );
  });

  it("reads the account only once however often it is asked", async () => {
    const freshTheme = await reimportedTheme();
    const read = vi.fn().mockResolvedValue("dark" as ThemeChoice);

    freshTheme.followAccount(read);
    freshTheme.followAccount(read);

    await vi.waitFor(() => expect(read).toHaveBeenCalledTimes(1));
  });
});

describe("Theme.lastPainted", () => {
  it("lastPainted property remembers the last explicit choice", () => {
    fc.assert(
      fc.property(fc.constantFrom<ThemeChoice>("light", "dark"), (choice) => {
        Theme.apply(choice);

        expect(Theme.lastPainted()).toBe(choice);
      }),
    );
  });

  it("lastPainted property reads anything unknown as the system theme", () => {
    fc.assert(
      fc.property(
        fc.string().filter((name) => name !== "light" && name !== "dark"),
        (name) => {
          localStorage.setItem("leffic-theme", name);

          expect(Theme.lastPainted()).toBe("system");
        },
      ),
    );
  });
});
