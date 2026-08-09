import type { JSX } from "solid-js";
import { Icon } from "./icons/Icon";

export type ReviewOverlayProps = {
  readonly title: string;
  readonly onClose: () => void;
  readonly children: JSX.Element;
};

export function ReviewOverlay(props: ReviewOverlayProps): JSX.Element {
  return (
    <div class="overlay" role="dialog" aria-modal="true" aria-label={props.title}>
      <div class="overlay-bar">
        <span class="overlay-title">{props.title}</span>
        <button
          class="btn btn-quiet btn-icon"
          type="button"
          aria-label={`Close ${props.title}`}
          onClick={() => props.onClose()}
        >
          <Icon name="closePlain" size="sm" />
        </button>
      </div>
      {props.children}
    </div>
  );
}
