"""Schedule management API routes."""

import asyncio
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


class ScheduleCreateRequest(BaseModel):
    user_id: str = "default"
    domain: str = "Generative AI"
    frequency: str = "weekly"  # daily|weekly|biweekly|monthly
    must_include: list[str] = Field(default_factory=list)
    dont_include: list[str] = Field(default_factory=list)
    email: Optional[str] = None


class ScheduleUpdateRequest(BaseModel):
    frequency: Optional[str] = None
    must_include: Optional[list[str]] = None
    dont_include: Optional[list[str]] = None
    email: Optional[str] = None


@router.post("")
async def create_schedule(req: ScheduleCreateRequest):
    """Create a recurring schedule."""
    from enterprise_skills_lib.sensing.scheduler import add_schedule

    schedule_id = await add_schedule(
        user_id=req.user_id,
        domain=req.domain,
        frequency=req.frequency,
        must_include=req.must_include or None,
        dont_include=req.dont_include or None,
        email=req.email,
    )
    return {"schedule_id": schedule_id, "status": "created"}


@router.get("")
async def list_schedules(user_id: str = Query("default")):
    """List user's schedules."""
    from enterprise_skills_lib.sensing.scheduler import list_schedules as _list

    schedules = await _list(user_id=user_id)
    return {
        "schedules": [
            s.model_dump(mode="json") if hasattr(s, "model_dump") else s
            for s in schedules
        ],
    }


@router.put("/{schedule_id}")
async def update_schedule(schedule_id: str, req: ScheduleUpdateRequest):
    """Update a schedule."""
    from enterprise_skills_lib.sensing.scheduler import update_schedule as _update

    await _update(schedule_id=schedule_id, frequency=req.frequency)
    return {"status": "updated", "schedule_id": schedule_id}


@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: str):
    """Delete a schedule."""
    from enterprise_skills_lib.sensing.scheduler import remove_schedule

    await remove_schedule(schedule_id=schedule_id)
    return {"status": "deleted", "schedule_id": schedule_id}
