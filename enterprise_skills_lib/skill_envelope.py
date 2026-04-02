"""
Universal output envelope for all skills — standardized cross-skill data contract.
"""

import json
import os
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class SkillOutputEnvelope(BaseModel):
    """Universal wrapper for all skill outputs."""

    skill_name: str
    version: str = "1.0"
    tracking_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    user_id: str = "default"
    domain: str = ""
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    execution_time_seconds: float = 0.0
    status: str = "completed"  # "completed"|"partial"|"failed"
    report: dict = Field(default_factory=dict)
    meta: dict = Field(default_factory=dict)


def save_skill_output(
    skill_name: str,
    user_id: str,
    report_data: dict,
    domain: str = "",
    execution_time: float = 0.0,
    meta: dict | None = None,
) -> tuple[str, str]:
    """
    Save a skill output in the standard envelope format.

    Returns (tracking_id, output_path).
    """
    envelope = SkillOutputEnvelope(
        skill_name=skill_name,
        user_id=user_id,
        domain=domain,
        execution_time_seconds=execution_time,
        report=report_data,
        meta=meta or {},
    )

    output_dir = os.path.join("data", user_id, skill_name)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"report_{envelope.tracking_id}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(envelope.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    return envelope.tracking_id, output_path


def load_latest_skill_output(
    skill_name: str,
    user_id: str,
) -> SkillOutputEnvelope | None:
    """Load the most recent output for a skill+user."""
    skill_dir = os.path.join("data", user_id, skill_name)
    if not os.path.isdir(skill_dir):
        return None

    report_files = sorted(
        [f for f in os.listdir(skill_dir) if f.startswith("report_") and f.endswith(".json")],
        key=lambda f: os.path.getmtime(os.path.join(skill_dir, f)),
        reverse=True,
    )

    if not report_files:
        return None

    path = os.path.join(skill_dir, report_files[0])
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return SkillOutputEnvelope.model_validate(data)
    except Exception:
        return None
