import { Show, createSignal, type JSX } from "solid-js";
import { Icon } from "../../shared/ui/icons/Icon";

export type FileBookmarkProps = {
  readonly page: number | null;
  readonly onRemember: (page: number) => void;
  readonly onForget: () => void;
};

export function FileBookmark(props: FileBookmarkProps): JSX.Element {
  const [typedPage, setTypedPage] = createSignal("");

  const remember = (): void => {
    const page = Number.parseInt(typedPage(), 10);

    if (Number.isNaN(page) || page < 1) return;

    props.onRemember(page);
    setTypedPage("");
  };

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

      <input
        class="input input-narrow"
        type="number"
        min="1"
        aria-label="Page to bookmark"
        placeholder="Page"
        value={typedPage()}
        onInput={(event) => setTypedPage(event.currentTarget.value)}
        onKeyDown={(event) => {
          if (event.key !== "Enter") return;

          event.preventDefault();
          remember();
        }}
      />
      <button class="btn" type="button" onClick={remember}>
        Bookmark
      </button>
    </div>
  );
}
