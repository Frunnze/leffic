import { vi } from "vitest";
import { type DropdownItem } from "../src/shared/ui/Dropdown";

export function itemNamed(label: string, onSelect = vi.fn()): DropdownItem {
  return { label, icon: "note", onSelect };
}
