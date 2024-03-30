import sqlite3

# Open the connection to the DreamImages database
conn = sqlite3.connect('DreamImages.db')
cursor = conn.cursor()

# Query all records in the DreamImages table
cursor.execute("SELECT * FROM DreamImages")

# Fetch all rows from the query
rows = cursor.fetchall()

# Print the rows
for row in rows:
    print(row)

# Close the connection to the database
conn.close()
