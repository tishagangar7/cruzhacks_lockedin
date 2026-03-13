document.addEventListener("DOMContentLoaded", function () {
  const calendarEl = document.getElementById("calendar");
  const durationEl = document.getElementById("duration");
  const modalEl = document.getElementById("category-modal");
  const backdropEl = document.getElementById("modal-backdrop");
  const slotsListEl = document.getElementById("slots-list");
  const selectedSlots = [];
  let currentSelection = null;
  let selectedDay = null;

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "timeGridWeek",
    selectable: true,
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: "timeGridWeek",
    },
    select: function (info) {
      const now = new Date();
      const selectedStartTime = new Date(info.start);
      const oneHourFromNow = new Date(now.getTime() + 60 * 60 * 1000);

      if (selectedStartTime < oneHourFromNow) {
        alert("Please pick a time at least 1 hour from now.");
        return;
      }

      const selectedDate = info.start.toISOString().split("T")[0];
      if (selectedDay && selectedDay !== selectedDate) {
        alert("Select slots for one day only.");
        return;
      }
      selectedDay = selectedDate;

      const duration = parseInt(durationEl.value, 10);
      const adjustedEnd = new Date(info.start);
      adjustedEnd.setHours(adjustedEnd.getHours() + duration);

      currentSelection = { start: info.start, end: adjustedEnd };
      showModal();
    },
  });

  calendar.render();

  function showModal() {
    modalEl.classList.remove("hidden");
    backdropEl.style.display = "block";
  }

  function hideModal() {
    modalEl.classList.add("hidden");
    backdropEl.style.display = "none";
  }

  function getColorForCategory(category) {
    if (category === "works best") return "#4caf50";
    if (category === "works") return "#ffc107";
    if (category === "not preferred") return "#f44336";
    return "#2196f3";
  }

  function addSlotToList(slot, event) {
    const li = document.createElement("li");
    li.textContent = `${slot.date}: ${slot.time} (${slot.category})`;

    const removeBtn = document.createElement("button");
    removeBtn.textContent = "Remove";
    removeBtn.classList.add("remove-slot");
    removeBtn.addEventListener("click", () => {
      event.remove();
      const index = selectedSlots.indexOf(slot);
      if (index > -1) selectedSlots.splice(index, 1);
      li.remove();
      if (selectedSlots.length === 0) selectedDay = null;
    });

    li.appendChild(removeBtn);
    slotsListEl.appendChild(li);
  }

  document.querySelectorAll(".category-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const category = btn.dataset.category;
      const slot = {
        date: currentSelection.start.toISOString().split("T")[0],
        time: `${currentSelection.start.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        })} - ${currentSelection.end.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        })}`,
        category: category,
      };

      selectedSlots.push(slot);
      const event = calendar.addEvent({
        title: category,
        start: currentSelection.start,
        end: currentSelection.end,
        backgroundColor: getColorForCategory(category),
      });

      addSlotToList(slot, event);
      hideModal();
    });
  });

  document.getElementById("cancel-modal").addEventListener("click", hideModal);

  document.getElementById("submit").addEventListener("click", async () => {
    if (!selectedDay) {
      alert("Please select at least one time slot.");
      return;
    }

    const grouped = { "works best": [], works: [], "not preferred": [] };
    for (const slot of selectedSlots) {
      grouped[slot.category].push(slot.time);
    }

    const payload = {
      duration: parseInt(durationEl.value, 10),
      schedule: {
        [selectedDay]: grouped,
      },
    };

    try {
      const response = await fetch("/api/process-schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok || !data.success) {
        alert(data.message || "Failed to save schedule.");
        return;
      }

      alert("Schedule saved successfully!");
      window.location.href = "filters.html";
    } catch (error) {
      console.error("Error saving schedule:", error);
      alert("An error occurred while saving the schedule.");
    }
  });
});
