import { For, Show, createResource, createSignal, type JSX } from "solid-js";
import { useParams } from "@solidjs/router";
import { AppShell } from "../../shared/ui/AppShell";
import { ReviewOverlay } from "../../shared/ui/ReviewOverlay";
import { Icon } from "../../shared/ui/icons/Icon";
import { AssessmentReview } from "../assessment/AssessmentReview";
import { FlashcardsReview } from "../flashcards/FlashcardsReview";
import { DueSection } from "./DueSection";
import { ImportMenu } from "./import/ImportMenu";
import { StatsApi } from "./stats-api";
import { UnitListSkeleton } from "./UnitListSkeleton";
import { UnitPresentation } from "./unit-presentation";
import { UnitRow } from "./UnitRow";
import { UnitsApi } from "./units-api";
import type { Unit } from "../../shared/models/units";

type OpenReview = "none" | "flashcards" | "assessment";

export default function FolderPage(): JSX.Element {
  const params = useParams<{ id: string }>();
  const [folder, { mutate: setFolder }] = createResource(
    () => params.id,
    UnitsApi.folderContent,
  );
  const [breakdown, { refetch: refetchBreakdown }] = createResource(
    () => params.id,
    StatsApi.dueBreakdown,
  );
  const [openReview, setOpenReview] = createSignal<OpenReview>("none");

  const addUnits = (added: readonly Unit[]): void => {
    const current = folder();
    if (current === undefined) return;

    setFolder({
      ...current,
      units: UnitsApi.sortByNewest([...added, ...current.units]),
    });
  };

  const deleteUnit = async (unit: Unit): Promise<void> => {
    const current = folder();
    if (current === undefined) return;

    await UnitsApi.remove(unit.id, unit.type);
    setFolder({
      ...current,
      units: current.units.filter((kept) => kept.id !== unit.id),
    });
  };

  const closeReview = (): void => {
    setOpenReview("none");
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
                <ImportMenu
                  folderId={params.id}
                  folderName={folder()?.parentFolderName ?? "Home"}
                  variant="toolbar"
                  onUnitsAdded={addUnits}
                />
              </div>
            </div>
          </header>

          <Show when={breakdown()}>
            {(due) => (
              <DueSection
                breakdown={due()}
                onReviewFlashcards={() => setOpenReview("flashcards")}
                onReviewTest={() => setOpenReview("assessment")}
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
                      <ImportMenu
                        folderId={params.id}
                        folderName={loaded().parentFolderName}
                        variant="empty-state"
                        onUnitsAdded={addUnits}
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

      <Show when={openReview() === "flashcards"}>
        <ReviewOverlay title="Flashcards" onClose={closeReview}>
          <div class="review">
            <FlashcardsReview scope="folder" scopeId={params.id} />
          </div>
        </ReviewOverlay>
      </Show>

      <Show when={openReview() === "assessment"}>
        <ReviewOverlay title="Test" onClose={closeReview}>
          <div class="test-stage">
            <AssessmentReview scope="folder" scopeId={params.id} />
          </div>
        </ReviewOverlay>
      </Show>
    </AppShell>
  );
}
