const REVIEW_STORAGE_KEY = "relinkReviews";
const RECEIVED_REVIEW_STORAGE_KEY = "relinkReceivedReviews";
const WRITTEN_REVIEW_STORAGE_KEY = "relinkWrittenReviews";
const DEFAULT_PROFILE_IMAGE = "../../static/assets/icons/profile.svg";

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

function parseStoredArray(key) {
  try {
    const value = JSON.parse(localStorage.getItem(key));
    return Array.isArray(value) ? value : [];
  } catch {
    return [];
  }
}

function getReviews(type) {
  const typedReviews = parseStoredArray(
    type === "received"
      ? RECEIVED_REVIEW_STORAGE_KEY
      : WRITTEN_REVIEW_STORAGE_KEY,
  );

  if (typedReviews.length > 0) return typedReviews;

  return parseStoredArray(REVIEW_STORAGE_KEY).filter(
    (review) => (review.type || "received") === type,
  );
}

function getReviewValue(review, keys, fallback = "") {
  const key = keys.find((candidate) => review[candidate]);
  return key ? review[key] : fallback;
}

function createReviewCard(review, index) {
  const template = document.querySelector("#review-card-template");
  const card = template.content.cloneNode(true);
  const name = getReviewValue(
    review,
    ["name", "reviewerName", "partnerName", "author"],
    "파트너",
  );
  const image = getReviewValue(review, [
    "image",
    "profileImage",
    "reviewerImage",
    "partnerImage",
  ]);

  const profileImage = card.querySelector(".reviewer-image");
  profileImage.src = image || DEFAULT_PROFILE_IMAGE;
  profileImage.alt = `${name} 프로필`;
  profileImage.addEventListener("error", () => {
    profileImage.src = DEFAULT_PROFILE_IMAGE;
  });

  card.querySelector(".reviewer-name").textContent = name;
  card.querySelector(".review-period").textContent = getReviewValue(
    review,
    ["period", "projectPeriod"],
    "-",
  );
  card.querySelector(".review-project").textContent = getReviewValue(
    review,
    ["project", "projectName", "title"],
    "-",
  );
  card.querySelector(".review-body").textContent = getReviewValue(
    review,
    ["content", "review", "body", "message"],
    "",
  );
  card
    .querySelector(".review-card")
    .setAttribute("aria-label", `${name}의 후기 ${index + 1}`);

  return card;
}

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
  const reviews = getReviews(type);
  const emptyState = document.querySelector(".empty-state");
  const reviewList = document.querySelector(".review-list");

  reviewList.replaceChildren();
  renderEmptyState(type);

  if (reviews.length === 0) {
    emptyState.hidden = false;
    reviewList.hidden = true;
    return;
  }

  reviews.forEach((review, index) => {
    reviewList.append(createReviewCard(review, index));
  });
  emptyState.hidden = true;
  reviewList.hidden = false;
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
  document.querySelector(".back-button")?.addEventListener("click", () => {
    if (history.length > 1) {
      history.back();
      return;
    }
    location.href = "./mypage.html";
  });

  document.querySelectorAll(".review-tab").forEach((tab) => {
    tab.addEventListener("click", () => selectTab(tab));
  });

  renderReviews("received");
}

initializeReviewPage();
