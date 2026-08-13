import { Show, onCleanup, type JSX } from "solid-js";
import { GenerationApi, type GenerationWish } from "./generation-api";
import { GenerationWatcher } from "./generation-watcher";
import {
  ImportDialog,
  type ExtractedSource,
  type ImportRequest,
} from "./ImportDialog";
import { ImportOptions } from "./import-options";
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

      if (outcome.unit !== null) {
        props.onUnitsAdded([outcome.unit], targetFolderId);
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

    const uploaded = await uploadIntoFolder(chosen);
    const first = uploaded[0];

    if (first === undefined) return null;

    return {
      kind: "file",
      fileId: first.fileId,
      extension: first.extension,
      firstPage: request.firstPage,
      lastPage: request.lastPage,
    };
  };

  const writtenNote = async (topic: string): Promise<ExtractedSource> => {
    const tasks = await GenerationApi.start(
      { kind: "topic", topic },
      { kind: "topic", reference: topic },
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

  const originOf = (request: ImportRequest): GenerationOrigin => {
    if (request.kind === "file") {
      return { kind: "file", reference: request.file?.name ?? "" };
    }
    if (request.kind === "link") {
      return { kind: "link", reference: request.link };
    }
    if (request.kind === "topic") {
      return { kind: "topic", reference: request.topic };
    }

    return { kind: "text", reference: "" };
  };

  const sourceLabel = (request: ImportRequest): string => {
    if (request.kind === "file") return request.file?.name ?? "your file";
    if (request.kind === "link") return request.link;
    if (request.kind === "topic") return request.topic;

    return "your text";
  };

  const generate = (request: ImportRequest, reviewedText: string): void => {
    props.onClose();
    void startGeneration(
      { kind: "topic", topic: reviewedText },
      originOf(request),
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
