const PORTFOLIO_STORAGE_KEY = "relinkPortfolios";
const PROFILE_STORAGE_KEY = "relinkProfile";
const DEFAULT_PROFILE_IMAGE = "../../static/assets/icons/profile.svg";

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

function getProfile() {
  try {
    return JSON.parse(localStorage.getItem(PROFILE_STORAGE_KEY)) || {};
  } catch {
    return {};
  }
}

function getPeriod(portfolio) {
  if (portfolio.period) return portfolio.period;
  const start = formatMonth(portfolio.startDate);
  const end = formatMonth(portfolio.endDate);
  return start || end ? `${start}~${end}` : "-";
}

function getPortfolioValue(portfolio, keys, fallback = "-") {
  const key = keys.find((candidate) => portfolio[candidate]);
  return key ? portfolio[key] : fallback;
}

function renderPortfolios(portfolios) {
  const list = document.querySelector(".portfolio-list");
  const emptyState = document.querySelector(".empty-state");
  const addButton = document.querySelector(".floating-add-button");
  const template = document.querySelector("#portfolio-card-template");

  if (!list || !emptyState || !addButton || !template) return;

  if (portfolios.length === 0) {
    emptyState.hidden = false;
    return;
  }

  portfolios.forEach((portfolio, index) => {
    const card = template.content.cloneNode(true);
    card.querySelector("h2").textContent = portfolio.title || "";
    card.querySelector(".project-type").textContent =
      portfolio.projectType || "";
    card.querySelector(".portfolio-period").textContent = getPeriod(portfolio);
    card.querySelector(".portfolio-partner").textContent =
      `파트너: ${portfolio.partnerName || ""}`;
    card.querySelector(".detail-button").addEventListener("click", () => {
      const url = new URL("./portfolio-detail.html", window.location.href);
      url.searchParams.set("index", index);
      window.location.href = url.href;
    });
    list.append(card);
  });

  list.hidden = false;
  addButton.hidden = false;
}

function goBack(fallback) {
  if (history.length > 1) {
    history.back();
    return;
  }

  location.href = fallback;
}

function bindBackButton(fallback) {
  document.querySelector(".back-button")?.addEventListener("click", () => {
    goBack(fallback);
  });
}

function initializeManagePage() {
  if (!document.querySelector(".portfolio-container")) return;
  bindBackButton("./mypage.html");
  renderPortfolios(getPortfolios());
}

function getResultImages(portfolio) {
  const images =
    portfolio.resultImages || portfolio.results || portfolio.outcomes || [];
  if (!Array.isArray(images)) return [];

  return images
    .map((item) => (typeof item === "string" ? item : item?.src || item?.url))
    .filter(Boolean);
}

function getLearnings(portfolio) {
  return getPortfolioValue(
    portfolio,
    ["learnings", "reflection", "takeaways"],
    "",
  );
}

function setFieldValues(portfolio) {
  const values = {
    title: getPortfolioValue(portfolio, ["title", "projectName"]),
    period: getPeriod(portfolio),
    partner: getPortfolioValue(portfolio, ["partnerName", "partner"]),
    type: getPortfolioValue(portfolio, ["projectType", "collaborationType"]),
    overview: getPortfolioValue(portfolio, [
      "overview",
      "description",
      "intro",
    ]),
    role: getPortfolioValue(portfolio, ["role", "myRole", "roles"]),
  };

  Object.entries(values).forEach(([field, value]) => {
    const text = Array.isArray(value) ? value.join("  ") : value;
    document.querySelectorAll(`[data-field="${field}"]`).forEach((element) => {
      element.textContent = text;
    });
  });
}

function createRoleCard({ name, image, role }) {
  const card = document.createElement("article");
  card.className = "role-card";

  const person = document.createElement("div");
  person.className = "role-person";

  const profileImage = document.createElement("img");
  profileImage.src = image || DEFAULT_PROFILE_IMAGE;
  profileImage.alt = `${name} 프로필`;
  profileImage.addEventListener("error", () => {
    profileImage.src = DEFAULT_PROFILE_IMAGE;
  });

  const personName = document.createElement("span");
  personName.textContent = name || "파트너";
  person.append(profileImage, personName);

  const roleCopy = document.createElement("p");
  roleCopy.textContent = Array.isArray(role) ? role.join("\n") : role || "-";
  card.append(person, roleCopy);
  return card;
}

function renderRoles(portfolio) {
  const roleList = document.querySelector(".role-list");
  if (!roleList) return;
  roleList.replaceChildren();

  const savedProfile = getProfile();
  const roles =
    Array.isArray(portfolio.roleDetails) && portfolio.roleDetails.length
      ? portfolio.roleDetails
      : [
          {
            name: savedProfile.name || "나",
            image: savedProfile.image,
            role: getPortfolioValue(portfolio, ["role", "myRole"], "-"),
          },
          {
            name: portfolio.partnerName || "파트너",
            image: portfolio.partnerImage,
            role: getPortfolioValue(
              portfolio,
              ["partnerRole", "partnerRoles"],
              "-",
            ),
          },
        ];

  roles.forEach((role) => roleList.append(createRoleCard(role)));
}

