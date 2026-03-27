import sqlite3

try:
    conn = sqlite3.connect('blog_social.db')
    cursor = conn.cursor()
    cursor.execute('ALTER TABLE tags ADD COLUMN color VARCHAR(20) DEFAULT "#409EFF"')
    cursor.execute('ALTER TABLE tags ADD COLUMN description VARCHAR(255)')
    conn.commit()
    print("Columns added successfully")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()