import { Show, createSignal, onCleanup, type JSX } from "solid-js";
import { Dropdown } from "../../../shared/ui/Dropdown";
import { Icon } from "../../../shared/ui/icons/Icon";
import { PromptDialog } from "../../../shared/ui/PromptDialog";
import { GenerationApi } from "./generation-api";
import { GenerationWatcher } from "./generation-watcher";
import { useToasts } from "../../notifications/ToastContext";
import type { GenerationSource } from "./generation-models";
import type { Unit } from "../../../shared/models/units";

const KIND_LABELS = {
  flashcards: "Flashcards",
  note: "Note",
  test: "Test",
} as const;

type OpenDialog = "none" | "link" | "topic";

export type ImportMenuProps = {
  readonly folderId: string;
  readonly folderName: string;
  readonly variant: "toolbar" | "empty-state";
  readonly onUnitsAdded: (units: readonly Unit[]) => void;
};

export function ImportMenu(props: ImportMenuProps): JSX.Element {
  const toasts = useToasts();
  const [isMenuOpen, setMenuOpen] = createSignal(false);
  const [openDialog, setOpenDialog] = createSignal<OpenDialog>("none");
  let fileInput: HTMLInputElement | undefined;

  const startGeneration = async (
    source: GenerationSource,
    sourceLabel: string,
  ): Promise<void> => {
    const progressToast = toasts.show({
      tone: "progress",
      title: `Generating from ${sourceLabel}`,
      detail: "About a minute. You can keep working.",
    });
    const tasks = await GenerationApi.start(source, props.folderId);

    const stop = GenerationWatcher.watch(tasks, (outcome) => {
      toasts.dismiss(progressToast);

      if (outcome.unit !== null) props.onUnitsAdded([outcome.unit]);

      toasts.show({
        tone: outcome.succeeded ? "success" : "failure",
        title: outcome.succeeded
          ? `${KIND_LABELS[outcome.kind]} ready`
          : `Couldn't generate the ${outcome.kind}`,
        detail: outcome.succeeded
          ? `Generated from ${sourceLabel}.`
          : "The source could not be processed. Try again.",
      });
    });

    onCleanup(stop);
  };

  const uploadChosenFile = async (chosen: File): Promise<void> => {
    const uploaded = await GenerationApi.uploadFile(chosen, props.folderId);
    props.onUnitsAdded(
      uploaded.map((file) => ({
        id: file.fileId,
        name: file.name,
        type: "file" as const,
        createdAt: file.createdAt,
        extension: file.extension,
        dueCount: null,
        meta: null,
      })),
    );

    const first = uploaded[0];
    if (first === undefined) return;

    await startGeneration(
      { kind: "file", fileId: first.fileId, extension: first.extension },
      first.name,
    );
  };

  const chooseSource = (open: () => void): void => {
    setMenuOpen(false);
    open();
  };

  return (
    <>
      <div class="folder-action">
        <button
          class={props.variant === "toolbar" ? "btn" : "btn btn-primary btn-lg"}
          type="button"
          aria-expanded={isMenuOpen()}
          onClick={() => setMenuOpen(!isMenuOpen())}
        >
          <Icon name="aiImport" size="sm" />
          Import
        </button>
        <Dropdown
          isOpen={isMenuOpen()}
          onDismiss={() => setMenuOpen(false)}
          items={[
            {
              label: "File",
              icon: "fileSmall",
              onSelect: () => chooseSource(() => fileInput?.click()),
            },
            {
              label: "Link",
              icon: "link",
              onSelect: () => chooseSource(() => setOpenDialog("link")),
            },
            {
              label: "Topic",
              icon: "topic",
              onSelect: () => chooseSource(() => setOpenDialog("topic")),
            },
          ]}
        />
      </div>

      <input
        ref={fileInput}
        class="visually-hidden"
        type="file"
        aria-label="Choose a file to import"
        onChange={(event) => {
          const chosen = event.currentTarget.files?.[0];
          event.currentTarget.value = "";
          if (chosen !== undefined) void uploadChosenFile(chosen);
        }}
      />

      <Show when={openDialog() === "link"}>
        <PromptDialog
          title="Generate from a link"
          description={`Saved into ${props.folderName}.`}
          label="Page address"
          placeholder="https://"
          inputType="url"
          confirmLabel="Generate"
          onCancel={() => setOpenDialog("none")}
          onConfirm={(url) => {
            setOpenDialog("none");
            void startGeneration({ kind: "link", url }, url);
          }}
        />
      </Show>

      <Show when={openDialog() === "topic"}>
        <PromptDialog
          title="Generate from a topic"
          description={`Saved into ${props.folderName}.`}
          label="Topic"
          placeholder="e.g. Action potentials"
          inputType="text"
          confirmLabel="Generate"
          onCancel={() => setOpenDialog("none")}
          onConfirm={(topic) => {
            setOpenDialog("none");
            void startGeneration({ kind: "topic", topic }, topic);
          }}
        />
      </Show>
    </>
  );
}
