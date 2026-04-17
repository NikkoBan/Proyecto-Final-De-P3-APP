
"use strict";

const API = "/api/v1";

const state = {
  accessToken: null,
  refreshToken: null,
  currentUser: null,
  tasks: [],
  total: 0,
  limit: 20,
  offset: 0,
  statusFilter: "",
  editingTaskId: null,
};

async function apiFetch(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };

  if (state.accessToken) {
    headers["Authorization"] = `Bearer ${state.accessToken}`;
  }

  let response = await fetch(`${API}${path}`, { ...options, headers });

  if (response.status === 401 && state.refreshToken) {
    const refreshed = await attemptRefresh();
    if (refreshed) {
      headers["Authorization"] = `Bearer ${state.accessToken}`;
      response = await fetch(`${API}${path}`, { ...options, headers });
    } else {
      logout();
      return null;
    }
  }

  return response;
}

async function attemptRefresh() {
  try {
    const res = await fetch(`${API}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: state.refreshToken }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    state.accessToken = data.access_token;
    state.refreshToken = data.refresh_token;
    return true;
  } catch {
    return false;
  }
}

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const icons = { success: "✅", error: "❌", info: "ℹ️" };
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${icons[type] || "ℹ️"}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add("removing");
    toast.addEventListener("animationend", () => toast.remove());
  }, 3500);
}

function setLoading(btnId, textId, loading, label) {
  const btn = document.getElementById(btnId);
  const span = document.getElementById(textId);
  btn.disabled = loading;
  span.innerHTML = loading ? `<span class="spinner"></span>` : label;
}

function switchTab(tab) {
  const isLogin = tab === "login";
  document.getElementById("login-form").style.display    = isLogin ? ""     : "none";
  document.getElementById("register-form").style.display = isLogin ? "none" : "";
  document.getElementById("tab-login").classList.toggle("active", isLogin);
  document.getElementById("tab-register").classList.toggle("active", !isLogin);
}

function showFieldError(id, show) {
  document.getElementById(id).classList.toggle("visible", show);
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email    = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;

  let valid = true;
  if (!isValidEmail(email)) { showFieldError("login-email-err", true);    valid = false; } else { showFieldError("login-email-err", false); }
  if (!password)             { showFieldError("login-password-err", true); valid = false; } else { showFieldError("login-password-err", false); }
  if (!valid) return;

  setLoading("login-btn", "login-btn-text", true, "Sign In");

  try {
    const res = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();

    if (!res.ok) {
      showToast(data.detail || "Login failed.", "error");
      return;
    }

    state.accessToken  = data.access_token;
    state.refreshToken = data.refresh_token;
    state.currentUser  = { email };

    enterApp(email);
  } catch {
    showToast("Network error. Please try again.", "error");
  } finally {
    setLoading("login-btn", "login-btn-text", false, "Sign In");
  }
});

document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email    = document.getElementById("reg-email").value.trim();
  const password = document.getElementById("reg-password").value;
  const confirm  = document.getElementById("reg-confirm").value;

  let valid = true;
  if (!isValidEmail(email))         { showFieldError("reg-email-err",    true); valid = false; } else { showFieldError("reg-email-err",    false); }
  if (password.length < 8)          { showFieldError("reg-password-err", true); valid = false; } else { showFieldError("reg-password-err", false); }
  if (password !== confirm)         { showFieldError("reg-confirm-err",  true); valid = false; } else { showFieldError("reg-confirm-err",  false); }
  if (!valid) return;

  setLoading("register-btn", "register-btn-text", true, "Create Account");

  try {
    const res = await fetch(`${API}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();

    if (!res.ok) {
      showToast(data.detail || "Registration failed.", "error");
      return;
    }

    showToast("Account created! Please sign in.", "success");
    switchTab("login");
    document.getElementById("login-email").value = email;
  } catch {
    showToast("Network error. Please try again.", "error");
  } finally {
    setLoading("register-btn", "register-btn-text", false, "Create Account");
  }
});


function enterApp(email) {
  document.getElementById("auth-screen").style.display = "none";
  const appScreen = document.getElementById("app-screen");
  appScreen.classList.add("visible");

  const initial = email.charAt(0).toUpperCase();
  document.getElementById("user-avatar").textContent       = initial;
  document.getElementById("user-email-display").textContent = email;

  loadTasks();
}

