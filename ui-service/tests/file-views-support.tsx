import { afterEach, vi } from "vitest";

export const SHAPE = { width: 700, ratio: 0.7, unscaledWidth: 500 };

export function documentOf(numPages: number): never {
  return { numPages } as never;
}

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});
