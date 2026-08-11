import {
  Show,
  createEffect,
  createResource,
  createSignal,
  on,
  type JSX,
} from "solid-js";
import { useParams } from "@solidjs/router";
import { AppShell } from "../../shared/ui/AppShell";
import { Icon } from "../../shared/ui/icons/Icon";
import { FileBookmark } from "./FileBookmark";
import { FilesApi, type OpenedFile } from "./files-api";
import { FileSpinner } from "./FileSpinner";

type FileRouteParams = {
  readonly id: string;
  readonly extension: string;
};

export default function FilePage(): JSX.Element {
  const params = useParams<FileRouteParams>();
  const [opened] = createResource(
    () => ({ id: params.id, extension: params.extension }),
    (route: FileRouteParams) => FilesApi.opened(route.id, route.extension),
  );
  const [bookmarkedPage, setBookmarkedPage] = createSignal<number | null>(null);

  createEffect(
    on(opened, (file: OpenedFile | undefined) => {
      if (file === undefined) return;

      setBookmarkedPage(file.bookmarkedPage);
    }),
  );

  const fileName = (): string => `${params.id}.${params.extension}`;

  const openedAt = (file: OpenedFile): string =>
    file.bookmarkedPage === null
      ? file.url
      : `${file.url}#page=${file.bookmarkedPage}`;

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
          <FileBookmark
            page={bookmarkedPage()}
            onRemember={(page) => void remember(page)}
            onForget={() => void forget()}
          />
        </div>

        <Show
          when={opened()}
          fallback={<FileSpinner label={`Opening ${fileName()}…`} />}
        >
          {(file) => (
            <iframe
              class="file-frame"
              src={openedAt(file())}
              title={fileName()}
            />
          )}
        </Show>
      </div>
    </AppShell>
  );
}
