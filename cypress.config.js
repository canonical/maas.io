const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    blockHosts: [
      "www.googletagmanager.com",
      "www.google-analytics.com",
      "sentry.is.canonical.com",
    ],
    baseUrl: "https://maas.io/",
    specPattern: "cypress/e2e/**/*.{js,jsx,ts,tsx}",
    pageLoadTimeout: 15000,
  },
});
