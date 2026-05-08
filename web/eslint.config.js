import js from "@eslint/js";
import globals from "globals";

import pluginPrettier from "eslint-plugin-prettier";
import configPrettier from "eslint-config-prettier";

import html from "@html-eslint/eslint-plugin";

import { defineConfig, globalIgnores } from "eslint/config";

export default defineConfig([

  globalIgnores([
    "node_modules",
    "dist",
    ".cache",
    "coverage"
  ]),

  // ------------------------
  // JAVASCRIPT
  // ------------------------
  {
    files: ["**/*.js"],

    plugins: {
      prettier: pluginPrettier,
      html
    },

    extends: [
      js.configs.recommended,
      configPrettier
    ],

    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.browser,
        ...globals.es2021
      }
    },

    rules: {
      "prettier/prettier": "error",

      // HTML dentro de template literals
      "html/require-img-alt": "error",

      "no-console": "off",
      "no-unused-vars": ["warn", {
        argsIgnorePattern: "^_"
      }],
      "no-undef": "error",
      "no-shadow": "error",
      "no-magic-numbers": ["warn", {
        ignore: [0, 1, -1]
      }]
    }
  },

  // ------------------------
  // HTML
  // ------------------------
  {
    files: ["**/*.html"],

    plugins: {
      html,
      prettier: pluginPrettier
    },

    language: "html/html",

    extends: [
      "html/recommended",
      configPrettier
    ],

    languageOptions: {
      templateEngineSyntax: {
        "{{": "}}"
      }
    },

    rules: {
      "prettier/prettier": "error",

      "html/require-img-alt": "error",
      "html/no-duplicate-class": "error"
    }
  }
]);