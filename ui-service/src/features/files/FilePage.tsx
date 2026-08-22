import {
  Match,
  Show,
  Switch,
  createEffect,
  createResource,
  createSignal,
  on,
  type JSX,
} from "solid-js";
import { useNavigate, useParams } from "@solidjs/router";
import { AppShell } from "../../shared/ui/AppShell";
import { Icon } from "../../shared/ui/icons/Icon";
import { FileBookmark } from "./FileBookmark";
import { FilesApi, type OpenedFile } from "./files-api";
import { FileFailure } from "./FileFailure";
import { FileSpinner } from "./FileSpinner";
import { PdfPages } from "./PdfPages";

type FileRouteParams = {
  readonly id: string;
  readonly extension: string;
};

export default function FilePage(): JSX.Element {
  const params = useParams<FileRouteParams>();
  const navigate = useNavigate();
  const [opened] = createResource(
    () => ({ id: params.id, extension: params.extension }),
    (route: FileRouteParams) => FilesApi.opened(route.id, route.extension),
  );
  const [bookmarkedPage, setBookmarkedPage] = createSignal<number | null>(null);
  const [pageInView, setPageInView] = createSignal(1);

  const fileName = (): string => `${params.id}.${params.extension}`;

  const readyFile = (): OpenedFile | undefined => {
    if (opened.loading || opened.error) return undefined;

    return opened();
  };

  createEffect(
    on(readyFile, (file: OpenedFile | undefined) => {
      setBookmarkedPage(file?.bookmarkedPage ?? null);
    }),
  );

  const failure = (): string | null => {
    const reason: unknown = opened.error;

    if (reason instanceof Error) return reason.message;

    return null;
  };

  const remember = async (page: number): Promise<void> => {
    setBookmarkedPage(await FilesApi.rememberPage(params.id, page));
  };

  const forget = async (): Promise<void> => {
    await FilesApi.forgetPage(params.id);
    setBookmarkedPage(null);
  };

  return (
    <AppShell fillsViewport>
      <div class="file-stage">
        <div class="file-bar">
          <Icon name="file" />
          <span class="file-name">{fileName()}</span>
          <span class="file-chip">{params.extension.toUpperCase()}</span>
          <Show when={readyFile()}>
            {(file) => (
              <span class="file-position">
                Page {pageInView()} of {file().document.numPages}
              </span>
            )}
          </Show>
          <FileBookmark
            page={bookmarkedPage()}
            pageInView={pageInView()}
            onRemember={(page) => void remember(page)}
            onForget={() => void forget()}
          />
          <button
            class="btn btn-quiet btn-icon"
            type="button"
            aria-label={`Close ${fileName()}`}
            title="Close"
            onClick={() => { navigate(-1); }}
          >
            <Icon name="closePlain" size="sm" />
          </button>
        </div>

        <Switch
          fallback={<FileSpinner label={`Opening ${fileName()}…`} />}
        >
          <Match when={failure()}>
            {(reason) => (
              <FileFailure fileName={fileName()} reason={reason()} />
            )}
          </Match>

          <Match when={readyFile()}>
            {(file) => (
              <PdfPages
                document={file().document}
                openAtPage={file().bookmarkedPage}
                onPageInView={setPageInView}
              />
            )}
          </Match>
        </Switch>
      </div>
    </AppShell>
  );
}
