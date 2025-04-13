async function applyFilters() {
    const filters = {
      schedule: {
        category: document.getElementById("scheduleCategory").value,
        time: document.getElementById("scheduleTime").value,
      },
      keywords: document.getElementById("keywordFilter").value,
      classes: document.getElementById("classFilter").value,
    };
  
    try {
      const response = await fetch("/api/filters", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(filters),
      });
  
      const data = await response.json();
      if (data.success) {
        console.log("Filtered Results:", data.filters);
        // Update the UI with the filtered results
      } else {
        alert(data.message);
      }
    } catch (error) {
      console.error("Error applying filters:", error);
      alert("An error occurred while applying filters.");
    }
  }

meetingMode = document.getElementById("modeFilter").value;