function logout() {
  state.accessToken  = null;
  state.refreshToken = null;
  state.currentUser  = null;
  state.tasks        = [];
  state.offset       = 0;

  document.getElementById("app-screen").classList.remove("visible");
  document.getElementById("auth-screen").style.display = "";
  resetStats();
  showToast("Signed out successfully.", "info");
}

function resetStats() {
  ["stat-total","stat-pending","stat-progress","stat-done"].forEach(
    id => (document.getElementById(id).textContent = "—")
  );
}

async function loadStats() {
  const statuses = ["", "pending", "in_progress", "done"];
  const ids      = ["stat-total","stat-pending","stat-progress","stat-done"];

  const counts = await Promise.all(
    statuses.map(async (s) => {
      const qs  = s ? `?status=${s}&limit=1&offset=0` : `?limit=1&offset=0`;
      const res = await apiFetch(`/tasks${qs}`);
      if (!res || !res.ok) return "—";
      const data = await res.json();
      return data.total;
    })
  );

  counts.forEach((count, i) => {
    document.getElementById(ids[i]).textContent = count;
  });
}

function setFilter(btn, statusValue) {
  document.querySelectorAll(".filter-pill").forEach(p => p.classList.remove("active"));
  btn.classList.add("active");
  state.statusFilter = statusValue;
  state.offset = 0;
  loadTasks();
}

async function loadTasks() {
  renderSkeletonRows();
  const qs = new URLSearchParams({
    limit:  state.limit,
    offset: state.offset,
  });
  if (state.statusFilter) qs.set("status", state.statusFilter);

  try {
    const res = await apiFetch(`/tasks?${qs}`);
    if (!res || !res.ok) {
      showToast("Failed to load tasks.", "error");
      return;
    }
    const data = await res.json();
    state.tasks = data.items;
    state.total = data.total;
    renderTasks();
    renderPagination();
    loadStats();
  } catch {
    showToast("Network error loading tasks.", "error");
  }
}

function renderSkeletonRows() {
  const tbody = document.getElementById("tasks-tbody");
  tbody.innerHTML = Array(5).fill(0).map(() => `
    <tr>
      <td><div class="skeleton" style="height:14px;width:80%"></div></td>
      <td><div class="skeleton" style="height:14px;width:60px"></div></td>
      <td><div class="skeleton" style="height:14px;width:50px"></div></td>
      <td><div class="skeleton" style="height:14px;width:70px"></div></td>
      <td><div class="skeleton" style="height:14px;width:90px"></div></td>
    </tr>
  `).join("");
  document.getElementById("tasks-empty").style.display = "none";
}

function statusBadge(status) {
  const map = {
    pending:     ["badge-pending",  "⏳", "Pending"],
    in_progress: ["badge-progress", "⚡", "In Progress"],
    done:        ["badge-done",     "✅", "Done"],
  };
  const [cls, icon, label] = map[status] || ["", "", status];
  return `<span class="badge ${cls}">${icon} ${label}</span>`;
}

function priorityBadge(priority) {
  const map = {
    low:    ["badge-low",    "▽", "Low"],
    medium: ["badge-medium", "◇", "Medium"],
    high:   ["badge-high",   "▲", "High"],
  };
  const [cls, icon, label] = map[priority] || ["", "", priority];
  return `<span class="badge ${cls}">${icon} ${label}</span>`;
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short", day: "numeric", year: "numeric",
  });
}

function renderTasks() {
  const tbody = document.getElementById("tasks-tbody");
  const empty = document.getElementById("tasks-empty");

  if (state.tasks.length === 0) {
    tbody.innerHTML = "";
    empty.style.display = "";
    return;
  }

  empty.style.display = "none";
  tbody.innerHTML = state.tasks.map(t => `
    <tr>
      <td>
        <div class="task-title">${escHtml(t.title)}</div>
        ${t.description ? `<div class="task-desc">${escHtml(t.description.slice(0,60))}${t.description.length > 60 ? "…" : ""}</div>` : ""}
      </td>
      <td>${statusBadge(t.status)}</td>
      <td>${priorityBadge(t.priority)}</td>
      <td style="color:var(--text-secondary);font-size:.82rem">${formatDate(t.created_at)}</td>
      <td>
        <div class="action-cell">
          <button class="btn btn-edit" onclick="openEditModal(${t.id})">Edit</button>
          <button class="btn btn-danger" onclick="deleteTask(${t.id})">Del</button>
        </div>
      </td>
    </tr>
  `).join("");
}

