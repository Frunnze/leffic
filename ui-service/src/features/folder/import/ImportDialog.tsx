import { Match, Show, Switch, createSignal, type JSX } from "solid-js";
import { GenerationChoices } from "./GenerationChoices";
import { Icon } from "../../../shared/ui/icons/Icon";
import { ImportOptions } from "./import-options";
import { ImportRequestReading } from "./import-request";
import { ImportFooter } from "./ImportFooter";
import { ImportSource } from "./ImportSource";
import { ImportReview, ImportWait } from "./ImportReview";
import type { SourceKind, UnitChoice } from "./import-options";

export type ImportRequest = {
  readonly kind: SourceKind;
  readonly file: File | null;
  readonly link: string;
  readonly text: string;
  readonly topic: string;
  readonly firstPage: number | null;
  readonly lastPage: number | null;
  readonly flashcards: UnitChoice;
  readonly test: UnitChoice;
  readonly note: UnitChoice;
};

export type ExtractedSource = {
  readonly text: string;
  readonly isNoteAlreadyMade: boolean;
};

export type ImportDialogProps = {
  readonly folderName: string;
  readonly onExtract: (request: ImportRequest) => Promise<ExtractedSource>;
  readonly onGenerate: (request: ImportRequest, text: string) => void;
  readonly onUploadOnly: (request: ImportRequest) => void;
  readonly onCancel: () => void;
};

export function ImportDialog(props: ImportDialogProps): JSX.Element {
  const [kind, setKind] = createSignal<SourceKind>("file");
  const [chosenFile, setChosenFile] = createSignal<File | null>(null);
  const [link, setLink] = createSignal("");
  const [text, setText] = createSignal("");
  const [topic, setTopic] = createSignal("");
  const [firstPage, setFirstPage] = createSignal("");
  const [lastPage, setLastPage] = createSignal("");
  const [extractedText, setExtractedText] = createSignal<string | null>(null);
  const [isExtracting, setExtracting] = createSignal(false);
  const [isNoteAlreadyMade, setNoteAlreadyMade] = createSignal(false);
  const [flashcards, setFlashcards] = createSignal<UnitChoice>(
    ImportOptions.startingChoice("basic"),
  );
  const [test, setTest] = createSignal<UnitChoice>(
    ImportOptions.startingChoice("multiple_choice"),
  );
  const [note, setNote] = createSignal<UnitChoice>({
    ...ImportOptions.emptyChoice(),
    isChosen: true,
  });

  const request = (): ImportRequest => ({
    kind: kind(),
    file: chosenFile(),
    link: link(),
    text: text(),
    topic: topic(),
    firstPage: ImportRequestReading.chosenPage(firstPage()),
    lastPage: ImportRequestReading.chosenPage(lastPage()),
    flashcards: flashcards(),
    test: test(),
    note: note(),
  });

  const missingSource = (): string | null =>
    ImportRequestReading.missingSource(request());

  const sourceName = (): string => ImportRequestReading.sourceName(request());

  const nothingChosen = (): boolean =>
    ImportRequestReading.nothingChosen(request());

  const isShowingOptions = (): boolean =>
    kind() === "text" || extractedText() !== null;

  const canUploadOnly = (): boolean =>
    kind() === "file" && chosenFile() !== null && !isShowingOptions();

  const continueToReview = async (): Promise<void> => {
    setExtracting(true);

    const extracted = await props.onExtract(request());
    setNoteAlreadyMade(extracted.isNoteAlreadyMade);

    if (extracted.isNoteAlreadyMade) setNote(ImportOptions.emptyChoice());

    setExtractedText(extracted.text);
    setExtracting(false);
  };

  return (
    <div
      class="modal-backdrop"
      onClick={(event) => {
        if (event.target === event.currentTarget) props.onCancel();
      }}
    >
      <div
        class="modal modal-wide"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
      >
        <div class="modal-head">
          <div class="modal-heading">
            <h2 class="modal-title" id="dialog-title">
              Import
            </h2>
            <span class="modal-text">Saved into {props.folderName}.</span>
          </div>
          <button
            class="btn btn-quiet btn-icon"
            type="button"
            aria-label="Close dialog"
            onClick={() => props.onCancel()}
          >
            <Icon name="closePlain" size="sm" />
          </button>
        </div>

        <div class="modal-body">
          <Switch>
            <Match when={isExtracting()}>
              <ImportWait
                isWritingNote={kind() === "topic"}
                sourceName={sourceName()}
              />
            </Match>

            <Match when={extractedText() !== null}>
              <ImportReview
                sourceName={sourceName()}
                isNoteAlreadyMade={isNoteAlreadyMade()}
                text={extractedText() ?? ""}
                onTextChange={setExtractedText}
              />
            </Match>

            <Match when={extractedText() === null}>
              <ImportSource
                kind={kind()}
                chosenFile={chosenFile()}
                link={link()}
                text={text()}
                topic={topic()}
                firstPage={firstPage()}
                lastPage={lastPage()}
                onFirstPageChange={setFirstPage}
                onLastPageChange={setLastPage}
                onKindChange={setKind}
                onFileChosen={setChosenFile}
                onLinkChange={setLink}
                onTextChange={setText}
                onTopicChange={setTopic}
              />
            </Match>
          </Switch>

          <Show when={isShowingOptions() && !isExtracting()}>
            <GenerationChoices
              isNoteAlreadyMade={isNoteAlreadyMade()}
              flashcards={flashcards()}
              test={test()}
              note={note()}
              onFlashcardsChange={setFlashcards}
              onTestChange={setTest}
              onNoteChange={setNote}
            />
          </Show>
        </div>

        <ImportFooter
          missingSource={missingSource()}
          nothingChosen={nothingChosen()}
          isReviewing={isShowingOptions()}
          isExtracting={isExtracting()}
          canUploadOnly={canUploadOnly()}
          onCancel={props.onCancel}
          onUploadOnly={() => props.onUploadOnly(request())}
          onContinue={() => void continueToReview()}
          onGenerate={() =>
            props.onGenerate(request(), extractedText() ?? text())
          }
        />
      </div>
    </div>
  );
}
