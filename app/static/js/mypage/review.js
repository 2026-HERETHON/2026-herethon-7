const emptyStateCopy = {
  received: {
    title: "아직 받은 후기가 없어요.",
    description: "협업이 끝나면 파트너가 후기를\n남길 수 있어요.",
  },
  written: {
    title: "아직 작성한 후기가 없어요.",
    description: "협업이 끝난 파트너에게 후기를\n남겨보세요.",
  },
};

function renderEmptyState(type) {
  const emptyState = document.querySelector(".empty-state");
  const copy = emptyStateCopy[type];
  const lines = copy.description.split("\n");

  emptyState.querySelector("h2").textContent = copy.title;
  emptyState.querySelector("p").replaceChildren();
  lines.forEach((line, index) => {
    if (index > 0)
      emptyState.querySelector("p").append(document.createElement("br"));
    emptyState.querySelector("p").append(line);
  });
}

function renderReviews(type) {
  const emptyState = document.querySelector(".empty-state");
  const reviewList = document.querySelector(".review-list");
  const cards = reviewList.querySelectorAll(".review-card");
  let visibleCount = 0;

  cards.forEach((card) => {
    const isVisible = card.dataset.reviewType === type;
    card.hidden = !isVisible;
    if (isVisible) visibleCount += 1;
  });

  renderEmptyState(type);
  emptyState.hidden = visibleCount > 0;
  reviewList.hidden = visibleCount === 0;
}

function selectTab(selectedTab) {
  const type = selectedTab.dataset.reviewType;
  const content = document.querySelector("#review-content");

  document.querySelectorAll(".review-tab").forEach((tab) => {
    const isSelected = tab === selectedTab;
    tab.classList.toggle("active", isSelected);
    tab.setAttribute("aria-selected", String(isSelected));
  });

  content.setAttribute("aria-labelledby", selectedTab.id);
  renderReviews(type);
}

function initializeReviewPage() {
  const backButton = document.querySelector(".back-button");
  backButton?.addEventListener("click", () => {
    if (history.length > 1) {
      history.back();
      return;
    }
    location.href = backButton.dataset.backUrl || "/mypage/";
  });

  document.querySelectorAll(".review-tab").forEach((tab) => {
    tab.addEventListener("click", () => selectTab(tab));
  });

  renderReviews("received");
}

initializeReviewPage();
