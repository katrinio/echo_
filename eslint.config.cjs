module.exports = [
  {
    files: ["src/static/js/**/*.js"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        window: "readonly",
        document: "readonly",
      },
    },
    rules: {
      "no-unused-vars": ["error", { args: "none" }],
    },
  },
];
