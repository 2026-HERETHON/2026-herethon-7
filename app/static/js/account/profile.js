const form = document.querySelector(".profile-form");
const profileInput = document.querySelector("#profile-image");
const preview = document.querySelector("#profile-preview");
const intro = document.querySelector("#intro");
const count = document.querySelector(".text-count");

profileInput.addEventListener("change", function () {
  const file = this.files[0];
  if (!file) return;

  preview.src = URL.createObjectURL(file);
  preview.classList.add("uploaded");
  preview.parentElement.classList.add("uploaded");
});

if (!preview.src.includes("profile.svg")) {
  preview.classList.add("uploaded");
  preview.parentElement.classList.add("uploaded");
}

function updateIntroCount() {
  count.textContent = `${intro.value.length}/50`;
}

intro.addEventListener("input", updateIntroCount);
updateIntroCount();

document.querySelectorAll(".button-row").forEach((row) => {
  const buttons = row.querySelectorAll(".select-btn");

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      buttons.forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      row.closest(".required-group").classList.remove("error");
    });
  });
});

function getTalentOptions(type) {
  return [
    ...document.querySelectorAll(
      `#talent-fields [data-type="${type}"] input`,
    ),
  ].map((input) => ({
    id: input.value,
    name: input.closest("label")?.textContent.trim() || input.value,
    input,
  }));
}

const talentOptions = {
  provide: getTalentOptions("provide"),
  need: getTalentOptions("need"),
};

const selectedData = {
  provide: talentOptions.provide.filter((item) => item.input.checked),
  need: talentOptions.need.filter((item) => item.input.checked),
  interest: (form.dataset.savedSkills || "")
    .split(",")
    .map((name) => name.trim())
    .filter(Boolean)
    .map((name) => ({ id: name, name })),
};

const interestOptions = ["마케팅", "기획/제작", "디자인", "경영/회계", "개발"].map(
  (name) => ({ id: name, name }),
);

function fillSelectedBox(type) {
  const box = document.querySelector(`#${type}-group .select-box`);
  const items = selectedData[type];

  box.innerHTML = "";
  box.classList.toggle("has-items", items.length > 0);
  box.dataset.selected = items.length > 0 ? "true" : "false";

  if (items.length === 0) {
    box.textContent =
      type === "interest"
        ? "아직 선택된 관심분야가 없습니다."
        : "아직 선택된 역량이 없습니다.";
    return;
  }

  items.forEach((item) => {
    const chip = document.createElement("span");
    chip.className = "selected-chip";
    chip.textContent = item.name;
    box.appendChild(chip);
  });
}

["provide", "need", "interest"].forEach(fillSelectedBox);

function selectSavedButton(groupSelector, value) {
  if (!value) return;

  document
    .querySelectorAll(`${groupSelector} .select-btn`)
    .forEach((button) => {
      button.classList.toggle("active", button.dataset.value === value);
    });
}

selectSavedButton("#career-group", form.dataset.savedIdentity);
selectSavedButton("#work-group", form.dataset.savedWorkStyle);

const overlay = document.querySelector(".sheet-overlay");
const sheet = document.querySelector(".bottom-sheet");
const sheetTitle = document.querySelector(".sheet-title");
const recommendTags = document.querySelector(".recommend-tags");
const selectedTags = document.querySelector(".selected-tags");
const searchInput = document.querySelector("#sheet-search");

let currentType = "";
let selectedItems = [];

function itemExists(items, target) {
  return items.some((item) => item.id === target.id);
}

function optionsFor(type) {
  return type === "interest" ? interestOptions : talentOptions[type];
}

function titleFor(type) {
  if (type === "provide") return "제공 가능 역량 (1개 필수) 추가";
  if (type === "need") return "필요한 역량 (1개 필수) 추가";
  return "관심분야 추가";
}

