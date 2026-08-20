import { For, Show, createResource, createSignal, type JSX } from "solid-js";
import { useNavigate, useParams } from "@solidjs/router";
import { AppShell } from "../../shared/ui/AppShell";
import { Icon } from "../../shared/ui/icons/Icon";
import { DueSection } from "./DueSection";
import { ImportButton } from "./import/ImportButton";
import { ImportFlow } from "./import/ImportFlow";
import { NewFolderButton } from "./NewFolderButton";
import { StatsApi } from "./stats-api";
import { UnitListSkeleton } from "./UnitListSkeleton";
import { UnitPresentation } from "./unit-presentation";
import { UnitRow } from "./UnitRow";
import { UnitsApi } from "./units-api";
import type { Unit } from "../../shared/models/units";

export default function FolderPage(): JSX.Element {
  const params = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [folder, { mutate: setFolder }] = createResource(
    () => params.id,
    UnitsApi.folderContent,
  );
  const [breakdown, { refetch: refetchBreakdown }] = createResource(
    () => params.id,
    StatsApi.dueBreakdown,
  );
  const [isImportOpen, setImportOpen] = createSignal(false);

  const addUnits = (added: readonly Unit[], targetFolderId: string): void => {
    if (targetFolderId !== params.id) return;

    const current = folder();
    if (current === undefined) return;

    setFolder({
      ...current,
      units: UnitsApi.sortByNewest([...added, ...current.units]),
    });

    void refetchBreakdown();
  };

  const renameUnit = async (unit: Unit, name: string): Promise<void> => {
    const current = folder();
    if (current === undefined) return;

    await UnitsApi.rename(unit.id, unit.type, name);
    setFolder({
      ...current,
      units: current.units.map((entry) =>
        entry.id === unit.id ? { ...entry, name } : entry,
      ),
    });
  };

  const moveUnit = async (unit: Unit, folderId: string): Promise<void> => {
    const current = folder();
    if (current === undefined) return;

    await UnitsApi.move(unit.id, unit.type, folderId);
    setFolder({
      ...current,
      units: current.units.filter((kept) => kept.id !== unit.id),
    });

    void refetchBreakdown();
  };

  const deleteUnit = async (unit: Unit): Promise<void> => {
    const current = folder();
    if (current === undefined) return;

    await UnitsApi.remove(unit.id, unit.type);
    setFolder({
      ...current,
      units: current.units.filter((kept) => kept.id !== unit.id),
    });

    void refetchBreakdown();
  };

  return (
    <AppShell>
      <div class="page">
        <div class="folder">
          <header class="folder-head">
            <div class="folder-title-row">
              <h1 class="folder-name">{folder()?.parentFolderName ?? "Home"}</h1>
              <div class="folder-actions">
                <NewFolderButton
                  folderId={params.id}
                  onFolderCreated={(created) => addUnits(created, params.id)}
                />
                <Show when={(folder()?.units.length ?? 0) > 0}>
                  <ImportButton
                    variant="toolbar"
                    onOpen={() => setImportOpen(true)}
                  />
                </Show>
              </div>
            </div>
          </header>

          <Show when={breakdown()}>
            {(due) => (
              <DueSection
                breakdown={due()}
                onReviewFlashcards={() =>
                  navigate(`/folder/${params.id}/flashcards`)
                }
                onReviewTest={() => navigate(`/folder/${params.id}/test`)}
              />
            )}
          </Show>

          <section aria-labelledby="items-heading">
            <div class="units-head">
              <h2 class="section-label" id="items-heading">
                {UnitPresentation.countLabel(folder()?.units.length ?? 0)}
              </h2>
              <span class="units-note">Newest first</span>
            </div>

            <Show when={folder()} fallback={<UnitListSkeleton />}>
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
                      <ImportButton
                        variant="empty-state"
                        onOpen={() => setImportOpen(true)}
                      />
                    </div>
                  }
                >
                  <div class="units">
                    <For each={loaded().units}>
                      {(unit) => (
                        <UnitRow
                          unit={unit}
                          onDelete={(target) => void deleteUnit(target)}
                          onRename={(target, name) =>
                            void renameUnit(target, name)
                          }
                          onMove={(target, folderId) =>
                            void moveUnit(target, folderId)
                          }
                          destinations={UnitPresentation.moveDestinations(
                            folder()?.units ?? [],
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
        </div>
      </div>


      <ImportFlow
        folderId={params.id}
        folderName={folder()?.parentFolderName ?? "Home"}
        isOpen={isImportOpen()}
        onClose={() => setImportOpen(false)}
        onUnitsAdded={addUnits}
      />
    </AppShell>
  );
}
