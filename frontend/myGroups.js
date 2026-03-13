const API_BASE_URL = window.location.origin;
const groupsContainer = document.getElementById("groupsContainer");
const statusEl = document.getElementById("status");
const LOCAL_SELECTIONS_KEY = "selected_group_ids";
const LOCAL_CREATED_GROUPS_KEY = "created_groups_local";

function getLocalSelectedIds() {
  try {
    const raw = localStorage.getItem(LOCAL_SELECTIONS_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((id) => Number.isInteger(id));
  } catch {
    return [];
  }
}

function saveLocalSelectedIds(ids) {
  localStorage.setItem(LOCAL_SELECTIONS_KEY, JSON.stringify(ids));
}

function getLocalCreatedGroups() {
  try {
    const raw = localStorage.getItem(LOCAL_CREATED_GROUPS_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveLocalCreatedGroups(groups) {
  localStorage.setItem(LOCAL_CREATED_GROUPS_KEY, JSON.stringify(groups));
}

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.color = isError ? "#b91c1c" : "#1f1f1f";
}

function renderGroups(selectedGroups) {
  if (!selectedGroups.length) {
    groupsContainer.innerHTML = "<p>No groups selected yet. Go to Filters and select groups.</p>";
    return;
  }

  groupsContainer.innerHTML = selectedGroups
    .map((item) => {
      const group = item.group || {};
      const title = group.subject_title || group.class_code || "Study Group";
      return `
        <div class="group-card">
          <h3>${title}</h3>
          <p><strong>Class:</strong> ${group.class_code || "-"}</p>
          <p><strong>Mode:</strong> ${group.mode || "-"}</p>
          <p><strong>Location:</strong> ${group.location || "-"}</p>
          <p><strong>Topics:</strong> ${(group.topics || []).join(", ") || "-"}</p>
          <button class="remove-btn" type="button" data-group-id="${group.group_id}">Remove</button>
        </div>
      `;
    })
    .join("");

  for (const btn of groupsContainer.querySelectorAll(".remove-btn")) {
    btn.addEventListener("click", () => unselectGroup(Number(btn.dataset.groupId)));
  }
}

function renderCreatedGroups(createdGroups) {
  const sectionId = "createdGroupsSection";
  const existing = document.getElementById(sectionId);
  if (existing) existing.remove();

  const section = document.createElement("div");
  section.id = sectionId;
  section.className = "group-card";
  section.style.marginTop = "12px";
  section.innerHTML = "<h3>Groups You Created</h3>";

  if (!createdGroups.length) {
    section.innerHTML += "<p>No created groups yet.</p>";
  } else {
    section.innerHTML += createdGroups
      .map((group) => {
        const topics = Array.isArray(group.topics) ? group.topics.join(", ") : (group.topics || "");
        return `
          <div style="border-top:1px solid #e5e7eb; padding-top:8px; margin-top:8px;">
            <p><strong>Class:</strong> ${group.class_code || "-"}</p>
            <p><strong>Location:</strong> ${group.location || "-"}</p>
            <p><strong>Topics:</strong> ${topics || "-"}</p>
            <p><strong>Time:</strong> ${group.time_block || "-"}</p>
          </div>
        `;
      })
      .join("");
  }

  groupsContainer.insertAdjacentElement("afterend", section);
}

async function loadMyGroups() {
  setStatus("Loading your groups...");
  const userId = localStorage.getItem("user_id");
  const query = userId ? `?user_id=${encodeURIComponent(userId)}` : "";

  let selectedCount = 0;
  let createdCount = 0;
  try {
    const [response, createdRes] = await Promise.all([
      fetch(`${API_BASE_URL}/api/selections${query}`, { credentials: "include" }),
      fetch(`${API_BASE_URL}/api/created-groups${query}`, { credentials: "include" }),
    ]);
    const data = await response.json();
    const createdData = await createdRes.json();

    if (!response.ok || !data.success) {
      throw new Error(data.message || "Could not load your groups.");
    }

    const selectedGroups = data.selected_groups || [];
    const ids = selectedGroups
      .map((item) => item.group && item.group.group_id)
      .filter((id) => Number.isInteger(id));
    saveLocalSelectedIds(ids);
    selectedCount = selectedGroups.length;
    renderGroups(selectedGroups);

    if (createdRes.ok && createdData.success) {
      const groups = createdData.groups || [];
      createdCount = groups.length;
      saveLocalCreatedGroups(groups);
      renderCreatedGroups(groups);
    } else {
      const localCreated = getLocalCreatedGroups();
      createdCount = localCreated.length;
      renderCreatedGroups(localCreated);
    }
    setStatus(`You have ${selectedCount} selected group(s) and ${createdCount} created group(s).`);
  } catch (error) {
    console.error("Failed to load groups from selections API:", error);
    const localIds = getLocalSelectedIds();
    if (!localIds.length) {
      setStatus("You have 0 selected group(s).");
      renderGroups([]);
      return;
    }

    try {
      const groupsRes = await fetch(`${API_BASE_URL}/api/filtered-groups`, { credentials: "include" });
      const groupsData = await groupsRes.json();
      if (!groupsRes.ok || !groupsData.success) {
        throw new Error(groupsData.message || "Could not load group catalog.");
      }
      const selectedGroups = (groupsData.groups || [])
        .filter((group) => localIds.includes(group.group_id))
        .map((group) => ({ group }));

      selectedCount = selectedGroups.length;
      renderGroups(selectedGroups);
      const localCreated = getLocalCreatedGroups();
      createdCount = localCreated.length;
      renderCreatedGroups(localCreated);
      setStatus(`You have ${selectedCount} selected group(s) and ${createdCount} created group(s). (local cache)`, true);
    } catch (fallbackError) {
      console.error("Fallback group load failed:", fallbackError);
      setStatus("Could not load your groups right now.", true);
      groupsContainer.innerHTML = "";
      renderCreatedGroups(getLocalCreatedGroups());
    }
  }
}

async function unselectGroup(groupId) {
  if (!Number.isInteger(groupId)) return;
  const userId = localStorage.getItem("user_id");
  const query = userId ? `?user_id=${encodeURIComponent(userId)}` : "";

  try {
    const response = await fetch(`${API_BASE_URL}/api/selections${query}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ group_id: groupId, selected: false }),
    });
    const data = await response.json();
    if (!response.ok || !data.success) {
      throw new Error(data.message || "Could not remove group.");
    }
    setStatus("Group removed.");
  } catch (error) {
    console.error("Failed to remove group from API:", error);
    setStatus("Group removed locally. Backend sync failed.", true);
  } finally {
    const nextIds = getLocalSelectedIds().filter((id) => id !== groupId);
    saveLocalSelectedIds(nextIds);
    loadMyGroups();
  }
}

document.getElementById("creategroupButton").addEventListener("click", () => {
  window.location.href = "newGroup.html";
});

document.getElementById("backToHomeButton").addEventListener("click", () => {
  window.location.href = "index.html";
});

document.addEventListener("DOMContentLoaded", loadMyGroups);