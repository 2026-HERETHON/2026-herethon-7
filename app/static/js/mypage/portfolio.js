function goBack(fallback) {
  if (history.length > 1) {
    history.back();
    return;
  }

  location.href = fallback;
}

function initializeManagePage() {
  if (!document.querySelector(".portfolio-container")) return;

  document.querySelector(".back-button")?.addEventListener("click", () => {
    goBack("/mypage/");
  });

  document.querySelectorAll(".detail-button").forEach((button) => {
    button.addEventListener("click", () => {
      if (button.dataset.detailUrl) location.href = button.dataset.detailUrl;
    });
  });

  document
    .querySelectorAll(".floating-add-button, .empty-add-btn")
    .forEach((button) => {
      button.addEventListener("click", () => {
        location.href = button.dataset.addUrl || "/projects/";
      });
    });
}

function createImagePreview(src, isExisting = false) {
  const preview = document.createElement("div");
  preview.className = "result-preview";

  const image = document.createElement("img");
  image.src = src;
  image.alt = "추가한 결과물";
  preview.append(image);

  if (!isExisting) {
    const removeButton = document.createElement("button");
    removeButton.className = "remove-image";
    removeButton.type = "button";
    removeButton.setAttribute("aria-label", "결과물 삭제");
    removeButton.textContent = "×";
    removeButton.addEventListener("click", () => {
      const fileInput = document.querySelector(
        '.image-add-box input[name="file_path"]',
      );
      fileInput.value = "";
      preview.remove();
    });
    preview.append(removeButton);
  }

  return preview;
}

function initializeDetailPage() {
  if (!document.querySelector(".detail-container")) return;

  document.querySelector(".back-button")?.addEventListener("click", () => {
    goBack("/mypage/portfolio/");
  });

  const textarea = document.querySelector("#learnings");
  const textCount = document.querySelector(".text-count");
  textarea?.addEventListener("input", () => {
    textCount.textContent = `${textarea.value.length}/200`;
  });

  const previewContainer = document.querySelector(".result-inputs");
  const existingImage = previewContainer?.dataset.existingImage;
  if (existingImage) {
    previewContainer.append(createImagePreview(existingImage, true));
  }

  const fileInput = document.querySelector(
    '.image-add-box input[name="file_path"]',
  );
  fileInput?.addEventListener("change", () => {
    previewContainer.replaceChildren();
    const [file] = fileInput.files;
    if (file) {
      previewContainer.append(createImagePreview(URL.createObjectURL(file)));
    } else if (existingImage) {
      previewContainer.append(createImagePreview(existingImage, true));
    }
  });

  document.querySelector(".cancel-button")?.addEventListener("click", () => {
    const readView = document.querySelector(".read-view");
    if (existingImage && textarea.value.trim()) {
      document.querySelector(".edit-view").hidden = true;
      readView.hidden = false;
      return;
    }
    goBack("/mypage/portfolio/");
  });

  document.querySelector(".edit-button")?.addEventListener("click", () => {
    document.querySelector(".read-view").hidden = true;
    document.querySelector(".edit-view").hidden = false;
  });

  document.querySelector(".share-button")?.addEventListener("click", async () => {
    const title =
      document.querySelector('.read-view [data-field="title"]')?.textContent ||
      "포트폴리오";
    const shareData = {
      title,
      text: `${title} 상세 내용을 확인해보세요.`,
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
