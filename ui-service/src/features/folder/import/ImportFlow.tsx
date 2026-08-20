import { Show, onCleanup, type JSX } from "solid-js";
import { GenerationApi, type GenerationWish } from "./generation-api";
import { GenerationWatcher } from "./generation-watcher";
import {
  ImportDialog,
  type ExtractedSource,
  type ImportRequest,
} from "./ImportDialog";
import { ImportSources } from "./import-sources";
import { NotesApi } from "../../notes/notes-api";
import { useToasts } from "../../notifications/ToastContext";
import type {
  GenerationOrigin,
  GenerationSource,
  UploadedFile,
} from "./generation-models";
import type { Unit } from "../../../shared/models/units";

const KIND_LABELS = {
  flashcards: "Flashcards",
  note: "Note",
  test: "Test",
} as const;

export type ImportFlowProps = {
  readonly folderId: string;
  readonly folderName: string;
  readonly isOpen: boolean;
  readonly onClose: () => void;
  readonly onUnitsAdded: (units: readonly Unit[], folderId: string) => void;
};

export function ImportFlow(props: ImportFlowProps): JSX.Element {
  const toasts = useToasts();

  const startGeneration = async (
    source: GenerationSource,
    origin: GenerationOrigin,
    sourceLabel: string,
    wanted: GenerationWish,
  ): Promise<void> => {
    const targetFolderId = props.folderId;
    const progressToast = toasts.show({
      tone: "progress",
      title: `Generating from ${sourceLabel}`,
    });
    const tasks = await GenerationApi.start(
      source,
      origin,
      targetFolderId,
      wanted,
    );

    const stop = GenerationWatcher.watch(tasks, (outcome) => {
      toasts.dismiss(progressToast);

      if (outcome.units.length > 0) {
        props.onUnitsAdded(outcome.units, targetFolderId);
      }

      toasts.show(
        outcome.succeeded
          ? { tone: "success", title: `${KIND_LABELS[outcome.kind]} ready` }
          : {
              tone: "failure",
              title: `Couldn't generate the ${outcome.kind}`,
              detail: "The source could not be processed. Try again.",
            },
      );
    });

    onCleanup(stop);
  };

  const uploadIntoFolder = async (
    chosen: File,
  ): Promise<readonly UploadedFile[]> => {
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

    return uploaded;
  };

  const uploadOnly = async (request: ImportRequest): Promise<void> => {
    const chosen = request.file;

    if (chosen === null) return;

    props.onClose();

    const progressToast = toasts.show({
      tone: "progress",
      title: `Uploading ${chosen.name}`,
    });

    try {
      await uploadIntoFolder(chosen);
      toasts.dismiss(progressToast);
      toasts.show({ tone: "success", title: `${chosen.name} uploaded` });
    } catch {
      toasts.dismiss(progressToast);
      toasts.show({
        tone: "failure",
        title: `Couldn't upload ${chosen.name}`,
        detail: "The file could not be saved. Try again.",
      });
    }
  };

  const writtenNote = async (topic: string): Promise<ExtractedSource> => {
    const tasks = await GenerationApi.start(
      { kind: "topic", topic },
      { kind: "topic", reference: topic },
      props.folderId,
      {
        flashcardTypes: [],
        flashcardAmount: null,
        testTypes: [],
        testAmount: undefined,
        note: true,
      },
    );
    const outcome = await GenerationWatcher.awaitOne("note", tasks.noteTaskId);
    const writtenUnit = outcome.units[0];

    if (!outcome.succeeded || writtenUnit === undefined) {
      toasts.show({
        tone: "failure",
        title: "Couldn't write the note",
        detail: "The topic could not be turned into a note. Try again.",
      });

      return { text: "", isNoteAlreadyMade: false };
    }

    props.onUnitsAdded(outcome.units, props.folderId);
    const note = await NotesApi.note(writtenUnit.id);

    return { text: NotesApi.asPlainText(note.content), isNoteAlreadyMade: true };
  };

  const extractFrom = async (
    request: ImportRequest,
  ): Promise<ExtractedSource> => {
    if (request.kind === "topic") return writtenNote(request.topic);

    const source = await ImportSources.sourceFrom(
      request,
      uploadIntoFolder,
    );
    if (source === null) return { text: "", isNoteAlreadyMade: false };

    return {
      text: await GenerationApi.extractText(source),
      isNoteAlreadyMade: false,
    };
  };

  const generate = (request: ImportRequest, reviewedText: string): void => {
    props.onClose();
    void startGeneration(
      { kind: "topic", topic: reviewedText },
      ImportSources.originOf(request),
      ImportSources.labelFor(request),
      ImportSources.wishFrom(request),
    );
  };

  return (
    <Show when={props.isOpen}>
      <ImportDialog
        folderName={props.folderName}
        onExtract={extractFrom}
        onGenerate={generate}
        onUploadOnly={(request) => void uploadOnly(request)}
        onCancel={props.onClose}
      />
    </Show>
  );
}
