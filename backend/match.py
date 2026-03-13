def match_study_groups(conn, user_preferences):
    """
    Match study groups based on user preferences with partial matching.
    :param conn: SQLite connection object
    :param user_preferences: Dictionary containing user preferences
    :return: List of matched study groups with match scores
    """
    cursor = conn.cursor()

    # Extract user preferences
    preferred_class = user_preferences.get("class_code")
    preferred_topics = user_preferences.get("topics", [])
    preferred_mode = user_preferences.get("mode")
    preferred_time_blocks = user_preferences.get("time_blocks", [])
    preferred_location = user_preferences.get("location")

    # Query to fetch all study groups
    query = "SELECT * FROM study_groups"
    cursor.execute(query)
    groups = cursor.fetchall()

    # Calculate match scores for each group
    matched_groups = []
    for group in groups:
        group_id, class_code, subject_title, topics, time_blocks, mode, location, group_size, study_style, description = group

        # Decode JSON fields
        group_topics = json.loads(topics)
        group_time_blocks = json.loads(time_blocks)

        # Initialize match score
        match_score = 0

        # Check class code match
        if class_code == preferred_class:
            match_score += 3  # Higher weight for class code match

        # Check topic overlap
        topic_overlap = len(set(preferred_topics) & set(group_topics))
        match_score += topic_overlap * 2  # Add 2 points for each matching topic

        # Check mode match
        if mode == preferred_mode:
            match_score += 2

        # Check time block overlap
        time_overlap = len(set(preferred_time_blocks) & set(group_time_blocks))
        match_score += time_overlap  # Add 1 point for each matching time block

        # Check location match
        if location == preferred_location:
            match_score += 1

        # Add group to matched list if it has a non-zero score
        if match_score > 0:
            matched_groups.append((group, match_score))

    # Sort matched groups by match score in descending order
    matched_groups.sort(key=lambda x: x[1], reverse=True)

    return matched_groups

import sqlite3
import json

# Connect to the database
conn = sqlite3.connect("study_groups.db")

# Example user preferences
user_preferences = {
    "class_code": "CS101",
    "topics": ["Recursion", "Sorting Algorithms"],
    "mode": "in_person",
    "time_blocks": ["8-11am", "2-5pm"],
    "location": "McHenry Library"
}

# Match study groups
matched_groups = match_study_groups(conn, user_preferences)

# # Display matched groups
# if matched_groups:
#     print("Matched Study Groups:")
#     for group, score in matched_groups:
#         print(f"Group ID: {group[0]}, Class: {group[1]}, Topics: {group[3]}, "
#               f"Time Blocks: {group[4]}, Location: {group[6]}, Match Score: {score}")
# else:
#     print("No matching study groups found.")

# # Close the connection
# conn.close()
