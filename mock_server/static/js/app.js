document.addEventListener("DOMContentLoaded", () => {
  initFormLoading();
  initDeleteConfirmation();
  initStudentSearch();
  showFlashToasts();
});

function initFormLoading() {
  const form = document.getElementById("add-student-form");
  if (!form) return;

  form.addEventListener("submit", () => {
    const button = document.getElementById("add-btn");
    if (!button || button.disabled) return;
    button.disabled = true;
    button.classList.add("loading");
    button.dataset.originalText = button.textContent;
    button.innerHTML = '<span class="spinner"></span> Сохранение...';
  });
}

function initDeleteConfirmation() {
  const modal = document.getElementById("delete-modal");
  if (!modal) return;

  const nameEl = document.getElementById("delete-student-name");
  const confirmBtn = document.getElementById("confirm-delete-btn");
  const cancelBtn = document.getElementById("cancel-delete-btn");
  let pendingForm = null;

  document.querySelectorAll(".delete-btn").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      pendingForm = button.closest("form");
      if (nameEl) {
        nameEl.textContent = button.dataset.studentName || "этого студента";
      }
      modal.classList.add("open");
    });
  });

  cancelBtn?.addEventListener("click", () => {
    modal.classList.remove("open");
    pendingForm = null;
  });

  confirmBtn?.addEventListener("click", () => {
    if (pendingForm) pendingForm.submit();
    modal.classList.remove("open");
    pendingForm = null;
  });

  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      modal.classList.remove("open");
      pendingForm = null;
    }
  });
}

function initStudentSearch() {
  const search = document.getElementById("student-search");
  const table = document.getElementById("students-table");
  if (!search || !table) return;

  search.addEventListener("input", () => {
    const query = search.value.trim().toLowerCase();
    table.querySelectorAll("tbody tr").forEach((row) => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(query) ? "" : "none";
    });
  });
}

function showFlashToasts() {
  const success = document.querySelector(".alert-success");
  if (!success) return;

  const container = document.querySelector(".toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = success.textContent.trim();
  container.appendChild(toast);

  setTimeout(() => toast.remove(), 4000);
}
