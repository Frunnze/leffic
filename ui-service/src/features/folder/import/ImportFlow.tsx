import { Show, type JSX } from "solid-js";
import { GenerationApi } from "./generation-api";
import { GenerationWatcher } from "./generation-watcher";
import { useGenerations } from "./GenerationContext";
import {
  ImportDialog,
  type ExtractedSource,
  type ImportRequest,
} from "./ImportDialog";
import { ImportSources } from "./import-sources";
import { SourceKindHandlers } from "./source-kind-handlers";
import { NotesApi } from "../../../shared/notes/notes-api";
import { useToasts } from "../../../shared/notifications/ToastContext";
import type { UploadedFile } from "./generation-models";
import type { Unit } from "../unit-models";

type ImportFlowProps = {
  readonly folderId: string;
  readonly folderName: string;
  readonly isOpen: boolean;
  readonly onClose: () => void;
  readonly onUnitsAdded: (units: readonly Unit[], folderId: string) => void;
};

export function ImportFlow(props: ImportFlowProps): JSX.Element {
  const toasts = useToasts();
  const generations = useGenerations();

  const uploadIntoFolder = async (
    chosen: File,
  ): Promise<readonly UploadedFile[]> => {
    const targetFolderId = props.folderId;
    const uploaded = await GenerationApi.uploadFile(chosen, targetFolderId);

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
      targetFolderId,
    );

    return uploaded;
  };

  const uploadOnly = async (chosen: File): Promise<void> => {
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
    const targetFolderId = props.folderId;
    const tasks = await GenerationApi.start(
      { kind: "topic", topic },
      { kind: "topic", reference: topic },
      targetFolderId,
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

    props.onUnitsAdded(outcome.units, targetFolderId);
    const note = await NotesApi.note(writtenUnit.id);

    return { text: NotesApi.asPlainText(note.content), isNoteAlreadyMade: true };
  };

  const extractFrom = async (
    request: ImportRequest,
  ): Promise<ExtractedSource> => {
    return SourceKindHandlers.of(request.kind).extract(request, {
      extractText: GenerationApi.extractText,
      uploadIntoFolder,
      writeNote: writtenNote,
    });
  };

  const generate = (request: ImportRequest, reviewedText: string): void => {
    props.onClose();
    void generations.start({
      source: { kind: "topic", topic: reviewedText },
      origin: ImportSources.originOf(request),
      folderId: props.folderId,
      sourceLabel: ImportSources.labelFor(request),
      wanted: ImportSources.wishFrom(request),
    });
  };

  return (
    <Show when={props.isOpen}>
      <ImportDialog
        folderName={props.folderName}
        onExtract={extractFrom}
        onGenerate={generate}
        onUploadOnly={(chosen) => void uploadOnly(chosen)}
        onCancel={props.onClose}
      />
    </Show>
  );
}
