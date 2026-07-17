const PROFILE_STORAGE_KEY = "relinkProfile";

function getSavedProfile() {
  try {
    return JSON.parse(localStorage.getItem(PROFILE_STORAGE_KEY));
  } catch {
    return null;
  }
}

function ensureCareerElement(profileCopy, emptyMessage) {
  let career = document.querySelector("#profile-career");

  if (career) return career;

  career = document.createElement("p");
  career.className = "profile-career";
  career.id = "profile-career";

  if (emptyMessage) {
    emptyMessage.replaceWith(career);
  } else {
    profileCopy.appendChild(career);
  }

  return career;
}

function renderProfile(profile) {
  if (!profile?.name) return;

  const profileImage = document.querySelector("#profile-image");
  const profileName = document.querySelector("#profile-name");
  const profileCopy = document.querySelector(".profile-copy");
  const emptyMessage = document.querySelector(".profile-empty-message");

  profileName.textContent = profile.name;

  const career = ensureCareerElement(profileCopy, emptyMessage);
  career.textContent = profile.career || "프로필 등록 완료";
  career.hidden = false;

  if (profile.image && profileImage) {
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
