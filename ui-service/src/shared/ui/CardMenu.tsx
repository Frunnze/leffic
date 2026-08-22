import { createSignal, type JSX } from "solid-js";
import { Dropdown, type DropdownItem } from "./Dropdown";
import { Icon } from "./icons/Icon";

type CardMenuProps = {
  readonly label: string;
  readonly items: readonly DropdownItem[];
};

export function CardMenu(props: CardMenuProps): JSX.Element {
  const [isOpen, setOpen] = createSignal(false);

  const itemsThatCloseTheMenu = (): readonly DropdownItem[] =>
    props.items.map((item) => ({
      ...item,
      onSelect: () => {
        setOpen(false);
        item.onSelect();
      },
    }));

  return (
    <>
      <button
        class="btn btn-quiet btn-icon"
        type="button"
        aria-label={props.label}
        aria-expanded={isOpen()}
        onClick={() => setOpen(!isOpen())}
      >
        <Icon name="dots" size="sm" />
      </button>
      <Dropdown
        isOpen={isOpen()}
        onDismiss={() => setOpen(false)}
        items={itemsThatCloseTheMenu()}
      />
    </>
  );
}
