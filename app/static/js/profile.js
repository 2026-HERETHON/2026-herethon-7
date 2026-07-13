const form = document.querySelector(".profile-form");

// 프로필 사진
const profileInput = document.querySelector("#profile-image");
const preview = document.querySelector("#profile-preview");

profileInput.addEventListener("change", function () {
  const file = this.files[0];

  if (!file) return;

  preview.src = URL.createObjectURL(file);
});

// 한 줄 소개 글자 수
const intro = document.querySelector("#intro");
const count = document.querySelector(".text-count");

intro.addEventListener("input", () => {
  count.textContent = `${intro.value.length}/50`;
});

// 선택 버튼
document.querySelectorAll(".button-row").forEach((row) => {
  const buttons = row.querySelectorAll(".select-btn");

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      buttons.forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");

      row.closest(".required-group").classList.remove("error");
    });
  });
});

// 프로필 유효성 검사
form.addEventListener("submit", function (e) {
  e.preventDefault();

  let valid = true;

  const nameGroup = document.querySelector(".form-group");
  const nameInput = document.querySelector("#name");

  if (nameInput.value.trim() === "") {
    nameGroup.classList.add("error");
    valid = false;
  } else {
    nameGroup.classList.remove("error");
  }

  // 필수 선택 항목 검사
  document.querySelectorAll(".required-group").forEach((group) => {
    const buttons = group.querySelectorAll(".select-btn");

    if (buttons.length > 0) {
      const selected = [...buttons].some((btn) =>
        btn.classList.contains("active"),
      );

      if (!selected) {
        group.classList.add("error");
        valid = false;
      } else {
        group.classList.remove("error");
      }
    }

    const selectBox = group.querySelector(".select-box");

    if (selectBox) {
      if (selectBox.dataset.selected !== "true") {
        group.classList.add("error");
        valid = false;
      } else {
        group.classList.remove("error");
      }
    }
  });

  if (valid) {
    alert("저장되었습니다.");
    // location.href = "./home.html";
  }
});

// + 버튼 클릭 이벤트(모달)
const overlay = document.querySelector(".sheet-overlay");
const sheet = document.querySelector(".bottom-sheet");

const sheetTitle = document.querySelector(".sheet-title");
const recommendTags = document.querySelector(".recommend-tags");
const selectedTags = document.querySelector(".selected-tags");

let currentBox = null;
let selectedItems = [];
let currentType = "";

const sheetData = {
  provide: {
    title: "제공 가능 역량 (1개 필수) 추가",
    items: ["SNS운영", "AI 활용", "문서 작성", "시장조사", "실무 피드백"],
  },

  need: {
    title: "필요한 역량 (1개 필수) 추가",
    items: [
      "마케팅 전략",
      "실무 보고서 작성",
      "시장조사",
      "실무 피드백",
      "문서 작성",
    ],
  },

  interest: {
    title: "관심분야 추가",
    items: ["마케팅", "기획/제작", "디자인", "경영/회계", "개발"],
  },
};

function openSheet(type, box) {
  currentBox = box;
  currentType = type;

  sheet.classList.remove("hidden");
  overlay.classList.remove("hidden");

  sheetTitle.textContent = sheetData[type].title;

  recommendTags.innerHTML = "";
  selectedTags.innerHTML = "";

  selectedItems = [];

  sheetData[type].items.forEach((item) => {
    createRecommendTag(item);
  });
}

function createRecommendTag(text) {
  const tag = document.createElement("button");

  tag.type = "button";
  tag.className = "tag normal";
  tag.textContent = text;

  tag.onclick = () => {
    if (selectedItems.includes(text)) return;

    selectedItems.push(text);

    createSelectedTag(text);

    tag.classList.remove("normal");
    tag.classList.add("active");
  };

  recommendTags.appendChild(tag);
}

function createSelectedTag(text) {
  const tag = document.createElement("div");

  tag.className = "tag active";

  tag.innerHTML = `
      ${text}
      <span class="remove-tag">✕</span>
  `;

  tag.querySelector(".remove-tag").onclick = () => {
    tag.remove();

    selectedItems = selectedItems.filter((item) => item !== text);

    recommendTags.querySelectorAll(".tag").forEach((recommend) => {
      if (recommend.textContent === text) {
        recommend.classList.remove("active");
        recommend.classList.add("normal");
      }
    });
  };

  selectedTags.appendChild(tag);
}

function closeSheet() {
  sheet.classList.add("hidden");
  overlay.classList.add("hidden");
}

overlay.addEventListener("click", closeSheet);

document.querySelector(".cancel-btn").addEventListener("click", closeSheet);

document
  .querySelector("#provide-group .plus-btn")
  .addEventListener("click", () => {
    openSheet("provide", document.querySelector("#provide-group .select-box"));
  });

document
  .querySelector("#need-group .plus-btn")
  .addEventListener("click", () => {
    openSheet("need", document.querySelector("#need-group .select-box"));
  });

document
  .querySelector("#interest-group .plus-btn")
  .addEventListener("click", () => {
    openSheet(
      "interest",
      document.querySelector("#interest-group .select-box"),
    );
  });

document.querySelector(".add-btn").addEventListener("click", () => {
  if (selectedItems.length === 0) return;

  currentBox.textContent = selectedItems.join(", ");

  currentBox.dataset.selected = "true";

  currentBox.closest(".required-group").classList.remove("error");

  closeSheet();
});

// 검색
const searchInput = document.querySelector("#sheet-search");

searchInput.addEventListener("input", () => {
  const keyword = searchInput.value.toLowerCase();

  recommendTags.querySelectorAll(".tag").forEach((tag) => {
    tag.style.display = tag.textContent.toLowerCase().includes(keyword)
      ? ""
      : "none";
  });
});
