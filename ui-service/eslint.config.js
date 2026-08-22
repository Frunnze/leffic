import eslint from "@eslint/js";
import solid from "eslint-plugin-solid/configs/typescript";
import typescriptEslint from "typescript-eslint";

const TRUSTED_HTML_FILES = [
  "src/features/notes/NotePage.tsx",
  "src/shared/ui/icons/Icon.tsx",
];

export default typescriptEslint.config(
  eslint.configs.recommended,
  typescriptEslint.configs.strictTypeChecked,
  typescriptEslint.configs.stylisticTypeChecked,
  solid,
  {
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      "@typescript-eslint/consistent-type-definitions": ["error", "type"],
      "@typescript-eslint/dot-notation": [
        "error",
        { allowIndexSignaturePropertyAccess: true },
      ],
      "@typescript-eslint/no-extraneous-class": "off",
      "@typescript-eslint/restrict-template-expressions": [
        "error",
        { allowNumber: true },
      ],
      "@typescript-eslint/unbound-method": ["error", { ignoreStatic: true }],
      "solid/reactivity": ["error", { customReactiveFunctions: ["watch"] }],
      "solid/style-prop": "off",
    },
  },
  {
    files: TRUSTED_HTML_FILES,
    rules: { "solid/no-innerhtml": "off" },
  },
);
