import { For, Show, createEffect, createSignal, onCleanup, type JSX } from "solid-js";
import { Icon } from "./icons/Icon";
import type { IconName } from "./icons/icon-shapes";

export type DropdownItem = {
  readonly label: string;
  readonly icon: IconName;
  readonly hint?: string;
  readonly danger?: boolean;
  readonly onSelect: () => void;
};

export type DropdownProps = {
  readonly isOpen: boolean;
  readonly items: readonly DropdownItem[];
  readonly onDismiss: () => void;
};

class ClickAway {
  static watch(
    element: () => HTMLElement | null,
    isActive: () => boolean,
    onOutside: () => void,
  ): void {
    createEffect(() => {
      if (!isActive()) return;

      const handlePointerDown = (event: MouseEvent): void => {
        const current = element();
        if (current === null) return;
        if (event.target instanceof Node && current.contains(event.target)) return;

        onOutside();
      };

      document.addEventListener("mousedown", handlePointerDown);
      onCleanup(() => document.removeEventListener("mousedown", handlePointerDown));
    });
  }
}

export function Dropdown(props: DropdownProps): JSX.Element {
  const [panel, setPanel] = createSignal<HTMLElement | null>(null);
  ClickAway.watch(panel, () => props.isOpen, () => props.onDismiss());

  return (
    <Show when={props.isOpen}>
      <div class="dropdown" ref={setPanel} role="menu">
        <For each={props.items}>
          {(item) => (
            <button
              class="dropdown-item"
              classList={{ "is-danger": item.danger === true }}
              type="button"
              role="menuitem"
              onClick={() => item.onSelect()}
            >
              <Icon name={item.icon} size="sm" />
              {item.label}
              <Show when={item.hint !== undefined}>
                <span class="dropdown-hint">{item.hint}</span>
              </Show>
            </button>
          )}
        </For>
      </div>
    </Show>
  );
}