function escHtml(str) {
  return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function renderPagination() {
  const info   = document.getElementById("pagination-info");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const showing = Math.min(state.offset + state.limit, state.total) - state.offset;
  info.textContent = `Showing ${state.offset + 1}–${state.offset + showing} of ${state.total}`;
  if (state.total === 0) info.textContent = "No tasks";
  prevBtn.disabled = state.offset === 0;
  nextBtn.disabled = state.offset + state.limit >= state.total;
}

function changePage(direction) {
  state.offset = Math.max(0, state.offset + direction * state.limit);
  loadTasks();
}

function openCreateModal() {
  state.editingTaskId = null;
  document.getElementById("modal-title").textContent       = "New Task";
  document.getElementById("modal-submit-text").textContent = "Create Task";
  document.getElementById("task-form").reset();
  clearModalErrors();
  document.getElementById("task-modal").classList.add("open");
}

async function openEditModal(taskId) {
  const task = state.tasks.find(t => t.id === taskId);
  if (!task) return;

  state.editingTaskId = taskId;
  document.getElementById("modal-title").textContent       = "Edit Task";
  document.getElementById("modal-submit-text").textContent = "Save Changes";
  document.getElementById("task-title").value    = task.title;
  document.getElementById("task-desc").value     = task.description || "";
  document.getElementById("task-status").value   = task.status;
  document.getElementById("task-priority").value = task.priority;
  clearModalErrors();
  document.getElementById("task-modal").classList.add("open");
}

function closeModal() {
  document.getElementById("task-modal").classList.remove("open");
  state.editingTaskId = null;
}

function clearModalErrors() {
  document.getElementById("task-title-err").classList.remove("visible");
}

document.getElementById("task-modal").addEventListener("click", (e) => {
  if (e.target === e.currentTarget) closeModal();
});

document.getElementById("task-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const title    = document.getElementById("task-title").value.trim();
  const desc     = document.getElementById("task-desc").value.trim();
  const status   = document.getElementById("task-status").value;
  const priority = document.getElementById("task-priority").value;

  if (title.length < 3 || title.length > 100) {
    document.getElementById("task-title-err").classList.add("visible");
    return;
  }
  document.getElementById("task-title-err").classList.remove("visible");

  const payload = { title, description: desc || null, status, priority };
  const isEdit  = state.editingTaskId !== null;
  const submitBtn = document.getElementById("modal-submit-btn");

  submitBtn.disabled = true;
  document.getElementById("modal-submit-text").innerHTML = `<span class="spinner"></span>`;

  try {
    const res = await apiFetch(
      isEdit ? `/tasks/${state.editingTaskId}` : "/tasks",
      { method: isEdit ? "PUT" : "POST", body: JSON.stringify(payload) }
    );

    if (!res || !res.ok) {
      const data = await res?.json();
      showToast(data?.detail || "Failed to save task.", "error");
      return;
    }

    showToast(isEdit ? "Task updated!" : "Task created!", "success");
    closeModal();
    loadTasks();
  } catch {
    showToast("Network error.", "error");
  } finally {
    submitBtn.disabled = false;
    document.getElementById("modal-submit-text").textContent = isEdit ? "Save Changes" : "Create Task";
  }
});

async function deleteTask(taskId) {
  if (!confirm("Delete this task? This cannot be undone.")) return;

  try {
    const res = await apiFetch(`/tasks/${taskId}`, { method: "DELETE" });
    if (!res || (res.status !== 204 && !res.ok)) {
      const data = await res?.json().catch(() => ({}));
      showToast(data?.detail || "Failed to delete.", "error");
      return;
    }
    showToast("Task deleted.", "info");
    loadTasks();
  } catch {
    showToast("Network error.", "error");
  }
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModal();
});
