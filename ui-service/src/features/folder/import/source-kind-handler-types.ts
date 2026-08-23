import type { JSX } from "solid-js";
import type { ExtractedSource, ImportRequest } from "./ImportDialog";
import type { ImportSourceProps } from "./ImportSource";
import type {
  GenerationOrigin,
  GenerationSource,
  UploadedFile,
} from "./generation-models";

export type UploadIntoFolder = (
  chosen: File,
) => Promise<readonly UploadedFile[]>;

export type SourceExtraction = {
  readonly uploadIntoFolder: UploadIntoFolder;
  readonly extractText: (source: GenerationSource) => Promise<string>;
  readonly writeNote: (topic: string) => Promise<ExtractedSource>;
};

export type SourceKindHandler = {
  readonly selectorLabel: string;
  readonly panel: (props: ImportSourceProps) => JSX.Element;
  readonly missingSource: (request: ImportRequest) => string | null;
  readonly sourceName: (request: ImportRequest) => string;
  readonly origin: (request: ImportRequest) => GenerationOrigin;
  readonly label: (request: ImportRequest) => string;
  readonly source: (
    request: ImportRequest,
    uploadIntoFolder: UploadIntoFolder,
  ) => Promise<GenerationSource | null>;
  readonly extract: (
    request: ImportRequest,
    extraction: SourceExtraction,
  ) => Promise<ExtractedSource>;
  readonly showsOptions: boolean;
  readonly writesNote: boolean;
  readonly uploadable: boolean;
};
