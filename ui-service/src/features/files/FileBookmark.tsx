import { type JSX } from "solid-js";
import { Icon } from "../../shared/ui/icons/Icon";

export type FileBookmarkProps = {
  readonly page: number | null;
  readonly pageInView: number;
  readonly onRemember: (page: number) => void;
  readonly onForget: () => void;
};

export function FileBookmark(props: FileBookmarkProps): JSX.Element {
  const isPageInViewBookmarked = (): boolean => props.page === props.pageInView;

  const label = (): string =>
    isPageInViewBookmarked()
      ? `Remove the bookmark on page ${props.pageInView}`
      : `Bookmark page ${props.pageInView}`;

  const toggleBookmark = (): void => {
    if (isPageInViewBookmarked()) {
      props.onForget();
      return;
    }

    props.onRemember(props.pageInView);
  };

  return (
    <button
      class="btn btn-quiet btn-icon file-bookmark"
      classList={{ "is-bookmarked": isPageInViewBookmarked() }}
      type="button"
      aria-pressed={isPageInViewBookmarked()}
      aria-label={label()}
      title={label()}
      onClick={toggleBookmark}
    >
      <Icon name="bookmark" size="sm" />
    </button>
  );
}
