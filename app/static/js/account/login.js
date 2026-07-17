const form = document.querySelector(".login-form");
const loginErrorMsg = form.querySelector(".login-error-msg");
const emailGroup = form.querySelectorAll(".form-group")[0];
const passwordGroup = form.querySelectorAll(".form-group")[1];
const emailInput = emailGroup.querySelector("input");
const passwordInput = passwordGroup.querySelector("input");
const emailError = emailGroup.querySelector(".error-msg");
const passwordError = passwordGroup.querySelector(".error-msg");

function clearFieldErrors() {
  emailGroup.classList.remove("error");
  passwordGroup.classList.remove("error");
  loginErrorMsg.classList.remove("show");
}

form.addEventListener("submit", function (e) {
  e.preventDefault();

  let valid = true;
  clearFieldErrors();

  // 이메일 검증
  if (emailInput.value.trim() === "") {
    emailGroup.classList.add("error");
    emailError.textContent = "필수 항목을 입력하세요.";
    valid = false;
  } else if (!emailInput.checkValidity()) {
    emailGroup.classList.add("error");
    emailError.textContent = "올바른 이메일 형식을 입력하세요.";
    valid = false;
  }

  // 비밀번호 검증
  if (passwordInput.value.trim() === "") {
    passwordGroup.classList.add("error");
    passwordError.textContent = "필수 항목을 입력하세요.";
    valid = false;
  }

  if (valid) {
    form.submit();
  }
});

if (form.dataset.loginError === "true") {
  loginErrorMsg.classList.add("show");
}
