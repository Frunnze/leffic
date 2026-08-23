import type { IconName } from "../../shared/ui/icons/icon-shapes";

type UnitDefinition = {
  readonly deleteEndpoint: string;
  readonly hrefPrefix: string;
  readonly icon: IconName;
};

export const UNIT_DEFINITIONS = {
  folder: {
    deleteEndpoint: "/api/content/delete-folder/?folder_id=",
    hrefPrefix: "/folder",
    icon: "folder",
  },
  flashcard_deck: {
    deleteEndpoint: "/api/content/delete-deck/?deck_id=",
    hrefPrefix: "/flashcard_deck",
    icon: "flashcards",
  },
  test: {
    deleteEndpoint: "/api/content/delete-test/?test_id=",
    hrefPrefix: "/test",
    icon: "test",
  },
  note: {
    deleteEndpoint: "/api/content/delete-note/?note_id=",
    hrefPrefix: "/note",
    icon: "note",
  },
  file: {
    deleteEndpoint: "/api/content/delete-file/?file_id=",
    hrefPrefix: "/file",
    icon: "file",
  },
} as const satisfies Readonly<Record<string, UnitDefinition>>;

export type UnitType = keyof typeof UNIT_DEFINITIONS;

export const UNIT_TYPES = Object.keys(UNIT_DEFINITIONS) as readonly UnitType[];
