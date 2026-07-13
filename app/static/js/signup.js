const form = document.querySelector(".signup-form");

const agreement = document.querySelector(".agreement");
const allCheck = agreement.querySelector(".check-item input[type='checkbox']");
const checks = agreement.querySelectorAll(".check-item input[type='checkbox']");

// 전체동의 클릭 시 모든 체크박스 선택/해제
allCheck.addEventListener("change", () => {
  checks.forEach((checkbox) => {
    checkbox.checked = allCheck.checked;
  });
});

// 전체동의 체크 여부 변경
checks.forEach((checkbox, index) => {
  if (index === 0) return;

  checkbox.addEventListener("change", () => {
    const others = [...checks].slice(1);
    allCheck.checked = others.every((checkbox) => checkbox.checked);
  });
});

// 회원가입 유효성 검사
form.addEventListener("submit", function (e) {
  e.preventDefault();

  let valid = true;

  // 입력필드 검사
  document.querySelectorAll(".form-group").forEach((group) => {
    const input = group.querySelector("input");

    if (input.value.trim() === "") {
      group.classList.add("error");
      valid = false;
    } else {
      group.classList.remove("error");
    }
  });

  // 비밀번호 일치 여부 검사
  const password = document.querySelector("#password");
  const passwordCheck = document.querySelector("#password-check");
  const passwordGroup = passwordCheck.closest(".form-group");
  const passwordError = passwordGroup.querySelector(".error-msg");

  if (
    password.value.trim() !== "" &&
    passwordCheck.value.trim() !== "" &&
    password.value !== passwordCheck.value
  ) {
    passwordGroup.classList.add("error");
    passwordError.textContent = "비밀번호가 일치하지 않습니다.";
    valid = false;
  } else {
    passwordError.textContent = "필수 항목을 입력하세요.";
  }

  // 필수 약관동의 여부 검사
  const requiredChecks = agreement.querySelectorAll(".required-check");

  const requiredChecked = [...requiredChecks].every(
    (checkbox) => checkbox.checked,
  );

  if (!requiredChecked) {
    agreement.classList.add("error");
    valid = false;
  } else {
    agreement.classList.remove("error");
  }

  // 모든 검사 통과 시 폼 제출 및 로그인 페이지로 이동
  if (valid) {
    form.submit();
    window.location.href = "./complete.html";
  }
});
