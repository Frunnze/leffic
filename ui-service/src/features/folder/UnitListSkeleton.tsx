import { For, type JSX } from "solid-js";

const PLACEHOLDER_WIDTHS: readonly (readonly [string, string])[] = [
  ["46%", "24%"],
  ["62%", "18%"],
  ["38%", "30%"],
  ["54%", "22%"],
];

export function UnitListSkeleton(): JSX.Element {
  return (
    <div class="skeleton-list" aria-busy="true" aria-live="polite">
      <span class="visually-hidden">Loading folder contents</span>
      <For each={PLACEHOLDER_WIDTHS}>
        {([nameWidth, metaWidth]) => (
          <div class="skeleton-row">
            <span class="skeleton-dot" />
            <span class="skeleton-lines">
              <span class="skeleton-bar" style={`width: ${nameWidth}`} />
              <span class="skeleton-bar" style={`width: ${metaWidth}`} />
            </span>
          </div>
        )}
      </For>
    </div>
  );
}
