import js from "@eslint/js";
import globals from "globals";
import pluginPrettier from "eslint-plugin-prettier";
import configPrettier from "eslint-config-prettier";
import { defineConfig, globalIgnores } from "eslint/config";

export default defineConfig([
  globalIgnores([
    "node_modules",
    "dist",
    ".cache",
    "coverage"
  ]),

  {
    files: ["**/*.js"],
    plugins: {
      prettier: pluginPrettier
    },

    extends: [
      js.configs.recommended,
      configPrettier
    ],

    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.node,
        ...globals.es2021,
        Bun: "readonly"
      }
    },

    rules: {
      "prettier/prettier": "error",

      "no-console": "off",
      "no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
      "no-undef": "error",
      "no-shadow": "error",

      "eqeqeq": ["error", "always"],
      "consistent-return": "warn",

      "indent": ["error", 2],
      "quotes": ["error", "double"],
      "semi": ["error", "always"],

      "max-len": ["warn", { code: 120 }],
      "no-magic-numbers": ["warn", { ignore: [0, 1, -1] }]
    }
  }
]);