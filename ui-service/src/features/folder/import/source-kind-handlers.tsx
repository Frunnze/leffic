import { Show, type JSX } from "solid-js";
import { Icon } from "../../../shared/ui/icons/Icon";
import type { ImportSourceProps } from "./ImportSource";
import { PAGED_EXTENSIONS, type SourceKind } from "./import-options";
import { PdfPageRange } from "./PdfPageRange";
import type {
  SourceKindHandler,
} from "./source-kind-handler-types";
import { extractedSource } from "./source-extraction";

const isPaged = (chosen: File): boolean => {
  const chosenName = chosen.name.toLowerCase();

  return PAGED_EXTENSIONS.some((extension) =>
    chosenName.endsWith(`.${extension}`),
  );
};

const filePanel = (props: ImportSourceProps): JSX.Element => (
  <Show
    when={props.chosenFile}
    fallback={
      <div class="dropzone">
        <Icon name="fileSmall" />
        <span class="dropzone-text">Drop a file here</span>
        <label class="btn" for="import-file">
          Browse files
        </label>
        <span class="dropzone-hint">
          PDF, DOCX, PPTX or TXT · up to 20 MB
        </span>
      </div>
    }
  >
    {(chosen) => (
      <>
        <div class="chosen-file">
          <Icon name="fileSmall" size="sm" />
          <span class="chosen-file-name">{chosen().name}</span>
          <label class="btn" for="import-file">
            Replace
          </label>
        </div>

        <Show when={isPaged(chosen())}>
          <PdfPageRange
            firstPage={props.firstPage}
            lastPage={props.lastPage}
            onFirstPageChange={props.onFirstPageChange}
            onLastPageChange={props.onLastPageChange}
          />
        </Show>
      </>
    )}
  </Show>
);

const HANDLERS: Readonly<Record<SourceKind, SourceKindHandler>> = {
  file: {
    selectorLabel: "File",
    panel: filePanel,
    missingSource: (request) =>
      request.file === null ? "Choose a file first." : null,
    sourceName: (request) => request.file?.name ?? "",
    origin: (request) => ({
      kind: "file",
      reference: request.file?.name ?? "",
    }),
    label: (request) => request.file?.name ?? "your file",
    source: async (request, uploadIntoFolder) => {
      if (request.file === null) return null;

      const uploaded = await uploadIntoFolder(request.file);
      const first = uploaded[0];

      if (first === undefined) return null;

      return {
        kind: "file",
        fileId: first.fileId,
        firstPage: request.firstPage,
        lastPage: request.lastPage,
      };
    },
    extract: extractedSource,
    showsOptions: false,
    writesNote: false,
    uploadable: true,
  },
  link: {
    selectorLabel: "Link",
    panel: (props) => (
      <div class="field">
        <label for="import-link">Link</label>
        <input
          class="input"
          id="import-link"
          type="url"
          placeholder="https://"
          value={props.link}
          onInput={(event) =>
            { props.onLinkChange(event.currentTarget.value); }
          }
        />
        <span class="field-hint">
          A web page or a YouTube video with a transcript.
        </span>
      </div>
    ),
    missingSource: (request) =>
      request.link.trim().length === 0 ? "Paste a link first." : null,
    sourceName: (request) => request.link,
    origin: (request) => ({ kind: "link", reference: request.link }),
    label: (request) => request.link,
    source: (request) =>
      Promise.resolve({ kind: "link", url: request.link }),
    extract: extractedSource,
    showsOptions: false,
    writesNote: false,
    uploadable: false,
  },
  text: {
    selectorLabel: "Text",
    panel: (props) => (
      <div class="field">
        <label for="import-text">Text</label>
        <textarea
          class="input input-tall"
          id="import-text"
          value={props.text}
          onInput={(event) =>
            { props.onTextChange(event.currentTarget.value); }
          }
        />
        <span class="field-hint">
          Everything comes from this text. Leffic adds nothing of its own.
        </span>
      </div>
    ),
    missingSource: (request) =>
      request.text.trim().length === 0 ? "Paste some text first." : null,
    sourceName: () => "your text",
    origin: () => ({ kind: "text", reference: "" }),
    label: () => "your text",
    source: (request) =>
      Promise.resolve({ kind: "topic", topic: request.text }),
    extract: extractedSource,
    showsOptions: true,
    writesNote: false,
    uploadable: false,
  },
  topic: {
    selectorLabel: "Topic",
    panel: (props) => (
      <div class="field">
        <label for="import-topic">Topic</label>
        <input
          class="input"
          id="import-topic"
          type="text"
          placeholder="e.g. Action potentials"
          value={props.topic}
          onInput={(event) =>
            { props.onTopicChange(event.currentTarget.value); }
          }
        />
        <span class="field-hint">
          Leffic writes the material from what it knows.
        </span>
      </div>
    ),
    missingSource: (request) =>
      request.topic.trim().length === 0 ? "Name a topic first." : null,
    sourceName: (request) => request.topic,
    origin: (request) => ({ kind: "topic", reference: request.topic }),
    label: (request) => request.topic,
    source: (request) =>
      Promise.resolve({ kind: "topic", topic: request.topic }),
    extract: (request, extraction) => extraction.writeNote(request.topic),
    showsOptions: false,
    writesNote: true,
    uploadable: false,
  },
};

export const SourceKindHandlers = {
  options(): readonly { readonly kind: SourceKind; readonly label: string }[] {
    return (Object.keys(HANDLERS) as SourceKind[]).map((kind) => ({
      kind,
      label: HANDLERS[kind].selectorLabel,
    }));
  },

  of(kind: SourceKind): SourceKindHandler {
    return HANDLERS[kind];
  },
};
