import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

DB_PATH = "taiga_sync.db"
TAIGA_BASE_URL = "http://localhost:8001"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYzMzIzNTEyLCJqdGkiOiI5MmI5NTlmOTI5NWI0NjY4YjRiMzBiNzg1YzU5Y2U0OSIsInVzZXJfaWQiOjUwfQ.jsZVkD1zEeazETa6tSnJeYbRaE8oTt8coJX9499awrM"
PROJECT_SLUG = "dai-declaracion-aduanera-integral"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_tag(cursor: sqlite3.Cursor, project_id: int, name: str, color: Optional[str] = None) -> int:
    if not name:
        raise ValueError("Tag name is required")
    cursor.execute("SELECT id FROM tags WHERE project_id = ? AND name = ?", (project_id, name))
    row = cursor.fetchone()
    if row:
        tag_id = row[0]
        if color:
            cursor.execute("UPDATE tags SET color = ? WHERE id = ?", (color, tag_id))
        return tag_id
    cursor.execute(
        "INSERT INTO tags (project_id, name, color, last_synced) VALUES (?, ?, ?, ?)",
        (project_id, name, color or "#6c757d", now_iso()),
    )
    return cursor.lastrowid


def associate_user_story_tag(cursor: sqlite3.Cursor, story_id: int, tag_id: int):
    cursor.execute(
        "SELECT 1 FROM user_story_tags WHERE user_story_id = ? AND tag_id = ?", (story_id, tag_id)
    )
    if cursor.fetchone():
        return
    cursor.execute(
        "INSERT INTO user_story_tags (user_story_id, tag_id) VALUES (?, ?)", (story_id, tag_id)
    )


def associate_task_tag(cursor: sqlite3.Cursor, task_id: int, tag_id: int):
    cursor.execute("SELECT 1 FROM task_tags WHERE task_id = ? AND tag_id = ?", (task_id, tag_id))
    if cursor.fetchone():
        return
    cursor.execute("INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)", (task_id, tag_id))


def upsert_task(
    cursor: sqlite3.Cursor,
    story_id: int,
    project_id: int,
    task_data: Dict[str, Any],
    tag_cache: Dict[str, int],
) -> int:
    taiga_id = task_data.get("id")
    cursor.execute("SELECT id FROM tasks WHERE taiga_id = ?", (taiga_id,))
    existing = cursor.fetchone()
    subject = task_data.get("subject") or ""
    status_name = task_data.get("status_extra_info", {}).get("name") or ""
    ref = task_data.get("ref")
    created = task_data.get("created_date") or now_iso()
    modified = task_data.get("modified_date") or now_iso()
    description = task_data.get("description") or ""

    if existing:
        task_id = existing[0]
        cursor.execute(
            """
            UPDATE tasks
            SET subject = ?, status_name = ?, description = ?, modified_date = ?, user_story_id = ?
            WHERE id = ?
            """,
            (subject, status_name, description, modified, story_id, task_id),
        )
    else:
        cursor.execute(
            """
            INSERT INTO tasks (
                taiga_id, project_id, user_story_id, ref, subject, description, status_name,
                is_closed, version, created_date, modified_date, raw_data, last_synced
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                taiga_id,
                project_id,
                story_id,
                ref,
                subject,
                description,
                status_name,
                int(task_data.get("is_closed", False)),
                task_data.get("version") or 1,
                created,
                modified,
                json.dumps(task_data),
                now_iso(),
            ),
        )
        task_id = cursor.lastrowid

    tags = task_data.get("tags") or []
    for tag in tags:
        if isinstance(tag, list):
            tag_name = tag[0]
            tag_color = tag[1] if len(tag) > 1 else None
        else:
            tag_name = str(tag)
            tag_color = None
        if not tag_name:
            continue
        tag_id = tag_cache.get(tag_name)
        if not tag_id:
            tag_id = ensure_tag(cursor, project_id, tag_name, tag_color)
            tag_cache[tag_name] = tag_id
        associate_task_tag(cursor, task_id, tag_id)

    return task_id


def authenticate(session: requests.Session) -> None:
    resp = session.post(
        f"{TAIGA_BASE_URL}/auth",
        headers={"Content-Type": "application/json"},
        json={"token": AUTH_TOKEN},
        timeout=30,
    )
    resp.raise_for_status()


def fetch_user_stories(session: requests.Session) -> List[Dict[str, Any]]:
    params = {
        "project": PROJECT_SLUG,
        "include_tasks": "true",
    }
    resp = session.get(f"{TAIGA_BASE_URL}/user-stories", params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def import_from_api():
    session = requests.Session()
    authenticate(session)
    data = fetch_user_stories(session)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, taiga_id FROM projects WHERE taiga_id = ?", (3,))
    project_row = cursor.fetchone()
    if not project_row:
        raise RuntimeError("Project ID 3 not found")
    project_id = project_row[0]
    tag_cache: Dict[str, int] = {}
    cursor.execute("SELECT name, id FROM tags WHERE project_id = ?", (project_id,))
    for name, tag_id in cursor.fetchall():
        tag_cache[name] = tag_id

    for story in data:
        taiga_id = story["id"]
        cursor.execute("SELECT id FROM user_stories WHERE taiga_id = ?", (taiga_id,))
        row = cursor.fetchone()
        if not row:
            continue
        story_id = row[0]
        cursor.execute(
            """
            UPDATE user_stories
            SET description = ?, modified_date = ?, version = ?, milestone_name = ?, raw_data = ?
            WHERE id = ?
            """,
            (
                story.get("description"),
                story.get("modified_date") or now_iso(),
                story.get("version") or 1,
                story.get("milestone_name") or "MVP",
                json.dumps(story),
                story_id,
            ),
        )
        story_tags = story.get("tags") or []
        for tag in story_tags:
            if isinstance(tag, list):
                tag_name = tag[0]
                tag_color = tag[1] if len(tag) > 1 else None
            else:
                tag_name = str(tag)
                tag_color = None
            if not tag_name:
                continue
            tag_id = tag_cache.get(tag_name)
            if not tag_id:
                tag_id = ensure_tag(cursor, project_id, tag_name, tag_color)
                tag_cache[tag_name] = tag_id
            associate_user_story_tag(cursor, story_id, tag_id)

        for task in story.get("tasks") or []:
            upsert_task(cursor, story_id, project_id, task, tag_cache)

    conn.commit()
    conn.close()
    print(f"Imported {len(data)} stories from API.")


if __name__ == "__main__":
    import_from_api()
