import { Show, createSignal, type JSX } from "solid-js";
import { A } from "@solidjs/router";
import { Dropdown } from "../../shared/ui/Dropdown";
import { Icon } from "../../shared/ui/icons/Icon";
import { UnitPresentation } from "./unit-presentation";
import type { Unit } from "../../shared/models/units";

export type UnitRowProps = {
  readonly unit: Unit;
  readonly onDelete: (unit: Unit) => void;
};

export function UnitRow(props: UnitRowProps): JSX.Element {
  const [isMenuOpen, setMenuOpen] = createSignal(false);

  const remove = (): void => {
    setMenuOpen(false);
    props.onDelete(props.unit);
  };

  return (
    <div class="unit">
      <A class="unit-link" href={UnitPresentation.href(props.unit)}>
        <Icon name={UnitPresentation.icon(props.unit)} />
        <span class="unit-body">
          <span class="unit-name">{props.unit.name}</span>
          <Show when={UnitPresentation.meta(props.unit)}>
            {(meta) => <span class="unit-meta">{meta()}</span>}
          </Show>
        </span>
        <Show when={UnitPresentation.badge(props.unit)}>
          {(badge) => <span class="unit-badge">{badge()}</span>}
        </Show>
      </A>

      <button
        class="btn btn-quiet btn-icon unit-menu"
        type="button"
        aria-label={`More actions for ${props.unit.name}`}
        aria-expanded={isMenuOpen()}
        onClick={() => setMenuOpen(!isMenuOpen())}
      >
        <Icon name="dots" size="sm" />
      </button>

      <Dropdown
        isOpen={isMenuOpen()}
        onDismiss={() => setMenuOpen(false)}
        items={[{ label: "Delete", icon: "trash", danger: true, onSelect: remove }]}
      />
    </div>
  );
}
