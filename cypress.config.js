const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    baseUrl: "https://maas.io/",
    specPattern: "cypress/e2e/**/*.{js,jsx,ts,tsx}",
  },
});
