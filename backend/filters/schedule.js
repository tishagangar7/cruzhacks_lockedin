document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar');
    const durationEl = document.getElementById('duration'); // Dropdown for duration
    const modalEl = document.getElementById('category-modal'); // Modal for category selection
    const backdropEl = document.getElementById('modal-backdrop'); // Modal backdrop
    const slotsListEl = document.getElementById('slots-list'); // List of selected slots
    const selectedSlots = [];
    let currentSelection = null; // Store the current selection info
    let selectedDay = null; // Store the selected day
  
    // Initialize FullCalendar
    const calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'timeGridWeek', // Weekly view with time slots
      selectable: true, // Allow selecting time slots
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'timeGridWeek', // Only weekly view
      },
      select: function (info) {
        const currentTime = new Date(); // Get the current time
        const selectedStartTime = new Date(info.start); // Start time of the selected slot
        const oneHourFromNow = new Date(currentTime.getTime() + 60 * 60 * 1000); // 1 hour from now
  
        // Validate that the selected time is not in the past or within 1 hour from now
        if (selectedStartTime < oneHourFromNow) {
          alert('The selected time must be at least 1 hour from now. Please choose a valid time slot.');
          return; // Stop further processing
        }
  
        // Ensure the user is selecting time slots for only one day
        const selectedDate = info.start.toISOString().split('T')[0];
        if (selectedDay && selectedDay !== selectedDate) {
          alert('You can only select time slots for one day. Please modify your preferences to choose another day.');
          return; // Stop further processing
        }
        selectedDay = selectedDate;
  
        // Get the selected duration from the dropdown
        const duration = parseInt(durationEl.value, 10); // Convert to integer
        const adjustedEnd = new Date(info.start); // Clone the start time
        adjustedEnd.setHours(adjustedEnd.getHours() + duration); // Add the duration
  
        // Store the current selection info
        currentSelection = {
          start: info.start,
          end: adjustedEnd,
        };
  
        // Show the modal
        showModal();
      },
    });
  
    calendar.render();
  
    // Show the modal
    function showModal() {
      modalEl.classList.remove('hidden');
      backdropEl.style.display = 'block';
    }
  
    // Hide the modal
    function hideModal() {
      modalEl.classList.add('hidden');
      backdropEl.style.display = 'none';
    }
  
    // Handle category button clicks
    document.querySelectorAll('.category-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const category = btn.dataset.category;
  
        // Add the time slot to the selectedSlots array
        const slot = {
          date: currentSelection.start.toISOString().split('T')[0],
          time: `${currentSelection.start.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })} - ${currentSelection.end.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}`,
          category: category,
        };
        selectedSlots.push(slot);
  
        // Add the event to the calendar with the appropriate styling
        const event = calendar.addEvent({
          title: category,
          start: currentSelection.start,
          end: currentSelection.end,
          backgroundColor: getColorForCategory(category),
          extendedProps: { category: category },
        });
  
        // Add the slot to the list
        addSlotToList(slot, event);
  
        // Hide the modal
        hideModal();
      });
    });
  
    // Handle cancel button
    document.getElementById('cancel-modal').addEventListener('click', hideModal);
  
    // Helper function to assign colors based on category
    function getColorForCategory(category) {
      if (category.toLowerCase() === 'works best') return '#4caf50'; // Green
      if (category.toLowerCase() === 'works') return '#ffc107'; // Yellow
      if (category.toLowerCase() === 'not preferred') return '#f44336'; // Red
      return '#2196f3'; // Default Blue
    }
  
    // Add a slot to the list with a remove button
    function addSlotToList(slot, event) {
      const li = document.createElement('li');
      li.textContent = `${slot.date}: ${slot.time} (${slot.category})`;
  
      const removeBtn = document.createElement('button');
      removeBtn.textContent = 'Remove';
      removeBtn.classList.add('remove-slot');
      removeBtn.addEventListener('click', () => {
        // Remove the event from the calendar
        event.remove();
  
        // Remove the slot from the selectedSlots array
        const index = selectedSlots.indexOf(slot);
        if (index > -1) {
          selectedSlots.splice(index, 1);
        }
  
        // Remove the slot from the list
        li.remove();
  
        // Reset selectedDay if no slots are left
        if (selectedSlots.length === 0) {
          selectedDay = null;
        }
      });
  
      li.appendChild(removeBtn);
      slotsListEl.appendChild(li);
    }
  
    document.getElementById('submit').addEventListener('click', () => {
      if (!selectedDay) {
        alert('Please select at least one time slot.');
        return;
      }
    
      console.log('Selected Slots:', selectedSlots);
    
      // Prepare the schedule object
      const schedule = { [selectedDay]: selectedSlots };
    
      // Send the schedule to the backend
      fetch('/api/process-schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ schedule }),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log('Server Response:', data);
          if (data.success) {
            alert('Schedule saved successfully!');
            window.location.href = 'preferences.html'; // Redirect to preferences or another page
          } else {
            alert('Failed to save schedule.');
          }
        })
        .catch((error) => {
          console.error('Error:', error);
          alert('An error occurred while saving the schedule.');
        });
    });
  });