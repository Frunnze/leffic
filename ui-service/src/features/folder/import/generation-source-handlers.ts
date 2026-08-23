import type { GenerationSource } from "./generation-models";

type SourceKind = GenerationSource["kind"];
type SourceOf<Kind extends SourceKind> = Extract<
  GenerationSource,
  { kind: Kind }
>;
type ExtractText = (source: GenerationSource) => Promise<string>;
type SourceHandler<Kind extends SourceKind> = {
  readonly text: (
    source: SourceOf<Kind>,
    extract: ExtractText,
  ) => Promise<string>;
  readonly body: (
    source: SourceOf<Kind>,
  ) => Readonly<Record<string, unknown>>;
};
type SourceHandlers = {
  readonly [Kind in SourceKind]: SourceHandler<Kind>;
};

const HANDLERS: SourceHandlers = {
  file: {
    text: (source, extract) => extract(source),
    body: (source) => {
      const pages: Record<string, number> = {};

      if (source.firstPage !== null) pages.first = source.firstPage;
      if (source.lastPage !== null) pages.last = source.lastPage;

      const asked = Object.keys(pages).length === 0 ? {} : { pages };

      return {
        file_metadata: [
          { file_id: source.fileId, extension: source.extension, ...asked },
        ],
      };
    },
  },
  link: {
    text: (source, extract) => extract(source),
    body: (source) => ({ link_metadata: source.url }),
  },
  topic: {
    text: (source) => Promise.resolve(source.topic),
    body: (source) => ({ topic_metadata: source.topic }),
  },
};

const handlerFor = <Kind extends SourceKind>(
  kind: Kind,
): SourceHandler<Kind> => HANDLERS[kind];

export const GenerationSourceHandlers = {
  text(source: GenerationSource, extract: ExtractText): Promise<string> {
    return handlerFor(source.kind).text(source, extract);
  },

  body(source: GenerationSource): Readonly<Record<string, unknown>> {
    return handlerFor(source.kind).body(source);
  },
};
