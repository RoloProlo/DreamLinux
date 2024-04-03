import sqlite3

# Open the connection to the DreamImages database
conn = sqlite3.connect('DreamImages.db')
cursor = conn.cursor()

# Fetch all records from the DreamImages table
cursor.execute("SELECT id, image FROM DreamImages")

# Query all records in the DreamImages table
cursor.execute("SELECT id, image FROM DreamImages")
for row in cursor.fetchall():
    print("old", row)

# Fetch all rows from the query
cursor.execute("SELECT id, image FROM DreamImages")
for row in cursor.fetchall():
    image_id, old_image_path = row
    new_image_path = old_image_path.replace("\\", "/")
    print("new: ", new_image_path)
    cursor.execute("UPDATE DreamImages SET image = ? WHERE id = ?", (new_image_path, image_id))

conn.commit()


# Close the connection to the database
conn.close()
