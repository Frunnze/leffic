import fc from "fast-check";
import { ICONS, type IconName } from "../src/shared/ui/icons/icon-shapes";

export const ICON_NAME = fc.constantFrom(...(Object.keys(ICONS) as IconName[]));
export const LABEL = fc.stringMatching(/^[A-Za-z][A-Za-z0-9]{0,9}$/);

export function meterWidth(): number {
  const filled = document.querySelector(".meter-fill") as HTMLElement;

  return Number.parseFloat(filled.getAttribute("style")?.split(":")[1] ?? "");
}
