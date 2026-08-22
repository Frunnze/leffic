import { solidPreset, typescriptConfigFor } from "../hooks/eslint-config.mjs";

const TRUSTED_HTML_FILES = [
  "src/features/notes/NotePage.tsx",
  "src/shared/ui/icons/Icon.tsx",
];

export default [
  ...typescriptConfigFor(import.meta.dirname, [solidPreset]),
  {
    rules: {
      "solid/reactivity": ["error", { customReactiveFunctions: ["watch"] }],
      "solid/style-prop": "off",
    },
  },
  {
    files: TRUSTED_HTML_FILES,
    rules: { "solid/no-innerhtml": "off" },
  },
];
