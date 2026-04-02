"""Generic skill execution API routes."""

import asyncio
import json
import os
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()

# In-memory task tracker shared across skills
_skill_tasks: dict[str, dict] = {}

SKILL_DIR_MAP = {
    "competitive_intel": "competitive",
    "patent_monitor": "patents",
    "regulation_tracker": "regulations",
    "talent_radar": "talent",
}


class SkillRunRequest(BaseModel):
    user_id: str = "default"
    domain: str = "Generative AI"
    params: dict = Field(default_factory=dict,
                         description="Skill-specific parameters")


@router.post("/{skill_name}/run")
async def run_skill(skill_name: str, req: SkillRunRequest, background_tasks: BackgroundTasks):
    """Trigger async skill execution."""
    if skill_name == "tech_sensing":
        raise HTTPException(400, "Use /skills/tech_sensing/run endpoint instead")

    tracking_id = uuid.uuid4().hex[:12]
    _skill_tasks[tracking_id] = {"status": "running", "skill": skill_name}

    async def _execute():
        try:
            from enterprise_skills_lib.constants import GPU_SENSING_REPORT_LLM, PORT1
            from enterprise_skills_lib.llm.client import invoke_llm
            from enterprise_skills_lib.sensing.ingest import search_duckduckgo
            from enterprise_skills_lib.sensing.dedup import deduplicate_articles

            # Generic ingest
            queries = req.params.get("queries", [f"{req.domain} news"])
            lookback = req.params.get("lookback_days", 30)
            ddg = await search_duckduckgo(queries, req.domain, lookback_days=lookback)
            unique = deduplicate_articles(ddg)

            articles_text = ""
            for a in unique[:30]:
                articles_text += f"TITLE: {a.title}\nURL: {a.url}\nCONTENT: {a.snippet[:400]}\n\n"

            # Route to appropriate schema and prompt
            if skill_name == "competitive_intel":
                from enterprise_skills_lib.llm.output_schemas.competitive import CompetitiveReport
                from enterprise_skills_lib.llm.prompts.competitive_prompts import competitive_analysis_prompt
                companies = req.params.get("companies", ["Unknown"])
                messages = competitive_analysis_prompt(articles_text, companies, req.domain)
                result = await invoke_llm(GPU_SENSING_REPORT_LLM.model, CompetitiveReport, messages, PORT1)
            elif skill_name == "patent_monitor":
                from enterprise_skills_lib.llm.output_schemas.patents import PatentReport
                from enterprise_skills_lib.llm.prompts.patent_prompts import patent_analysis_prompt
                messages = patent_analysis_prompt(articles_text, req.domain)
                result = await invoke_llm(GPU_SENSING_REPORT_LLM.model, PatentReport, messages, PORT1)
            elif skill_name == "regulation_tracker":
                from enterprise_skills_lib.llm.output_schemas.regulations import RegulationReport
                from enterprise_skills_lib.llm.prompts.regulation_prompts import regulation_scan_prompt
                jurisdictions = req.params.get("jurisdictions", ["EU", "US"])
                messages = regulation_scan_prompt(articles_text, [req.domain], jurisdictions)
                result = await invoke_llm(GPU_SENSING_REPORT_LLM.model, RegulationReport, messages, PORT1)
            elif skill_name == "talent_radar":
                from enterprise_skills_lib.llm.output_schemas.talent import TalentReport
                from enterprise_skills_lib.llm.prompts.talent_prompts import talent_scan_prompt
                roles = req.params.get("roles", ["AI Engineer"])
                messages = talent_scan_prompt(articles_text, roles)
                result = await invoke_llm(GPU_SENSING_REPORT_LLM.model, TalentReport, messages, PORT1)
            else:
                _skill_tasks[tracking_id] = {"status": "error", "message": f"Unknown skill: {skill_name}"}
                return

            # Save
            skill_dir = SKILL_DIR_MAP.get(skill_name, skill_name)
            output_dir = os.path.join("data", req.user_id, skill_dir)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"report_{tracking_id}.json")

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

            _skill_tasks[tracking_id] = {
                "status": "completed",
                "output_path": output_path,
                "skill": skill_name,
            }
        except Exception as e:
            _skill_tasks[tracking_id] = {"status": "error", "message": str(e), "skill": skill_name}

    background_tasks.add_task(_execute)
    return {"tracking_id": tracking_id, "status": "started", "skill": skill_name}


@router.get("/{skill_name}/status/{tracking_id}")
async def skill_status(skill_name: str, tracking_id: str):
    """Poll skill execution status."""
    if tracking_id not in _skill_tasks:
        raise HTTPException(404, "Task not found")
    return _skill_tasks[tracking_id]


@router.get("/{skill_name}/history")
async def skill_history(skill_name: str, user_id: str = Query("default")):
    """List past reports for a skill."""
    skill_dir = SKILL_DIR_MAP.get(skill_name, skill_name)
    reports_dir = os.path.join("data", user_id, skill_dir)
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
                "title": data.get("report_title", ""),
                "generated_at": meta.get("generated_at", ""),
            })
        except Exception:
            continue

    return {"reports": reports}


@router.delete("/{skill_name}/report/{tracking_id}")
async def delete_skill_report(skill_name: str, tracking_id: str, user_id: str = Query("default")):
    """Delete a skill report."""
    skill_dir = SKILL_DIR_MAP.get(skill_name, skill_name)
    path = os.path.join("data", user_id, skill_dir, f"report_{tracking_id}.json")
    if not os.path.exists(path):
        raise HTTPException(404, "Report not found")
    os.remove(path)
    return {"status": "deleted"}
