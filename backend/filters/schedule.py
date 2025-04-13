from datetime import datetime, timedelta

def process_user_schedule(data):
    """
    Process the user's selected schedule and preferences.
    :param data: A dictionary containing the user's selected time slots and preferences.
    Example:
    {
        "duration": 2,
        "schedule": {
            "2025-04-15": {
                "best": ["9:00 AM - 11:00 AM"],
                "works": ["1:00 PM - 3:00 PM"],
                "not_preferred": ["4:00 PM - 6:00 PM"]
            }
        }
    }
    :return: Processed schedule data with validation results.
    """
    try:
        duration = data.get("duration", 1)
        schedule = data.get("schedule", {})

        # Current time for validation
        current_time = datetime.now()

        # Validate each time slot
        valid_slots = {}
        invalid_slots = {}

        for date, categories in schedule.items():
            valid_slots[date] = {}
            invalid_slots[date] = {}

            for category, time_ranges in categories.items():
                valid_slots[date][category] = []
                invalid_slots[date][category] = []

                for time_range in time_ranges:
                    try:
                        # Parse the start and end times
                        start_time_str, end_time_str = time_range.split(" - ")
                        start_time = datetime.strptime(f"{date} {start_time_str}", "%Y-%m-%d %I:%M %p")
                        end_time = datetime.strptime(f"{date} {end_time_str}", "%Y-%m-%d %I:%M %p")

                        # Validation: Check if the time is in the past
                        if start_time < current_time:
                            raise ValueError("Start time is in the past")

                        # Validation: Check if the time is within 1 hour from now
                        if start_time < current_time + timedelta(hours=1):
                            raise ValueError("Start time must be at least 1 hour from now")

                        # Validation: Check if the end time is after the start time
                        if end_time <= start_time:
                            raise ValueError("End time must be after start time")

                        # If all validations pass, add to valid slots
                        valid_slots[date][category].append(time_range)

                    except ValueError as e:
                        # Add invalid slots with error messages
                        invalid_slots[date][category].append({
                            "time_range": time_range,
                            "error": str(e)
                        })

        # Return the results
        return {
            "success": True,
            "duration": duration,
            "valid_slots": valid_slots,
            "invalid_slots": invalid_slots
        }

    except Exception as e:
        # Handle unexpected errors
        return {"success": False, "message": "An error occurred", "error": str(e)}