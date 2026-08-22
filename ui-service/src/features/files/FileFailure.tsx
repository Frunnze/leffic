import type { JSX } from "solid-js";
import { Icon } from "../../shared/ui/icons/Icon";

type FileFailureProps = {
  readonly fileName: string;
  readonly reason: string;
};

export function FileFailure(props: FileFailureProps): JSX.Element {
  return (
    <div class="file-failure">
      <Icon name="failure" size="lg" />
      <p class="file-failure-title">Couldn't open {props.fileName}</p>
      <p class="file-failure-reason">{props.reason}</p>
      <button
        class="btn"
        type="button"
        onClick={() => { window.location.reload(); }}
      >
        Try again
      </button>
    </div>
  );
}
