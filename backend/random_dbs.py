import sqlite3
import random
import json
from datetime import datetime

# Same data pools as before
class_codes = ["CS101", "BIO20", "MATH23", "PHYS2B", "HIST10", "CHEM1A", "STAT5", "PHIL3", "ECON100A"]
subject_titles = {
    "CS101": "Data Structures",
    "BIO20": "Molecular Biology",
    "MATH23": "Multivariable Calculus",
    "PHYS2B": "Electricity & Magnetism",
    "HIST10": "Modern European History",
    "CHEM1A": "General Chemistry",
    "STAT5": "Probability & Statistics",
    "PHIL3": "Ethics",
    "ECON100A": "Macroeconomic Theory"
}
topics_by_class = {
    "CS101": ["Recursion", "Trees", "Sorting Algorithms", "Big-O Analysis"],
    "BIO20": ["DNA Replication", "Protein Synthesis", "Cell Structures"],
    "MATH23": ["Partial Derivatives", "Double Integrals", "Vector Fields"],
    "PHYS2B": ["Coulomb's Law", "Electric Fields", "Circuits"],
    "HIST10": ["French Revolution", "WWI", "Cold War Politics"],
    "CHEM1A": ["Molecular Structures", "Stoichiometry", "Thermochemistry"],
    "STAT5": ["Probability", "Distributions", "Hypothesis Testing"],
    "PHIL3": ["Utilitarianism", "Kantian Ethics", "Moral Dilemmas"],
    "ECON100A": ["IS-LM Model", "Inflation", "Fiscal Policy"]
}
time_blocks = ["8-11am", "11am-2pm", "2-5pm", "5-8pm", "8-11pm"]
locations_in_person = ["McHenry Library", "Science and Engineering Library", "Jacks Lounge"]
study_styles = ["Quiet", "Discussion", "Problem-Solving", "Flashcards", "Teaching Each Other"]
modes = ["remote", "in_person"]

def generate_and_insert_group(conn, index):
    cursor = conn.cursor()
    class_code = random.choice(class_codes)
    mode = random.choice(modes)
    location = random.choice(locations_in_person) if mode == "in_person" else None
    topics = random.sample(topics_by_class[class_code], random.randint(1, 3))
    time_slots = random.sample(time_blocks, random.randint(1, 2))
    group_id = f"g{index:04d}"

    cursor.execute("""
        INSERT OR REPLACE INTO study_groups (
            group_id, class_code, subject_title, topics, time_blocks,
            mode, location, group_size, study_style, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        group_id,
        class_code,
        subject_titles[class_code],
        json.dumps(topics),
        json.dumps(time_slots),
        mode,
        location,
        f"{random.randint(2, 5)}/{random.randint(5, 8)}",
        random.choice(study_styles),
        f"Auto-generated group for {', '.join(topics)} in {class_code}."
    ))
    conn.commit()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Inserted group {group_id}")

    cursor.execute("""SELECT * FROM StudyGroups;""")