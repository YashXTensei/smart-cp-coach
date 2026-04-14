function showToast(message, type = 'success') {
  // type: 'success' | 'danger' | 'warning' | 'info'

  const container = document.getElementById('toast-container');

  const toast = document.createElement('div');
  toast.className = `toast align-items-center text-bg-${type} border-0 show mb-2`;
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', 'assertive');
  toast.style.minWidth = '280px';

  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body fw-semibold">${message}</div>
      <button type="button"
              class="btn-close btn-close-white me-2 m-auto"
              data-bs-dismiss="toast"
              aria-label="Close">
      </button>
    </div>
  `;

  container.appendChild(toast);

  // Bootstrap Toast initialize karo
  const bsToast = new bootstrap.Toast(toast, { delay: 3500 });
  bsToast.show();

  // DOM se remove karo fade hone ke baad
  toast.addEventListener('hidden.bs.toast', () => toast.remove());
}