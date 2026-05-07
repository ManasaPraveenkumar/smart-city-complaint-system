import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    description TEXT,
    category TEXT,
    location TEXT,
    status TEXT DEFAULT 'Pending'
)
''')

#cursor.execute("ALTER TABLE complaints ADD COLUMN image TEXT")

#cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")

#cursor.execute("ALTER TABLE complaints ADD COLUMN date TEXT")

#cursor.execute("DELETE FROM complaints")

conn.commit()
conn.close()

print("Database created successfully!")