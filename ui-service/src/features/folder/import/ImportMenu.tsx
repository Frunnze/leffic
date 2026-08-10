import { Show, createSignal, onCleanup, type JSX } from "solid-js";
import { GenerationApi, type GenerationWish } from "./generation-api";
import { GenerationWatcher } from "./generation-watcher";
import { Icon } from "../../../shared/ui/icons/Icon";
import {
  ImportDialog,
  type ExtractedSource,
  type ImportRequest,
} from "./ImportDialog";
import { ImportOptions } from "./import-options";
import { NotesApi } from "../../notes/notes-api";
import { useToasts } from "../../notifications/ToastContext";
import type { GenerationSource } from "./generation-models";
import type { Unit } from "../../../shared/models/units";

const KIND_LABELS = {
  flashcards: "Flashcards",
  note: "Note",
  test: "Test",
} as const;

export type ImportMenuProps = {
  readonly folderId: string;
  readonly folderName: string;
  readonly variant: "toolbar" | "empty-state";
  readonly onUnitsAdded: (units: readonly Unit[], folderId: string) => void;
};

export function ImportMenu(props: ImportMenuProps): JSX.Element {
  const toasts = useToasts();
  const [isDialogOpen, setDialogOpen] = createSignal(false);

  const startGeneration = async (
    source: GenerationSource,
    sourceLabel: string,
    wanted: GenerationWish,
  ): Promise<void> => {
    const targetFolderId = props.folderId;
    const progressToast = toasts.show({
      tone: "progress",
      title: `Generating from ${sourceLabel}`,
      detail: "About a minute. You can keep working.",
    });
    const tasks = await GenerationApi.start(source, targetFolderId, wanted);

    const stop = GenerationWatcher.watch(tasks, (outcome) => {
      toasts.dismiss(progressToast);

      if (outcome.unit !== null) {
        props.onUnitsAdded([outcome.unit], targetFolderId);
      }

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

  const uploadedSource = async (
    request: ImportRequest,
  ): Promise<GenerationSource | null> => {
    if (request.kind === "link") return { kind: "link", url: request.link };
    if (request.kind === "topic") {
      return { kind: "topic", topic: request.topic };
    }
    if (request.kind === "text") {
      return { kind: "topic", topic: request.text };
    }

    const chosen = request.file;
    if (chosen === null) return null;

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
      props.folderId,
    );

    const first = uploaded[0];
    if (first === undefined) return null;

    return { kind: "file", fileId: first.fileId, extension: first.extension };
  };

  const writtenNote = async (topic: string): Promise<ExtractedSource> => {
    const tasks = await GenerationApi.start(
      { kind: "topic", topic },
      props.folderId,
      { flashcardTypes: [], flashcardAmount: null, testAmount: undefined, note: true },
    );
    const outcome = await GenerationWatcher.awaitOne("note", tasks.noteTaskId);

    if (!outcome.succeeded || outcome.unit === null) {
      toasts.show({
        tone: "failure",
        title: "Couldn't write the note",
        detail: "The topic could not be turned into a note. Try again.",
      });

      return { text: "", isNoteAlreadyMade: false };
    }

    props.onUnitsAdded([outcome.unit], props.folderId);
    const note = await NotesApi.note(outcome.unit.id);

    return { text: NotesApi.asPlainText(note.content), isNoteAlreadyMade: true };
  };

  const extractFrom = async (
    request: ImportRequest,
  ): Promise<ExtractedSource> => {
    if (request.kind === "topic") return writtenNote(request.topic);

    const source = await uploadedSource(request);
    if (source === null) return { text: "", isNoteAlreadyMade: false };

    return {
      text: await GenerationApi.extractText(source),
      isNoteAlreadyMade: false,
    };
  };

  const sourceLabel = (request: ImportRequest): string => {
    if (request.kind === "file") return request.file?.name ?? "your file";
    if (request.kind === "link") return request.link;
    if (request.kind === "topic") return request.topic;

    return "your text";
  };

  const generate = (request: ImportRequest, reviewedText: string): void => {
    setDialogOpen(false);
    void startGeneration(
      { kind: "topic", topic: reviewedText },
      sourceLabel(request),
      {
        flashcardTypes: request.flashcards.isChosen
          ? request.flashcards.chosenTypes
          : [],
        flashcardAmount: ImportOptions.totalCount(request.flashcards),
        testAmount: request.test.isChosen
          ? ImportOptions.totalCount(request.test)
          : undefined,
        note: request.note.isChosen,
      },
    );
  };

  return (
    <>
      <div class="folder-action">
        <button
          class={props.variant === "toolbar" ? "btn" : "btn btn-primary btn-lg"}
          type="button"
          onClick={() => setDialogOpen(true)}
        >
          <Icon name="aiImport" size="sm" />
          Import
        </button>
      </div>

      <Show when={isDialogOpen()}>
        <ImportDialog
          folderName={props.folderName}
          onExtract={extractFrom}
          onGenerate={generate}
          onCancel={() => setDialogOpen(false)}
        />
      </Show>
    </>
  );
}
