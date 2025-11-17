import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "taiga_sync.db"
MAP_PATH = BASE_DIR / "util" / "llm-docs-proyect" / "mapa-proyect.json"


def parse_iso(value: Optional[str]) -> str:
    if not value:
        return datetime.utcnow().isoformat()
    return value


def ensure_tag(
    cursor: sqlite3.Cursor,
    project_id: int,
    name: str,
    color: Optional[str] = None,
) -> int:
    cursor.execute(
        "SELECT id FROM tags WHERE project_id = ? AND name = ?", (project_id, name)
    )
    row = cursor.fetchone()
    if row:
        tag_id = row[0]
        if color:
            cursor.execute(
                "UPDATE tags SET color = ? WHERE id = ?", (color, tag_id)
            )
        return tag_id
    cursor.execute(
        "INSERT INTO tags (project_id, name, color, last_synced) VALUES (?, ?, ?, ?)",
        (project_id, name, color or "#6c757d", datetime.utcnow().isoformat()),
    )
    return cursor.lastrowid


def associate_user_story_tag(cursor: sqlite3.Cursor, story_id: int, tag_id: int):
    cursor.execute(
        "SELECT 1 FROM user_story_tags WHERE user_story_id = ? AND tag_id = ?",
        (story_id, tag_id),
    )
    if cursor.fetchone():
        return
    cursor.execute(
        "INSERT INTO user_story_tags (user_story_id, tag_id) VALUES (?, ?)",
        (story_id, tag_id),
    )


def associate_task_tag(cursor: sqlite3.Cursor, task_id: int, tag_id: int):
    cursor.execute(
        "SELECT 1 FROM task_tags WHERE task_id = ? AND tag_id = ?",
        (task_id, tag_id),
    )
    if cursor.fetchone():
        return
    cursor.execute(
        "INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)",
        (task_id, tag_id),
    )


def upsert_task(
    cursor: sqlite3.Cursor,
    project_id: int,
    story_id: int,
    task_data: Dict,
    tag_cache: Dict[str, int],
) -> int:
    taiga_task_id = task_data.get("id")
    cursor.execute("SELECT id FROM tasks WHERE taiga_id = ?", (taiga_task_id,))
    existing = cursor.fetchone()
    subject = task_data.get("subject") or ""
    status_name = task_data.get("status_extra_info", {}).get("name") or ""
    ref = task_data.get("ref")
    created_date = parse_iso(task_data.get("created_date"))
    modified_date = parse_iso(task_data.get("modified_date"))

    if existing:
        task_id = existing[0]
        cursor.execute(
            """
            UPDATE tasks
            SET subject = ?, status_name = ?, modified_date = ?, project_id = ?, user_story_id = ?
            WHERE id = ?
            """,
            (subject, status_name, modified_date, project_id, story_id, task_id),
        )
    else:
        cursor.execute(
            """
            INSERT INTO tasks
                (taiga_id, project_id, user_story_id, ref, subject, description, status_name,
                 is_closed, version, created_date, modified_date, raw_data, last_synced)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                taiga_task_id,
                project_id,
                story_id,
                ref,
                subject,
                task_data.get("description") or "",
                status_name,
                int(task_data.get("is_closed", False)),
                task_data.get("version") or 1,
                created_date,
                modified_date,
                json.dumps(task_data),
                datetime.utcnow().isoformat(),
            ),
        )
        task_id = cursor.lastrowid

    tags = task_data.get("tags") or []
    for tag_entry in tags:
        if isinstance(tag_entry, list):
            tag_name = tag_entry[0]
            tag_color = tag_entry[1] if len(tag_entry) > 1 else None
        else:
            tag_name = str(tag_entry)
            tag_color = None
        tag_id = tag_cache.get(tag_name)
        if not tag_id:
            tag_id = ensure_tag(cursor, project_id, tag_name, tag_color)
            tag_cache[tag_name] = tag_id
        associate_task_tag(cursor, task_id, tag_id)

    return task_id


def import_map():
    if not MAP_PATH.exists():
        raise FileNotFoundError(f"{MAP_PATH} not found")

    with open(MAP_PATH) as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    taiga_project_id = data.get("project")
    cursor.execute("SELECT id FROM projects WHERE taiga_id = ?", (taiga_project_id,))
    project_row = cursor.fetchone()
    if not project_row:
        raise RuntimeError(f"Project {taiga_project_id} not found in database.")
    project_id = project_row[0]
    tag_cache = {}

    cursor.execute(
        "SELECT name, id FROM tags WHERE project_id = ?", (project_id,)
    )
    for name, tag_id in cursor.fetchall():
        tag_cache[name] = tag_id

    total_stories = 0
    total_tasks = 0

    for epic in data.get("epics", []):
        for us_data in epic.get("user_stories", []):
            ref = us_data.get("ref")
            cursor.execute(
                "SELECT id FROM user_stories WHERE ref = ? AND project_id = ?",
                (ref, project_id),
            )
            row = cursor.fetchone()
            if not row:
                continue
            story_id = row[0]
            total_stories += 1

            milestone = us_data.get("milestone_name") or "MVP"
            version = us_data.get("version") or 1
            modified_date = parse_iso(us_data.get("modified_date"))
            cursor.execute(
                """
                UPDATE user_stories
                SET version = ?, milestone_name = ?, modified_date = ?
                WHERE id = ?
                """,
                (version, milestone, modified_date, story_id),
            )

            tags = us_data.get("tags") or []
            for tag_entry in tags:
                if isinstance(tag_entry, list):
                    tag_name = tag_entry[0]
                    tag_color = tag_entry[1] if len(tag_entry) > 1 else None
                else:
                    tag_name = str(tag_entry)
                    tag_color = None
                if not tag_name:
                    continue
                tag_id = tag_cache.get(tag_name)
                if not tag_id:
                    tag_id = ensure_tag(cursor, project_id, tag_name, tag_color)
                    tag_cache[tag_name] = tag_id
                associate_user_story_tag(cursor, story_id, tag_id)

            for task in us_data.get("tasks", []):
                upsert_task(cursor, project_id, story_id, task, tag_cache)
                total_tasks += 1

    conn.commit()
    conn.close()
    print(f"Imported map: {total_stories} stories updated, {total_tasks} tasks synced.")


if __name__ == "__main__":
    import_map()
