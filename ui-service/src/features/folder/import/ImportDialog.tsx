import { Match, Show, Switch, createSignal, type JSX } from "solid-js";
import { GenerationChoices } from "./GenerationChoices";
import { ImportOptions } from "./import-options";
import { ImportRequestReading } from "./import-request";
import { ImportFooter } from "./ImportFooter";
import { ImportSource } from "./ImportSource";
import { ImportReview, ImportWait } from "./ImportReview";
import type { SourceKind, UnitChoice } from "./import-options";
import { ModalBackdrop } from "../../../shared/ui/ModalBackdrop";
import { DIALOG_TITLE_ID, ModalHead } from "../../../shared/ui/ModalHead";

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

type ImportDialogProps = {
  readonly folderName: string;
  readonly onExtract: (request: ImportRequest) => Promise<ExtractedSource>;
  readonly onGenerate: (request: ImportRequest, text: string) => void;
  readonly onUploadOnly: (file: File) => void;
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
  const [extracted, setExtracted] = createSignal<ExtractedSource | null>(null);
  const [isExtracting, setExtracting] = createSignal(false);
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
    kind() === "text" || extracted() !== null;

  const uploadableFile = (): File | null => {
    if (kind() !== "file" || isShowingOptions()) return null;

    return chosenFile();
  };

  const continueToReview = async (): Promise<void> => {
    setExtracting(true);

    const source = await props.onExtract(request());

    if (source.isNoteAlreadyMade) setNote(ImportOptions.emptyChoice());

    setExtracted(source);
    setExtracting(false);
  };

  return (
    <ModalBackdrop onDismiss={props.onCancel}>
      <div
        class="modal modal-wide"
        role="dialog"
        aria-modal="true"
        aria-labelledby={DIALOG_TITLE_ID}
      >
        <ModalHead
          title="Import"
          description={<>Saved into {props.folderName}.</>}
          onClose={props.onCancel}
        />

        <div class="modal-body">
          <Switch>
            <Match when={isExtracting()}>
              <ImportWait
                isWritingNote={kind() === "topic"}
                sourceName={sourceName()}
              />
            </Match>

            <Match when={extracted()}>
              {(source) => (
                <ImportReview
                  sourceName={sourceName()}
                  isNoteAlreadyMade={source().isNoteAlreadyMade}
                  text={source().text}
                  onTextChange={(text) => setExtracted({ ...source(), text })}
                />
              )}
            </Match>

            <Match when={extracted() === null}>
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
              isNoteAlreadyMade={extracted()?.isNoteAlreadyMade ?? false}
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
          uploadableFile={uploadableFile()}
          onCancel={props.onCancel}
          onUploadOnly={props.onUploadOnly}
          onContinue={() => void continueToReview()}
          onGenerate={() =>
            { props.onGenerate(request(), extracted()?.text ?? text()); }
          }
        />
      </div>
    </ModalBackdrop>
  );
}
