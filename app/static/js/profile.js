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

// + 버튼 클릭 이벤트
document.querySelectorAll(".select-box-row").forEach((row) => {
  const plusBtn = row.querySelector(".plus-btn");
  const box = row.querySelector(".select-box");

  plusBtn.addEventListener("click", () => {
    const value = prompt("항목을 입력하세요.");

    if (!value) return;

    box.textContent = value;
    box.dataset.selected = "true";

    row.closest(".required-group").classList.remove("error");
  });
});
