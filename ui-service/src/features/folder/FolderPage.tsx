import {
  Show,
  createEffect,
  createResource,
  createSignal,
  on,
  type JSX,
} from "solid-js";
import { useNavigate, useParams } from "@solidjs/router";
import { AppShell } from "../../shared/ui/AppShell";
import { DueSection } from "./DueSection";
import { ImportButton } from "./import/ImportButton";
import { ImportFlow } from "./import/ImportFlow";
import { useGenerations } from "./import/GenerationContext";
import { NewFolderButton } from "./NewFolderButton";
import { StatsApi } from "./stats-api";
import { UnitsSection } from "./UnitsSection";
import { UnitsApi } from "./units-api";
import type { FolderContent, Unit } from "./unit-models";

export default function FolderPage(): JSX.Element {
  const params = useParams<{ id: string }>();
  const navigate = useNavigate();
  const generations = useGenerations();
  const [folder, { mutate: setFolder, refetch: refetchFolder }] =
    createResource(() => params.id, UnitsApi.folderContent);
  const [breakdown, { refetch: refetchBreakdown }] = createResource(
    () => params.id,
    StatsApi.dueBreakdown,
  );
  const [isImportOpen, setImportOpen] = createSignal(false);

  const folderName = (): string => folder()?.parentFolderName ?? "Home";

  createEffect(
    on(
      () => generations.completionsIn(params.id),
      () => {
        void refetchFolder();
        void refetchBreakdown();
      },
      { defer: true },
    ),
  );

  const addUnits = (added: readonly Unit[], targetFolderId: string): void => {
    if (targetFolderId !== params.id) return;

    const current = folder();
    if (current === undefined) return;

    const byId = new Map<string, Unit>(
      current.units.map((listed) => [listed.id, listed]),
    );

    for (const unit of added) {
      byId.set(unit.id, unit);
    }

    setFolder({
      ...current,
      units: UnitsApi.sortByNewest([...byId.values()]),
    });

    void refetchBreakdown();
  };

  const renameUnit = async (
    current: FolderContent,
    unit: Unit,
    name: string,
  ): Promise<void> => {
    await UnitsApi.rename(unit.id, unit.type, name);
    setFolder({
      ...current,
      units: current.units.map((entry) =>
        entry.id === unit.id ? { ...entry, name } : entry,
      ),
    });
  };

  const moveUnit = async (
    current: FolderContent,
    unit: Unit,
    folderId: string,
  ): Promise<void> => {
    await UnitsApi.move(unit.id, unit.type, folderId);
    setFolder({
      ...current,
      units: current.units.filter((kept) => kept.id !== unit.id),
    });

    void refetchBreakdown();
  };

  const deleteUnit = async (
    current: FolderContent,
    unit: Unit,
  ): Promise<void> => {
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
              <h1 class="folder-name">{folderName()}</h1>
              <div class="folder-actions">
                <NewFolderButton
                  folderId={params.id}
                  onFolderCreated={(created) => { addUnits(created, params.id); }}
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
                  { navigate(`/folder/${params.id}/flashcards`); }
                }
                onReviewTest={() => { navigate(`/folder/${params.id}/test`); }}
              />
            )}
          </Show>

          <UnitsSection
            content={folder()}
            onImport={() => setImportOpen(true)}
            onDelete={(current, target) => void deleteUnit(current, target)}
            onRename={(current, target, name) =>
              void renameUnit(current, target, name)
            }
            onMove={(current, target, folderId) =>
              void moveUnit(current, target, folderId)
            }
          />
        </div>
      </div>

      <ImportFlow
        folderId={params.id}
        folderName={folderName()}
        isOpen={isImportOpen()}
        onClose={() => setImportOpen(false)}
        onUnitsAdded={addUnits}
      />
    </AppShell>
  );
}
