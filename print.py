import sqlite3

# Open the connection to the DreamImages database
conn = sqlite3.connect('DreamImages.db')
cursor = conn.cursor()

# Fetch all records from the DreamImages table
cursor.execute("SELECT id, image FROM DreamImages")

# Iterate through the records
for row in cursor.fetchall():
    image_id, old_image_path = row
    new_image_path = old_image_path.replace("\\", "/")  # Replace backslashes with forward slashes
    # Update the record with the new image path
    cursor.execute("UPDATE DreamImages SET image = ? WHERE id = ?", (new_image_path, image_id))

# Commit the changes
conn.commit()

# Query all records in the DreamImages table
cursor.execute("SELECT * FROM DreamImages")

# Fetch all rows from the query
rows = cursor.fetchall()

# Print the rows
for row in rows:
    print(row)

# Close the connection to the database
conn.close()
