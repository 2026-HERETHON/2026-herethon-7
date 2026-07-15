const PROFILE_STORAGE_KEY = "relinkProfile";

function getSavedProfile() {
  try {
    return JSON.parse(localStorage.getItem(PROFILE_STORAGE_KEY));
  } catch {
    return null;
  }
}

function renderProfile(profile) {
  if (!profile?.name) return;

  const profileImage = document.querySelector("#profile-image");
  const emptyMessage = document.querySelector(".profile-empty-message");
  const career = document.querySelector("#profile-career");

  document.querySelector("#profile-name").textContent = profile.name;
  emptyMessage.hidden = true;

  career.textContent = profile.career || "프로필 등록 완료";
  career.hidden = false;

  if (profile.image) {
    profileImage.src = profile.image;
    profileImage.classList.add("uploaded");
  }

  const counts = profile.counts || {};
  document.querySelector("#project-count").textContent = counts.projects ?? 0;
  document.querySelector("#collaboration-count").textContent =
    counts.collaborations ?? 0;
  document.querySelector("#review-count").textContent = counts.reviews ?? 0;
}

renderProfile(getSavedProfile());
