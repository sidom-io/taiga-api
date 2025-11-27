from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
from urllib.parse import urlparse, parse_qs

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.metrics_exporter import MetricsExporter
from app.crud import get_project_by_taiga_id, get_project_by_slug

router = APIRouter()

class SimpleJsonTarget(BaseModel):
    target: str
    refId: str
    type: str = "table"

class SimpleJsonQuery(BaseModel):
    range: Dict[str, Any]
    interval: str = "30s"
    targets: List[SimpleJsonTarget]
    maxDataPoints: int = 100
    scopedVars: Dict[str, Any] = {}

async def _resolve_project(db: AsyncSession, identifier: Union[int, str]):
    try:
        taiga_id = int(identifier)
        return await get_project_by_taiga_id(db, taiga_id)
    except (ValueError, TypeError):
        return await get_project_by_slug(db, str(identifier))

@router.get("/")
async def health_check():
    return {"status": "ok"}

@router.post("/search")
async def search():
    return [
        "sprint-velocity",
        "stuck-tasks",
        "activity-feed",
        "project-summary"
    ]

@router.post("/query")
async def query(query: SimpleJsonQuery, db: AsyncSession = Depends(get_db)):
    results = []

    exporter = MetricsExporter(db)

    for target in query.targets:
        # Parse target string (e.g. "/metrics/sprint-velocity?project=3")
        # If it's just a name, handle it too
        target_name = target.target
        params = {}

        if "?" in target_name:
            parsed = urlparse(target_name)
            target_name = parsed.path
            query_params = parse_qs(parsed.query)
            # Flatten params (parse_qs returns lists)
            params = {k: v[0] for k, v in query_params.items()}

        # Normalize target name
        if target_name.startswith("/metrics/"):
            target_name = target_name.replace("/metrics/", "")

        project_id_or_slug = params.get("project")
        if not project_id_or_slug:
            # Try to find project in scopedVars if not in URL
            if "project" in query.scopedVars:
                project_id_or_slug = query.scopedVars["project"].get("value")

        if not project_id_or_slug:
            continue

        project = await _resolve_project(db, project_id_or_slug)
        if not project:
            continue

        if target_name == "sprint-velocity":
            sprint_count = int(params.get("sprint_count", 6))
            metrics = await exporter.get_sprint_velocity(project.id, sprint_count)

            # Convert to Table
            columns = [
                {"text": "Sprint", "type": "string"},
                {"text": "Tasks Completed", "type": "number"},
                {"text": "Story Points", "type": "number"}
            ]
            rows = []
            for m in metrics:
                rows.append([
                    m["sprint_id"],
                    m["tasks_completed"],
                    m["story_points"]
                ])

            results.append({
                "target": target.target,
                "type": "table",
                "columns": columns,
                "rows": rows
            })

        elif target_name == "stuck-tasks":
            days = int(params.get("days_threshold", 5))
            tasks = await exporter.get_stuck_tasks(project.id, days)

            # For Gauge, we need a value. But dashboard also has a Table.
            # We return a Table with all details.
            # The Gauge panel can use the Table data if configured to pick a column.
            # Or we can add a "total_stuck" column to every row?
            # Better: Return the detailed table.

            columns = [
                {"text": "ID", "type": "number"},
                {"text": "Ref", "type": "number"},
                {"text": "Subject", "type": "string"},
                {"text": "Status", "type": "string"},
                {"text": "Days Stuck", "type": "number"},
                {"text": "Severity", "type": "string"},
                {"text": "Assigned To", "type": "string"},
                {"text": "US Ref", "type": "number"}
            ]
            rows = []
            for t in tasks:
                rows.append([
                    t["task_id"],
                    t["ref"],
                    t["subject"],
                    t["status"],
                    t["days_stuck"],
                    t["severity"],
                    t["assigned_to"] or "",
                    t["user_story_ref"] or 0
                ])

            results.append({
                "target": target.target,
                "type": "table",
                "columns": columns,
                "rows": rows
            })

        elif target_name == "activity-feed":
            limit = int(params.get("limit", 50))
            hours = int(params.get("hours", 168))
            activities = await exporter.get_activity_feed(project.id, limit, hours)

            columns = [
                {"text": "Time", "type": "time"}, # Grafana expects time as number (ms) or ISO string
                {"text": "Type", "type": "string"},
                {"text": "Ref", "type": "number"},
                {"text": "Subject", "type": "string"},
                {"text": "Description", "type": "string"},
                {"text": "Author", "type": "string"}
            ]
            rows = []
            for a in activities:
                # Convert ISO string to ms timestamp if possible, or keep string
                # SimpleJson handles ISO strings usually.
                rows.append([
                    a["timestamp"],
                    a["type"],
                    a["ref"],
                    a["subject"],
                    a["description"],
                    a["author"] or ""
                ])

            results.append({
                "target": target.target,
                "type": "table",
                "columns": columns,
                "rows": rows
            })

        elif target_name == "project-summary":
            summary = await exporter.get_project_summary(project.id)

            # Return as a single row table
            columns = [
                {"text": "Epics", "type": "number"},
                {"text": "Total US", "type": "number"},
                {"text": "US Completed", "type": "number"},
                {"text": "Total Tasks", "type": "number"},
                {"text": "Tasks Completed", "type": "number"},
                {"text": "Task Completion %", "type": "number"},
                {"text": "US Completion %", "type": "number"}
            ]
            rows = [[
                summary["epics"],
                summary["user_stories"]["total"],
                summary["user_stories"]["completed"],
                summary["tasks"]["total"],
                summary["tasks"]["completed"],
                summary["completion_rate"]["tasks"],
                summary["completion_rate"]["user_stories"]
            ]]

            results.append({
                "target": target.target,
                "type": "table",
                "columns": columns,
                "rows": rows
            })

    return results

@router.post("/annotations")
async def annotations():
    return []
