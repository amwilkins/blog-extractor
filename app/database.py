import re
import sqlite3
from typing import Optional


def save_to_db(url: str, title: str, html: str, content: str, success: bool):
    """Save the extracted blog content to an SQLite database."""
    conn = sqlite3.connect("blog_data.sqlite")  # Local file-based database
    cur = conn.cursor()

    # use url to make table name
    match = re.search(r"https?://(?:www\.)?([^/.]+)", url)
    table_name = match.group(1) if match else None

    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            url TEXT PRIMARY KEY,
            title TEXT,
            html TEXT,
            content TEXT,
            success BOOLEAN
            retrieval_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """
    cur.execute(create_table_query)

    insert_query = f"INSERT INTO {table_name} (url, title, html, content, success, retrieval_date) VALUES (?, ?, ?, ?, ?, ?)"
    cur.execute(insert_query, (url, title, html, content, success))

    conn.commit()
    cur.close()
    conn.close()


def read_db(db_path: str, url: str, table_name) -> Optional[tuple]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT url, title, html, content, success, retrieval_date FROM {table_name} WHERE url = ?",
        (url,),
    )
    result = cursor.fetchone()
    conn.close()
    return result
