import { Show, type JSX } from "solid-js";

type MeterProps = {
  readonly done: number;
  readonly total: number;
  readonly leadingLabel?: string;
  readonly trailingLabel?: string;
};

class MeterMath {
  static percentage(done: number, total: number): number {
    if (total <= 0) return 0;

    return Math.min(100, Math.max(0, (done / total) * 100));
  }
}

export function Meter(props: MeterProps): JSX.Element {
  const width = (): string =>
    `${MeterMath.percentage(props.done, props.total).toFixed(1)}%`;
  const hasLegend = (): boolean =>
    props.leadingLabel !== undefined || props.trailingLabel !== undefined;

  return (
    <div class="meter-block">
      <Show when={hasLegend()}>
        <div class="meter-legend">
          <span>{props.leadingLabel ?? ""}</span>
          <span>{props.trailingLabel ?? ""}</span>
        </div>
      </Show>
      <div class="meter" aria-hidden="true">
        <div class="meter-fill" style={`width: ${width()}`} />
      </div>
    </div>
  );
}
