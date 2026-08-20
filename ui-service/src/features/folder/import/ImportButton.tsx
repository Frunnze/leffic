import type { JSX } from "solid-js";
import { Icon } from "../../../shared/ui/icons/Icon";

export type ImportButtonProps = {
  readonly variant: "toolbar" | "empty-state";
  readonly onOpen: () => void;
};

export function ImportButton(props: ImportButtonProps): JSX.Element {
  return (
    <div class="folder-action">
      <button
        class={props.variant === "toolbar" ? "btn" : "btn btn-primary btn-lg"}
        type="button"
        onClick={props.onOpen}
      >
        <Icon name="aiImport" size="sm" />
        Import
      </button>
    </div>
  );
}
