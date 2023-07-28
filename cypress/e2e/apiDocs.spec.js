
context("/docs/api", () => {
  beforeEach(() => {
    cy.setCookie("_cookies_accepted", "all");
    cy.visit("/docs/api");
  });

  it("displays side navigation correctly", () => {
    cy.get(".p-side-navigation__drawer").should("not.be.visible");
    cy.findAllByRole("link", { name: /Toggle side navigation/ }).first().click();
    cy.get(".p-side-navigation__drawer").should("be.visible");
    cy.get(".p-side-navigation__drawer")
      .findAllByRole("link")
      .should("have.length.least", 1);
  });

  it("displays content correctly", () => {
    cy.findByRole("heading", { level: 1, name: "MAAS API" }).should("exist");
    cy.findByRole("heading", { level: 2, name: "Operations" }).should("exist");
  });
});
