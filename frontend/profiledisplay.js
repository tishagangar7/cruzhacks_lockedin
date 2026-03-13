const API_BASE_URL = window.location.origin;

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) {
    el.textContent = value || "-";
  }
}

function renderAppointments(scheduleObj, classes = []) {
  const list = document.getElementById("appointments-list");
  if (!list) return;
  const items = [];
  const classLabel = classes.length ? classes.join(", ") : "General";
  for (const [day, categories] of Object.entries(scheduleObj || {})) {
    for (const [category, slots] of Object.entries(categories || {})) {
      for (const slot of slots || []) {
        items.push(`${day} - ${slot} (${category}) [Class: ${classLabel}]`);
      }
    }
  }

  if (!items.length) {
    list.innerHTML = "<li>No appointments yet.</li>";
    return;
  }
  list.innerHTML = items.map((item) => `<li>${item}</li>`).join("");
}

function appendSwipeAppointments() {
  const list = document.getElementById("appointments-list");
  if (!list) return;
  let swipes = [];
  try {
    swipes = JSON.parse(localStorage.getItem("swiped_right_appointments") || "[]");
    if (!Array.isArray(swipes)) swipes = [];
  } catch {
    swipes = [];
  }
  if (!swipes.length) return;

  const existingNoAppointments = list.querySelector("li")?.textContent === "No appointments yet.";
  if (existingNoAppointments) {
    list.innerHTML = "";
  }

  const swipeItems = swipes.slice(0, 20).map((item) => {
    const className = item.class_name || "Study Group";
    const location = item.location || "Remote";
    const time = item.time_block || "Flexible";
    return `<li>Swipe Match - ${className} (${location}) at ${time}</li>`;
  });
  list.innerHTML += swipeItems.join("");
}

function renderSelectedGroups(selectedGroups) {
  const list = document.getElementById("selected-groups-list");
  if (!list) return;
  if (!selectedGroups.length) {
    list.innerHTML = "<li>No selected groups yet.</li>";
    return;
  }

  list.innerHTML = selectedGroups
    .map((item) => {
      const group = item.group || {};
      const title = group.subject_title || group.class_code || "Study Group";
      const location = group.location || "-";
      return `<li>${title} (${location})</li>`;
    })
    .join("");
}

async function loadProfile() {
  try {
    const storedUserId = localStorage.getItem("user_id");

    let meRes = await fetch(`${API_BASE_URL}/api/me`, {
      method: "GET",
      credentials: "include",
    });
    let meData = await meRes.json();

    // Fallback: if session cookie is missing, try localStorage user id.
    if ((!meRes.ok || !meData.success) && storedUserId) {
      meRes = await fetch(`${API_BASE_URL}/api/me?user_id=${encodeURIComponent(storedUserId)}`, {
        method: "GET",
        credentials: "include",
      });
      meData = await meRes.json();
    }

    if (!meRes.ok || !meData.success) {
      window.location.href = "login.html";
      return;
    }

    const querySuffix = storedUserId ? `?user_id=${encodeURIComponent(storedUserId)}` : "";
    const [scheduleRes, selectionsRes] = await Promise.all([
      fetch(`${API_BASE_URL}/api/get-schedule${querySuffix}`, { method: "GET", credentials: "include" }),
      fetch(`${API_BASE_URL}/api/selections${querySuffix}`, { method: "GET", credentials: "include" }),
    ]);

    const user = meData.user || {};
    setText("profile-name", user.name);
    setText("profile-email", user.email);
    setText("profile-email-top", user.email);
    setText("profile-major", user.major);
    setText("profile-year", user.year);
    setText("profile-classes", (user.classes || []).join(", "));
    setText("profile-style", user.study_style);

    const scheduleData = await scheduleRes.json();
    if (scheduleRes.ok && scheduleData.success) {
      renderAppointments(scheduleData.schedule || {}, user.classes || []);
    } else {
      renderAppointments({}, user.classes || []);
    }
    appendSwipeAppointments();

    const selectionsData = await selectionsRes.json();
    if (selectionsRes.ok && selectionsData.success) {
      renderSelectedGroups(selectionsData.selected_groups || []);
    } else {
      renderSelectedGroups([]);
    }
  } catch (error) {
    console.error("Failed to load profile:", error);
    window.location.href = "login.html";
  }
}

document.getElementById("mygroups")?.addEventListener("click", () => {
  window.location.href = "myGroups.html";
});

document.getElementById("profile")?.addEventListener("click", () => {
  window.location.href = "profiledisplay.html";
});

document.getElementById("logout")?.addEventListener("click", async () => {
  try {
    await fetch(`${API_BASE_URL}/api/logout`, {
      method: "POST",
      credentials: "include",
    });
  } finally {
    window.location.href = "login.html";
  }
});

document.addEventListener("DOMContentLoaded", loadProfile);