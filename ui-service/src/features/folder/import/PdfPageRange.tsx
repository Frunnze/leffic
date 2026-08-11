import type { JSX } from "solid-js";

export type PdfPageRangeProps = {
  readonly firstPage: string;
  readonly lastPage: string;
  readonly onFirstPageChange: (page: string) => void;
  readonly onLastPageChange: (page: string) => void;
};

export function PdfPageRange(props: PdfPageRangeProps): JSX.Element {
  return (
    <div class="page-range">
      <span class="page-range-label">Pages</span>
      <input
        class="input input-narrow"
        type="number"
        min="1"
        aria-label="First page"
        placeholder="1"
        value={props.firstPage}
        onInput={(event) => props.onFirstPageChange(event.currentTarget.value)}
      />
      <span class="page-range-dash">to</span>
      <input
        class="input input-narrow"
        type="number"
        min="1"
        aria-label="Last page"
        placeholder="last"
        value={props.lastPage}
        onInput={(event) => props.onLastPageChange(event.currentTarget.value)}
      />
      <span class="field-hint">Leave empty to read the whole document.</span>
    </div>
  );
}
