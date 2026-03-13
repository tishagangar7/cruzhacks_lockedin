const API_BASE_URL = window.location.origin;

const classFilter = document.getElementById("classFilter");
const topicFilter = document.getElementById("topicFilter");
const modeFilter = document.getElementById("modeFilter");
const locationFilter = document.getElementById("locationFilter");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const selectedGroupIds = new Set();
const LOCAL_SELECTIONS_KEY = "selected_group_ids";

function userQuerySuffix() {
  const userId = localStorage.getItem("user_id");
  return userId ? `?user_id=${encodeURIComponent(userId)}` : "";
}

function loadLocalSelectionIds() {
  try {
    const raw = localStorage.getItem(LOCAL_SELECTIONS_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((id) => Number.isInteger(id));
  } catch {
    return [];
  }
}

function saveLocalSelectionIds() {
  localStorage.setItem(LOCAL_SELECTIONS_KEY, JSON.stringify(Array.from(selectedGroupIds)));
}

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.color = isError ? "#9a1b1b" : "#1f1f1f";
}

function renderGroups(groups) {
  if (!groups.length) {
    resultsEl.innerHTML = "<p>No groups matched these filters.</p>";
    return;
  }

  resultsEl.innerHTML = groups
    .map(
      (group) => `
      <div class="group-card">
        <h3>${group.subject_title || group.class_code || "Study Group"}</h3>
        <p><strong>Class:</strong> ${group.class_code || "-"}</p>
        <p><strong>Mode:</strong> ${group.mode || "-"}</p>
        <p><strong>Location:</strong> ${group.location || "-"}</p>
        <p><strong>Topics:</strong> ${(group.topics || []).join(", ") || "-"}</p>
        <button
          type="button"
          class="select-btn ${selectedGroupIds.has(group.group_id) ? "selected" : ""}"
          data-group-id="${group.group_id}"
        >
          ${selectedGroupIds.has(group.group_id) ? "Unselect" : "Select Group"}
        </button>
      </div>
    `
    )
    .join("");

}

async function loadSelections() {
  selectedGroupIds.clear();
  for (const id of loadLocalSelectionIds()) {
    selectedGroupIds.add(id);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/selections${userQuerySuffix()}`, {
      credentials: "include",
    });
    const data = await response.json();
    if (!response.ok || !data.success) {
      return;
    }
    selectedGroupIds.clear();
    for (const item of data.selected_groups || []) {
      if (item.group && Number.isInteger(item.group.group_id)) {
        selectedGroupIds.add(item.group.group_id);
      }
    }
    saveLocalSelectionIds();
  } catch (error) {
    console.error("Failed to load selected groups:", error);
  }
}

async function toggleSelection(buttonEl) {
  const groupId = Number(buttonEl.dataset.groupId);
  if (!Number.isInteger(groupId)) {
    return;
  }

  const currentlySelected = selectedGroupIds.has(groupId);
  buttonEl.disabled = true;
  try {
    const response = await fetch(`${API_BASE_URL}/api/selections${userQuerySuffix()}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ group_id: groupId, selected: !currentlySelected }),
    });
    const data = await response.json();
    if (!response.ok || !data.success) {
      throw new Error(data.message || "Could not save group selection.");
    }

    if (currentlySelected) {
      selectedGroupIds.delete(groupId);
      buttonEl.classList.remove("selected");
      buttonEl.textContent = "Select Group";
      setStatus("Group unselected.");
    } else {
      selectedGroupIds.add(groupId);
      buttonEl.classList.add("selected");
      buttonEl.textContent = "Unselect";
      setStatus("Group selected and saved.");
    }
    saveLocalSelectionIds();
  } catch (error) {
    console.error("Error saving selection:", error);
    // Fallback so the UX still works even if backend persistence fails.
    if (currentlySelected) {
      selectedGroupIds.delete(groupId);
      buttonEl.classList.remove("selected");
      buttonEl.textContent = "Select Group";
      setStatus("Group unselected locally. Backend sync failed.", true);
    } else {
      selectedGroupIds.add(groupId);
      buttonEl.classList.add("selected");
      buttonEl.textContent = "Unselect";
      setStatus("Group selected locally. Backend sync failed.", true);
    }
    saveLocalSelectionIds();
  } finally {
    buttonEl.disabled = false;
  }
}

async function loadClassOptions() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/get-user-classes${userQuerySuffix()}`, {
      credentials: "include",
    });
    const data = await response.json();

    if (!response.ok || !data.success || !Array.isArray(data.classes)) {
      return;
    }

    for (const classCode of data.classes) {
      const option = document.createElement("option");
      option.value = classCode;
      option.textContent = classCode;
      classFilter.appendChild(option);
    }
  } catch (error) {
    console.error("Failed to load classes:", error);
  }
}

async function applyFilters() {
  setStatus("Applying filters...");

  const payload = {
    classes: classFilter.value,
    keywords: topicFilter.value.trim(),
    mode: modeFilter.value,
    location: locationFilter.value.trim(),
  };

  try {
    const response = await fetch(`${API_BASE_URL}/api/filters`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(payload),
    });
    const data = await response.json();

    if (!response.ok || !data.success) {
      setStatus(data.message || "Failed to apply filters.", true);
      return;
    }

    const groups = Array.isArray(data.groups) ? data.groups : [];
    setStatus(`Found ${groups.length} matching group(s).`);
    renderGroups(groups);
  } catch (error) {
    console.error("Error applying filters:", error);
    setStatus("An error occurred while applying filters.", true);
  }
}

function clearFilters() {
  classFilter.value = "";
  topicFilter.value = "";
  modeFilter.value = "";
  locationFilter.value = "";
  resultsEl.innerHTML = "";
  setStatus("Filters cleared.");
}

document.getElementById("applyBtn").addEventListener("click", applyFilters);
document.getElementById("resetBtn").addEventListener("click", clearFilters);
document.getElementById("scheduleBtn").addEventListener("click", () => {
  window.location.href = "schedule.html";
});
document.getElementById("profileBtn").addEventListener("click", () => {
  window.location.href = "profiledisplay.html";
});
resultsEl.addEventListener("click", (event) => {
  const btn = event.target.closest(".select-btn");
  if (!btn) return;
  toggleSelection(btn);
});

document.addEventListener("DOMContentLoaded", async () => {
  await loadSelections();
  await loadClassOptions();
  await applyFilters();
});
