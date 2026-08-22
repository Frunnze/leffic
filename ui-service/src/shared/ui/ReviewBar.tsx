import type { JSX } from "solid-js";
import { Icon } from "./icons/Icon";

type ReviewBarProps = {
  readonly title: string;
  readonly onClose: () => void;
};

export function ReviewBar(props: ReviewBarProps): JSX.Element {
  return (
    <div class="review-bar">
      <span class="review-bar-title">{props.title}</span>
      <button
        class="btn btn-quiet btn-icon"
        type="button"
        aria-label={`Close ${props.title}`}
        onClick={() => {
          props.onClose();
        }}
      >
        <Icon name="closePlain" size="sm" />
      </button>
    </div>
  );
}