function renderGallery(images) {
  const gallery = document.querySelector(".result-gallery");
  if (!gallery) return;
  gallery.replaceChildren();

  images.forEach((src, index) => {
    const image = document.createElement("img");
    image.src = src;
    image.alt = `성과 및 결과물 ${index + 1}`;
    gallery.append(image);
  });
}

function renderLearnings(learnings) {
  const list = document.querySelector(".learning-list");
  const template = document.querySelector("#learning-item-template");
  if (!list || !template) return;
  list.replaceChildren();

  learnings
    .split(/\n+/)
    .map((line) => line.replace(/^[•●\-]\s*/, "").trim())
    .filter(Boolean)
    .forEach((line) => {
      const item = template.content.cloneNode(true);
      item.querySelector("span").textContent = line;
      list.append(item);
    });
}

let selectedResultImages = [];

function renderInputPreviews() {
  const container = document.querySelector(".result-inputs");
  if (!container) return;
  container.replaceChildren();

  selectedResultImages.forEach((src, index) => {
    const preview = document.createElement("div");
    preview.className = "result-preview";

    const image = document.createElement("img");
    image.src = src;
    image.alt = `추가한 결과물 ${index + 1}`;

    const removeButton = document.createElement("button");
    removeButton.className = "remove-image";
    removeButton.type = "button";
    removeButton.setAttribute("aria-label", `결과물 ${index + 1} 삭제`);
    removeButton.textContent = "×";
    removeButton.addEventListener("click", () => {
      selectedResultImages.splice(index, 1);
      renderInputPreviews();
    });

    preview.append(image, removeButton);
    container.append(preview);
  });
}

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.addEventListener("load", () => resolve(reader.result));
    reader.addEventListener("error", reject);
    reader.readAsDataURL(file);
  });
}

function showEditView(portfolio) {
  document.querySelector(".read-view").hidden = true;
  document.querySelector(".edit-view").hidden = false;
  selectedResultImages = [...getResultImages(portfolio)];

  const textarea = document.querySelector("#learnings");
  textarea.value = getLearnings(portfolio);
  document.querySelector(".text-count").textContent =
    `${textarea.value.length}/200`;
  renderInputPreviews();
}

function showReadView(portfolio) {
  document.querySelector(".edit-view").hidden = true;
  document.querySelector(".read-view").hidden = false;
  renderRoles(portfolio);
  renderGallery(getResultImages(portfolio));
  renderLearnings(getLearnings(portfolio));
}

function initializeDetailPage() {
  if (!document.querySelector(".detail-container")) return;
  bindBackButton("./portfolio-manage.html");

  const portfolios = getPortfolios();
  const index = Number.parseInt(
    new URLSearchParams(window.location.search).get("index"),
    10,
  );
  const portfolio = portfolios[index];

  if (!portfolio) {
    document.querySelector(".not-found").hidden = false;
    return;
  }

  setFieldValues(portfolio);

  const hasCompletedDetail =
    getResultImages(portfolio).length > 0 && getLearnings(portfolio).trim();
  if (hasCompletedDetail) {
    showReadView(portfolio);
  } else {
    showEditView(portfolio);
  }

  const textarea = document.querySelector("#learnings");
  textarea.addEventListener("input", () => {
    document.querySelector(".text-count").textContent =
      `${textarea.value.length}/200`;
  });

  document
    .querySelector(".image-add-box input")
    .addEventListener("change", async (event) => {
      const files = [...event.target.files];
      const images = await Promise.all(files.map(readFileAsDataUrl));
      selectedResultImages.push(...images);
      renderInputPreviews();
      event.target.value = "";
    });

  document
    .querySelector(".portfolio-detail-form")
    .addEventListener("submit", (event) => {
      event.preventDefault();
      const learnings = textarea.value.trim();

      if (selectedResultImages.length === 0 || !learnings) {
        alert("성과 및 결과물과 느낀점/알게된점을 모두 입력해주세요.");
        return;
      }

      portfolio.resultImages = [...selectedResultImages];
      portfolio.learnings = learnings;

      try {
        localStorage.setItem(PORTFOLIO_STORAGE_KEY, JSON.stringify(portfolios));
      } catch {
        alert(
          "이미지 용량이 커서 저장할 수 없어요. 더 작은 이미지를 선택해주세요.",
        );
        return;
      }

      showReadView(portfolio);
    });

  document.querySelector(".cancel-button").addEventListener("click", () => {
    if (getResultImages(portfolio).length && getLearnings(portfolio).trim()) {
      showReadView(portfolio);
      return;
    }
    goBack("./portfolio-manage.html");
  });

  document.querySelector(".edit-button").addEventListener("click", () => {
    showEditView(portfolio);
  });

  document
    .querySelector(".share-button")
    .addEventListener("click", async () => {
      const shareData = {
        title: portfolio.title || "포트폴리오",
        text: `${portfolio.title || "포트폴리오"} 상세 내용을 확인해보세요.`,
        url: window.location.href,
      };

      if (navigator.share) {
        try {
          await navigator.share(shareData);
        } catch (error) {
          if (error.name !== "AbortError") alert("공유하지 못했어요.");
        }
        return;
      }

      await navigator.clipboard.writeText(window.location.href);
      alert("포트폴리오 주소를 복사했어요.");
    });
}

initializeManagePage();
initializeDetailPage();
