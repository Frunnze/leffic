import { For, Show, type JSX } from "solid-js";
import { Icon } from "../../shared/ui/icons/Icon";
import { ImportButton } from "./import/ImportButton";
import { UnitListSkeleton } from "./UnitListSkeleton";
import { UnitPresentation } from "./unit-presentation";
import { UnitRow } from "./UnitRow";
import type { FolderContent, Unit } from "./unit-models";

type UnitsSectionProps = {
  readonly content: FolderContent | undefined;
  readonly onImport: () => void;
  readonly onDelete: (content: FolderContent, unit: Unit) => void;
  readonly onRename: (
    content: FolderContent,
    unit: Unit,
    name: string,
  ) => void;
  readonly onMove: (
    content: FolderContent,
    unit: Unit,
    folderId: string,
  ) => void;
};

export function UnitsSection(props: UnitsSectionProps): JSX.Element {
  return (
    <section aria-labelledby="items-heading">
      <div class="units-head">
        <h2 class="section-label" id="items-heading">
          {UnitPresentation.countLabel(props.content?.units.length ?? 0)}
        </h2>
        <span class="units-note">Newest first</span>
      </div>

      <Show when={props.content} fallback={<UnitListSkeleton />}>
        {(loaded) => (
          <Show
            when={loaded().units.length > 0}
            fallback={
              <div class="state">
                <Icon name="folderOpen" />
                <span class="state-title">Nothing here yet</span>
                <span class="state-text">
                  Import a file, a link or a topic and Leffic will generate
                  flashcards, a note and a test from it.
                </span>
                <ImportButton variant="empty-state" onOpen={props.onImport} />
              </div>
            }
          >
            <div class="units">
              <For each={loaded().units}>
                {(unit) => (
                  <UnitRow
                    unit={unit}
                    onDelete={(target) => {
                      props.onDelete(loaded(), target);
                    }}
                    onRename={(target, name) => {
                      props.onRename(loaded(), target, name);
                    }}
                    onMove={(target, folderId) => {
                      props.onMove(loaded(), target, folderId);
                    }}
                    destinations={UnitPresentation.moveDestinations(
                      loaded().units,
                      unit,
                    )}
                  />
                )}
              </For>
            </div>
          </Show>
        )}
      </Show>
    </section>
  );
}
