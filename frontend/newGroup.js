const API_BASE_URL = window.location.origin;
const LOCAL_CREATED_GROUPS_KEY = "created_groups_local";

function getSelectedTime() {
  const selected = document.querySelector(".button1.pressed");
  return selected ? selected.textContent.trim() : "";
}

function saveCreatedGroupLocally(group) {
  let existing = [];
  try {
    existing = JSON.parse(localStorage.getItem(LOCAL_CREATED_GROUPS_KEY) || "[]");
    if (!Array.isArray(existing)) existing = [];
  } catch {
    existing = [];
  }
  existing.unshift(group);
  localStorage.setItem(LOCAL_CREATED_GROUPS_KEY, JSON.stringify(existing));
}

async function createGroup() {
  const classCode = document.getElementById("classname").value.trim();
  const location = document.getElementById("location").value.trim();
  const topicsRaw = document.getElementById("topics").value.trim();
  const timeBlock = getSelectedTime();
  const topics = topicsRaw
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean);

  if (!classCode || !location || !topics.length) {
    alert("Please fill class, location, and topics.");
    return false;
  }

  const payload = {
    class_code: classCode,
    location,
    topics,
    time_block: timeBlock,
    mode: "in_person",
  };

  const userId = localStorage.getItem("user_id");
  const query = userId ? `?user_id=${encodeURIComponent(userId)}` : "";

  try {
    const response = await fetch(`${API_BASE_URL}/api/created-groups${query}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok || !data.success) {
      throw new Error(data.message || "Could not create group.");
    }
    saveCreatedGroupLocally({
      id: data.group_id,
      class_code: classCode,
      location,
      topics,
      time_block: timeBlock,
      mode: "in_person",
      created_at: new Date().toISOString(),
    });
    return true;
  } catch (error) {
    console.error("Create group API failed:", error);
    saveCreatedGroupLocally({
      id: Date.now(),
      class_code: classCode,
      location,
      topics,
      time_block: timeBlock,
      mode: "in_person",
      created_at: new Date().toISOString(),
      local_only: true,
    });
    return true;
  }
}

document.querySelectorAll('.button1').forEach(button => {
    button.addEventListener('click', function () {
      // Remove "pressed" class from all buttons
      document.querySelectorAll('.button1').forEach(btn => btn.classList.remove('pressed'));
  
      // Add "pressed" class to the clicked button
      this.classList.add('pressed');
    });
  });

  document.addEventListener('DOMContentLoaded', function () {
    const popupOverlay = document.getElementById('popupOverlay');
    const popup = document.getElementById('popup');
    const closePopup = document.getElementById('closePopup');

    // Function to open the popup
    function openPopup() {
        popupOverlay.style.display = 'block';
    }

    // Function to close the popup
    function closePopupFunc() {
        popupOverlay.style.display = 'none';
    }

    // Event listener for the "end" button to open the popup
    document.getElementById('end').addEventListener('click', async (e) => {
        e.preventDefault(); // Prevent default behavior
        const ok = await createGroup();
        if (ok) {
          openPopup(); // Open the popup
        }
    });

    // Close the popup when the close button is clicked
    closePopup.addEventListener('click', closePopupFunc);

    // Redirect functionality for the OK button
    document.getElementById('okButton').addEventListener('click', () => {
        window.location.href = 'index.html'; // Redirect to index.html in the same tab
    });
});

    // You can customize and expand these functions based on your specific requirements.





 