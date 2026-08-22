import { vi } from "vitest";

type ObserverCallback = (
  entries: readonly Partial<IntersectionObserverEntry>[],
) => void;

type FakeObservers = {
  readonly intersections: ObserverCallback[];
  readonly resizes: (() => void)[];
  readonly disconnects: ReturnType<typeof vi.fn>;
  readonly observed: Element[];
};

export function stubObservers(): FakeObservers {
  const intersections: ObserverCallback[] = [];
  const resizes: (() => void)[] = [];
  const disconnects = vi.fn();
  const observed: Element[] = [];

  class FakeIntersectionObserver {
    constructor(callback: ObserverCallback) {
      intersections.push(callback);
    }

    observe(element: Element): void {
      observed.push(element);
    }

    disconnect(): void {
      disconnects();
    }
  }

  class FakeResizeObserver {
    constructor(callback: () => void) {
      resizes.push(callback);
    }

    observe(element: Element): void {
      observed.push(element);
    }

    disconnect(): void {
      disconnects();
    }
  }

  vi.stubGlobal("IntersectionObserver", FakeIntersectionObserver);
  vi.stubGlobal("ResizeObserver", FakeResizeObserver);

  return { intersections, resizes, disconnects, observed };
}

export function entryFor(
  page: number,
  isIntersecting: boolean,
): Partial<IntersectionObserverEntry> {
  const target = document.createElement("div");
  target.setAttribute("data-page", String(page));

  return { target, isIntersecting };
}
