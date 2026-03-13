import sqlite3
import random

# Data pools
class_codes = ["CS101", "BIO20", "MATH23", "PHYS2B", "HIST10"]
topics = ["Recursion", "Sorting", "DNA Replication", "Cold War", "Electric Fields"]
modes = ["remote", "in_person"]
locations = ["McHenry Library", "Science Library", "Stevenson Coffeehouse"]
time_blocks = ["8-11am", "2-5pm", "6-9pm"]

# Generate random users
def generate_random_users(conn, num_users=10):
    cursor = conn.cursor()
    for i in range(num_users):
        name = f"User{i+1}"
        class_code = random.choice(class_codes)
        user_topics = ",".join(random.sample(topics, random.randint(1, 3)))
        mode = random.choice(modes)
        availability = ",".join(random.sample(time_blocks, random.randint(1, 2)))
        location = random.choice(locations)

        cursor.execute("""
            INSERT INTO users (name, class_code, topics, mode, availability, location)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, class_code, user_topics, mode, availability, location))
    conn.commit()

