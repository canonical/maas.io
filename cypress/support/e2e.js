import "@testing-library/cypress/add-commands";

Cypress.on("uncaught:exception", (_err, _runnable) => {
    return false;
});
