import { Show, createSignal, type JSX } from "solid-js";
import { A } from "@solidjs/router";
import { Dropdown } from "../../shared/ui/Dropdown";
import { Icon } from "../../shared/ui/icons/Icon";
import { MoveUnitDialog, type MoveDestination } from "./MoveUnitDialog";
import { PromptDialog } from "../../shared/ui/PromptDialog";
import { UnitPresentation } from "./unit-presentation";
import type { Unit } from "./unit-models";

type UnitRowProps = {
  readonly unit: Unit;
  readonly onDelete: (unit: Unit) => void;
  readonly onRename: (unit: Unit, name: string) => void;
  readonly onMove: (unit: Unit, folderId: string) => void;
  readonly destinations: readonly MoveDestination[];
};

export function UnitRow(props: UnitRowProps): JSX.Element {
  const [isMenuOpen, setMenuOpen] = createSignal(false);
  const [isRenaming, setRenaming] = createSignal(false);
  const [isMoving, setMoving] = createSignal(false);

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
        items={[
          {
            label: "Move to folder",
            icon: "folder",
            onSelect: () => {
              setMenuOpen(false);
              setMoving(true);
            },
          },
          {
            label: "Rename",
            icon: "note",
            onSelect: () => {
              setMenuOpen(false);
              setRenaming(true);
            },
          },
          { label: "Delete", icon: "trash", danger: true, onSelect: remove },
        ]}
      />

      <Show when={isMoving()}>
        <MoveUnitDialog
          unit={props.unit}
          destinations={props.destinations}
          onConfirm={(folderId) => {
            setMoving(false);
            props.onMove(props.unit, folderId);
          }}
          onCancel={() => setMoving(false)}
        />
      </Show>

      <Show when={isRenaming()}>
        <PromptDialog
          title="Rename"
          description="Pick a name you will recognise later."
          label="Name"
          placeholder={props.unit.name}
          inputType="text"
          confirmLabel="Save name"
          onConfirm={(name) => {
            setRenaming(false);
            props.onRename(props.unit, name);
          }}
          onCancel={() => setRenaming(false)}
        />
      </Show>
    </div>
  );
}
