import { describe, expect, it } from "vitest";
import fc from "fast-check";
import { render } from "@solidjs/testing-library";
import { ImportSource } from "../src/features/folder/import/ImportSource";
import { PAGED_EXTENSIONS } from "../src/features/folder/import/import-options";
import { SourceKindHandlers } from "../src/features/folder/import/source-kind-handlers";
import { NO_SOURCE_PROPS, sourceHandlers } from "./import-views-support";

describe("ImportSource properties", () => {
  it("options property exposes every selectable source kind once", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("file", "link", "text", "topic" as const),
        (kind) => {
          const matching = SourceKindHandlers.options().filter(
            (option) => option.kind === kind,
          );

          expect(matching).toHaveLength(1);
          expect(matching[0]?.label).not.toBe("");
        },
      ),
    );
  });

  it("filePanel property shows every chosen file name", () => {
    const fileStem = fc
      .array(fc.constantFrom("a", "b", "c", "1", "2"), {
        minLength: 1,
        maxLength: 12,
      })
      .map((characters) => characters.join(""));

    fc.assert(
      fc.property(fileStem, (stem) => {
        const filename = `${stem}.txt`;
        const shown = render(() => (
          <ImportSource
            {...NO_SOURCE_PROPS}
            chosenFile={new File(["x"], filename)}
            {...sourceHandlers()}
          />
        ));

        expect(
          shown.container.querySelector(".chosen-file-name")?.textContent,
        ).toBe(filename);
        shown.unmount();
      }),
    );
  });

  it("isPaged property offers a range for every paged extension", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: PAGED_EXTENSIONS.length - 1 }),
        (index) => {
          const extension = PAGED_EXTENSIONS[index];

          expect(extension).toBeDefined();
          if (extension === undefined) return;

          const shown = render(() => (
            <ImportSource
              {...NO_SOURCE_PROPS}
              chosenFile={new File(["x"], `notes.${extension}`)}
              {...sourceHandlers()}
            />
          ));

          expect(
            shown.container.querySelector('[aria-label="First page"]'),
          ).not.toBeNull();
          shown.unmount();
        },
      ),
    );
  });
});
