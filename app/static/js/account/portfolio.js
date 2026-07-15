const PORTFOLIO_STORAGE_KEY = "relinkPortfolios";

function getPortfolios() {
  try {
    const portfolios = JSON.parse(localStorage.getItem(PORTFOLIO_STORAGE_KEY));
    return Array.isArray(portfolios) ? portfolios : [];
  } catch {
    return [];
  }
}

function formatMonth(value) {
  if (!value) return "";
  return value.slice(0, 7).replace("-", ".");
}

function renderPortfolios(portfolios) {
  const list = document.querySelector(".portfolio-list");
  const emptyState = document.querySelector(".empty-state");
  const addButton = document.querySelector(".floating-add-button");
  const template = document.querySelector("#portfolio-card-template");

  if (portfolios.length === 0) {
    emptyState.hidden = false;
    return;
  }

  portfolios.forEach((portfolio) => {
    const card = template.content.cloneNode(true);
    card.querySelector("h2").textContent = portfolio.title || "";
    card.querySelector(".project-type").textContent =
      portfolio.projectType || "";
    card.querySelector(".portfolio-period").textContent =
      `${formatMonth(portfolio.startDate)}~${formatMonth(portfolio.endDate)}`;
    card.querySelector(".portfolio-partner").textContent =
      `파트너: ${portfolio.partnerName || ""}`;
    list.append(card);
  });

  list.hidden = false;
  addButton.hidden = false;
}

document.querySelector(".back-button").addEventListener("click", () => {
  if (history.length > 1) {
    history.back();
    return;
  }

  location.href = "./mypage.html";
});

renderPortfolios(getPortfolios());
