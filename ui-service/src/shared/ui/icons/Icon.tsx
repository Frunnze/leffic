import type { JSX } from "solid-js";
import { ICONS, type IconName } from "./icon-shapes";

export type IconSize = "sm" | "md" | "lg";

const SIZE_CLASS: Readonly<Record<IconSize, string>> = {
  sm: "icon-sm",
  md: "icon",
  lg: "icon-lg",
};

export type IconProps = {
  readonly name: IconName;
  readonly size?: IconSize;
  readonly title?: string;
};

export function Icon(props: IconProps): JSX.Element {
  const shape = (): (typeof ICONS)[IconName] => ICONS[props.name];

  return (
    <svg
      class={SIZE_CLASS[props.size ?? "md"]}
      viewBox={shape().viewBox}
      role={props.title === undefined ? "presentation" : "img"}
      aria-hidden={props.title === undefined}
      aria-label={props.title}
      innerHTML={shape().body}
    />
  );
}