function createSelectedTag(item) {
  const tag = document.createElement("div");
  const remove = document.createElement("span");

  tag.className = "tag active";
  tag.append(document.createTextNode(item.name));
  remove.className = "remove-tag";
  remove.textContent = "✕";
  tag.appendChild(remove);

  remove.addEventListener("click", () => {
    selectedItems = selectedItems.filter(
      (selected) => selected.id !== item.id,
    );
    renderSheet();
  });

  selectedTags.appendChild(tag);
}

function createRecommendTag(item) {
  const tag = document.createElement("button");
  tag.type = "button";
  tag.className = itemExists(selectedItems, item)
    ? "tag active"
    : "tag normal";
  tag.textContent = item.name;

  tag.addEventListener("click", () => {
    if (!itemExists(selectedItems, item)) {
      selectedItems.push(item);
      renderSheet();
    }
  });

  recommendTags.appendChild(tag);
}

function renderSheet() {
  selectedTags.innerHTML = "";
  recommendTags.innerHTML = "";
  selectedItems.forEach(createSelectedTag);
  optionsFor(currentType).forEach(createRecommendTag);
  searchInput.dispatchEvent(new Event("input"));
}

function openSheet(type) {
  currentType = type;
  selectedItems = [...selectedData[type]];
  sheetTitle.textContent = titleFor(type);
  searchInput.value = "";
  renderSheet();
  sheet.classList.remove("hidden");
  overlay.classList.remove("hidden");
}

function closeSheet() {
  sheet.classList.add("hidden");
  overlay.classList.add("hidden");
}

overlay.addEventListener("click", closeSheet);
document.querySelector(".cancel-btn").addEventListener("click", closeSheet);

document
  .querySelector("#provide-group .plus-btn")
  .addEventListener("click", () => openSheet("provide"));
document
  .querySelector("#need-group .plus-btn")
  .addEventListener("click", () => openSheet("need"));
document
  .querySelector("#interest-group .plus-btn")
  .addEventListener("click", () => openSheet("interest"));

document.querySelector(".add-btn").addEventListener("click", () => {
  const customInterest = searchInput.value.trim();

  if (
    currentType === "interest" &&
    customInterest &&
    !itemExists(selectedItems, { id: customInterest })
  ) {
    selectedItems.push({ id: customInterest, name: customInterest });
  }

  if (selectedItems.length === 0) return;

  selectedData[currentType] = [...selectedItems];
  fillSelectedBox(currentType);
  document
    .querySelector(`#${currentType}-group`)
    .classList.remove("error");
  closeSheet();
});

searchInput.addEventListener("input", () => {
  const keyword = searchInput.value.toLowerCase();

  recommendTags.querySelectorAll(".tag").forEach((tag) => {
    tag.style.display = tag.textContent.toLowerCase().includes(keyword)
      ? ""
      : "none";
  });
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  let valid = true;

  const nameInput = document.querySelector("#name");
  const nameGroup = nameInput.closest(".form-group");
  nameGroup.classList.toggle("error", nameInput.value.trim() === "");
  if (nameInput.value.trim() === "") valid = false;

  document.querySelectorAll(".required-group").forEach((group) => {
    const hasButton = group.querySelector(".select-btn");
    const box = group.querySelector(".select-box");
    const missing =
      (hasButton && !group.querySelector(".select-btn.active")) ||
      (box && box.dataset.selected !== "true");

    group.classList.toggle("error", Boolean(missing));
    if (missing) valid = false;
  });

  if (!valid) return;

  document.querySelector("#identity").value = document.querySelector(
    "#career-group .select-btn.active",
  ).dataset.value;
  document.querySelector("#work-style").value = document.querySelector(
    "#work-group .select-btn.active",
  ).dataset.value;
  document.querySelector("#skills").value = selectedData.interest
    .map((item) => item.name)
    .join(",");

  ["provide", "need"].forEach((type) => {
    const selectedIds = new Set(selectedData[type].map((item) => item.id));
    talentOptions[type].forEach((item) => {
      item.input.checked = selectedIds.has(item.id);
    });
  });

  form.querySelector(".save-btn").disabled = true;
  form.submit();
});
