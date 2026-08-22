import { afterEach, vi } from "vitest";
import { fireEvent, screen } from "@solidjs/testing-library";

export const STRONG_PASSWORD = "correct horse";

export function typeInto(label: string, value: string): void {
  fireEvent.input(screen.getByLabelText(label), { target: { value } });
}

afterEach(() => {
  vi.restoreAllMocks();
});
