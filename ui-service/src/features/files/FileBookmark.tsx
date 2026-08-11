import { Show, type JSX } from "solid-js";
import { Icon } from "../../shared/ui/icons/Icon";

export type FileBookmarkProps = {
  readonly page: number | null;
  readonly pageInView: number;
  readonly onRemember: (page: number) => void;
  readonly onForget: () => void;
};

export function FileBookmark(props: FileBookmarkProps): JSX.Element {
  return (
    <div class="file-bookmark">
      <Show when={props.page !== null}>
        <span class="file-bookmark-current">
          <Icon name="bookmark" size="sm" />
          Page {props.page}
        </span>
        <button class="btn btn-quiet" type="button" onClick={props.onForget}>
          Remove
        </button>
      </Show>

      <button
        class="btn"
        type="button"
        onClick={() => props.onRemember(props.pageInView)}
      >
        <Icon name="bookmark" size="sm" />
        Bookmark page {props.pageInView}
      </button>
    </div>
  );
}
