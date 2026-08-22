import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@solidjs/testing-library";
import fc from "fast-check";
import { Icon } from "../src/shared/ui/icons/Icon";
import { ICONS } from "../src/shared/ui/icons/icon-shapes";
import { Meter } from "../src/shared/ui/Meter";
import { ModalFoot } from "../src/shared/ui/ModalFoot";
import { ModalHead } from "../src/shared/ui/ModalHead";
import { ICON_NAME, LABEL, meterWidth } from "./shared-ui-support";

describe("Icon", () => {
  it("draws every icon the app knows", () => {
    fc.assert(
      fc.property(ICON_NAME, (name) => {
        const { unmount } = render(() => <Icon name={name} />);

        expect(document.querySelector("svg")?.getAttribute("viewBox")).toBe(
          ICONS[name].viewBox,
        );
        unmount();
      }),
    );
  });

  it("hides a decorative icon from a screen reader", () => {
    render(() => <Icon name="folder" />);
    const drawn = document.querySelector("svg");

    expect(drawn?.getAttribute("role")).toBe("presentation");
    expect(drawn?.getAttribute("aria-hidden")).toBe("true");
    expect(drawn?.getAttribute("class")).toBe("icon");
  });

  it("announces an icon that carries a title", () => {
    render(() => <Icon name="folder" size="lg" title="Folder" />);
    const drawn = document.querySelector("svg");

    expect(drawn?.getAttribute("role")).toBe("img");
    expect(drawn?.getAttribute("aria-label")).toBe("Folder");
    expect(drawn?.getAttribute("class")).toBe("icon-lg");
  });
});

describe("MeterMath.percentage", () => {
  it("percentage property never fills past the whole bar", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 500 }),
        fc.integer({ min: 1, max: 500 }),
        (done, total) => {
          const { unmount } = render(() => <Meter done={done} total={total} />);
          const filled = meterWidth();

          expect(filled).toBeGreaterThanOrEqual(0);
          expect(filled).toBeLessThanOrEqual(100);
          unmount();
        },
      ),
    );
  });

  it("percentage property shows nothing done when nothing is countable", () => {
    fc.assert(
      fc.property(fc.integer({ min: -50, max: 0 }), (total) => {
        const { unmount } = render(() => <Meter done={5} total={total} />);

        expect(meterWidth()).toBe(0);
        unmount();
      }),
    );
  });

  it("percentage property never falls below an empty bar", () => {
    fc.assert(
      fc.property(fc.integer({ min: -50, max: -1 }), (done) => {
        const { unmount } = render(() => <Meter done={done} total={10} />);

        expect(meterWidth()).toBe(0);
        unmount();
      }),
    );
  });
});

describe("Meter", () => {
  it("fills to the share that is done", () => {
    render(() => <Meter done={1} total={4} />);

    expect(meterWidth()).toBe(25);
  });

  it("shows no legend when neither side is labelled", () => {
    render(() => <Meter done={1} total={4} />);

    expect(document.querySelector(".meter-legend")).toBeNull();
  });

  it("labels the leading side alone", () => {
    render(() => <Meter done={1} total={4} leadingLabel="1 of 4" />);

    expect(document.querySelector(".meter-legend")?.textContent).toBe("1 of 4");
  });

  it("labels both sides of the legend", () => {
    render(() => (
      <Meter done={1} total={4} leadingLabel="1 of 4" trailingLabel="25%" />
    ));

    expect(document.querySelector(".meter-legend")?.textContent).toBe(
      "1 of 425%",
    );
  });

  it("labels the trailing side alone", () => {
    render(() => <Meter done={1} total={4} trailingLabel="25%" />);

    expect(document.querySelector(".meter-legend")?.textContent).toBe("25%");
  });
});

describe("ModalFoot", () => {
  it("names the confirm button whatever the dialog asked for", () => {
    fc.assert(
      fc.property(LABEL, (confirmLabel) => {
        const { unmount } = render(() => (
          <ModalFoot
            confirmLabel={confirmLabel}
            isConfirmBlocked={false}
            onCancel={() => undefined}
          />
        ));

        expect(
          screen.getByRole("button", { name: confirmLabel }),
        ).toHaveProperty("disabled", false);
        unmount();
      }),
    );
  });

  it("cancels when the cancel button is pressed", () => {
    const onCancel = vi.fn();
    render(() => (
      <ModalFoot
        confirmLabel="Save"
        isConfirmBlocked={false}
        onCancel={onCancel}
      />
    ));

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("blocks the confirm button when the dialog is incomplete", () => {
    render(() => (
      <ModalFoot
        confirmLabel="Save"
        isConfirmBlocked
        onCancel={() => undefined}
      />
    ));

    expect(screen.getByRole("button", { name: "Save" })).toHaveProperty(
      "disabled",
      true,
    );
  });
});

describe("ModalHead", () => {
  it("shows the title and description it was given", () => {
    render(() => (
      <ModalHead
        title="Move it"
        description="Pick a folder"
        onClose={() => undefined}
      />
    ));

    expect(screen.getByRole("heading", { name: "Move it" })).toBeTruthy();
    expect(document.querySelector(".modal-text")?.textContent).toBe(
      "Pick a folder",
    );
  });

  it("closes when the close button is pressed", () => {
    const onClose = vi.fn();
    render(() => <ModalHead title="t" description="d" onClose={onClose} />);

    fireEvent.click(screen.getByRole("button", { name: "Close dialog" }));

    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
