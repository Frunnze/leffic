import { Show, createResource, type JSX } from "solid-js";
import { useParams } from "@solidjs/router";
import { AppShell } from "../../shared/ui/AppShell";
import { Icon } from "../../shared/ui/icons/Icon";
import { FilesApi } from "./files-api";
import { FileSpinner } from "./FileSpinner";

type FileRouteParams = {
  readonly id: string;
  readonly extension: string;
};

export default function FilePage(): JSX.Element {
  const params = useParams<FileRouteParams>();
  const [fileUrl] = createResource(
    () => ({ id: params.id, extension: params.extension }),
    (route: FileRouteParams) => FilesApi.openableUrl(route.id, route.extension),
  );

  const fileName = (): string => `${params.id}.${params.extension}`;

  return (
    <AppShell fillsViewport>
      <div class="file-stage">
        <div class="file-bar">
          <Icon name="file" />
          <span class="file-name">{fileName()}</span>
          <span class="file-chip">{params.extension.toUpperCase()}</span>
        </div>

        <Show
          when={fileUrl()}
          fallback={<FileSpinner label={`Opening ${fileName()}…`} />}
        >
          {(url) => (
            <iframe class="file-frame" src={url()} title={fileName()} />
          )}
        </Show>
      </div>
    </AppShell>
  );
}
