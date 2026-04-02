"""Tech Sensing API routes."""

import asyncio
import json
import os
import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


class SensingRunRequest(BaseModel):
    domain: str = "Generative AI"
    lookback_days: int = 7
    user_id: str = "default"
    custom_requirements: str = ""
    must_include: list[str] = Field(default_factory=list)
    dont_include: list[str] = Field(default_factory=list)
    feed_urls: list[str] = Field(default_factory=list)
    search_queries: list[str] = Field(default_factory=list)
    key_people: list[str] = Field(default_factory=list)


# In-memory task tracker
_tasks: dict[str, dict] = {}


@router.post("/run")
async def run_sensing(req: SensingRunRequest, background_tasks: BackgroundTasks):
    """Trigger async sensing pipeline execution."""
    tracking_id = uuid.uuid4().hex[:12]
    _tasks[tracking_id] = {"status": "running", "progress": 0, "message": "Starting..."}

    async def _execute():
        try:
            from enterprise_skills_lib.sensing.pipeline import run_sensing_pipeline

            async def progress(stage, pct, msg=""):
                _tasks[tracking_id] = {"status": "running", "progress": pct, "message": msg}

            result = await run_sensing_pipeline(
                domain=req.domain,
                custom_requirements=req.custom_requirements,
                feed_urls=req.feed_urls or None,
                search_queries=req.search_queries or None,
                must_include=req.must_include or None,
                dont_include=req.dont_include or None,
                lookback_days=req.lookback_days,
                progress_callback=progress,
                user_id=req.user_id,
                key_people=req.key_people or None,
            )

            output_dir = os.path.join("data", req.user_id, "sensing")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"report_{tracking_id}.json")

            report_data = result.report.model_dump(mode="json")
            report_data["_meta"] = {
                "tracking_id": tracking_id,
                "domain": req.domain,
                "raw_article_count": result.raw_article_count,
                "deduped_article_count": result.deduped_article_count,
                "classified_article_count": result.classified_article_count,
                "execution_time_seconds": result.execution_time_seconds,
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            _tasks[tracking_id] = {
                "status": "completed",
                "progress": 100,
                "output_path": output_path,
                "stats": {
                    "raw": result.raw_article_count,
                    "unique": result.deduped_article_count,
                    "classified": result.classified_article_count,
                    "time_seconds": result.execution_time_seconds,
                },
            }
        except Exception as e:
            _tasks[tracking_id] = {"status": "error", "progress": 0, "message": str(e)}

    background_tasks.add_task(_execute)
    return {"tracking_id": tracking_id, "status": "started"}


@router.get("/status/{tracking_id}")
async def sensing_status(tracking_id: str):
    """Poll execution status."""
    if tracking_id not in _tasks:
        raise HTTPException(404, "Task not found")
    return _tasks[tracking_id]


@router.get("/history")
async def sensing_history(user_id: str = Query("default")):
    """List past sensing reports."""
    reports_dir = os.path.join("data", user_id, "sensing")
    if not os.path.isdir(reports_dir):
        return {"reports": []}

    reports = []
    for fname in sorted(os.listdir(reports_dir), reverse=True):
        if not fname.startswith("report_") or not fname.endswith(".json"):
            continue
        fpath = os.path.join(reports_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            meta = data.get("_meta", {})
            reports.append({
                "tracking_id": meta.get("tracking_id", fname),
                "domain": meta.get("domain", ""),
                "generated_at": meta.get("generated_at", ""),
                "title": data.get("report_title", ""),
            })
        except Exception:
            continue

    return {"reports": reports}


@router.delete("/report/{tracking_id}")
async def delete_report(tracking_id: str, user_id: str = Query("default")):
    """Delete a sensing report."""
    path = os.path.join("data", user_id, "sensing", f"report_{tracking_id}.json")
    if not os.path.exists(path):
        raise HTTPException(404, "Report not found")
    os.remove(path)
    return {"status": "deleted", "tracking_id": tracking_id}
