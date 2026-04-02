"""
FastAPI REST API layer for the CoPaw Enterprise Skills Platform.

Wraps skill scripts as HTTP endpoints with async execution and Socket.IO progress.
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure enterprise_skills_lib is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.routes import schedules, sensing, skills
from api.socket_handler import sio_app

app = FastAPI(
    title="CoPaw Enterprise Skills Platform",
    version="1.0.0",
    description="Multi-skill enterprise intelligence platform powered by CoPaw",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(sensing.router, prefix="/skills/tech_sensing", tags=["Tech Sensing"])
app.include_router(skills.router, prefix="/skills", tags=["Skills"])
app.include_router(schedules.router, prefix="/schedules", tags=["Schedules"])

# Mount Socket.IO
app.mount("/ws", sio_app)


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


# ── Cross-skill endpoints ──


class BriefRequest(BaseModel):
    user_id: str = "default"
    domain: str = "Generative AI"
    input_reports: list[str] = Field(default_factory=list,
                                     description="List of 'skill:tracking_id' pairs")


@app.post("/brief/compose")
async def compose_brief(req: BriefRequest, background_tasks: BackgroundTasks):
    """Trigger executive brief composition."""
    tracking_id = uuid.uuid4().hex[:12]

    async def _run():
        from enterprise_skills_lib.constants import GPU_SENSING_REPORT_LLM, PORT1
        from enterprise_skills_lib.llm.client import invoke_llm
        from enterprise_skills_lib.llm.output_schemas.executive import ExecutiveBrief
        from enterprise_skills_lib.llm.prompts.executive_prompts import executive_brief_prompt
        from enterprise_skills_lib.skill_envelope import load_latest_skill_output

        skill_summaries = ""
        for skill_name in ["sensing", "competitive", "patents", "regulations", "talent"]:
            envelope = load_latest_skill_output(skill_name, req.user_id)
            if envelope:
                summary = json.dumps(envelope.report, indent=1, ensure_ascii=False)[:3000]
                skill_summaries += f"\n--- {skill_name.upper()} ---\n{summary}\n"

        if not skill_summaries:
            return

        messages = executive_brief_prompt(skill_summaries=skill_summaries, domain=req.domain)
        brief = await invoke_llm(
            gpu_model=GPU_SENSING_REPORT_LLM.model,
            response_schema=ExecutiveBrief,
            contents=messages,
            port=PORT1,
        )

        output_dir = os.path.join("data", req.user_id, "briefs")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"brief_{tracking_id}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(brief.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    background_tasks.add_task(asyncio.coroutine(_run) if not asyncio.iscoroutinefunction(_run) else _run)
    return {"tracking_id": tracking_id, "status": "started"}


class PptxRequest(BaseModel):
    skill: str
    input_path: str
    output_path: str = "output/deck.pptx"
    template: str = "executive"


@app.post("/pptx/generate")
async def generate_pptx(req: PptxRequest):
    """Generate PPTX from skill output."""
    if not os.path.exists(req.input_path):
        raise HTTPException(404, f"Input file not found: {req.input_path}")

    with open(req.input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "pptx_gen", "scripts"))
    from pptx_engine import add_content_slide, add_title_slide, create_presentation, save_presentation

    prs = create_presentation()
    title = data.get("report_title", data.get("brief_title", "Report"))
    add_title_slide(prs, title, data.get("domain", ""))

    for key, value in data.items():
        if isinstance(value, list) and value and len(value) <= 20:
            bullets = []
            for item in value[:8]:
                if isinstance(item, dict):
                    text_vals = [v for v in item.values() if isinstance(v, str) and len(v) > 3]
                    bullets.append(text_vals[0][:100] if text_vals else str(item)[:100])
                elif isinstance(item, str):
                    bullets.append(item[:100])
            if bullets:
                add_content_slide(prs, key.replace("_", " ").title(), bullets)

    os.makedirs(os.path.dirname(req.output_path) or ".", exist_ok=True)
    save_presentation(prs, req.output_path)
    return {"status": "success", "output": req.output_path}


class DigestRequest(BaseModel):
    to_email: str
    skills: list[str] = ["tech_sensing"]
    user_id: str = "default"
    domain: str = "Generative AI"


@app.post("/digest/send")
async def send_digest(req: DigestRequest):
    """Send a one-time email digest."""
    from enterprise_skills_lib.sensing.email_digest import is_smtp_configured, send_report_email

    if not is_smtp_configured():
        raise HTTPException(503, "SMTP not configured")

    # Build simple HTML
    html = f"<h1>Intelligence Digest: {req.domain}</h1><p>Skills: {', '.join(req.skills)}</p>"
    await send_report_email(to_email=req.to_email, subject=f"Digest: {req.domain}", html_body=html)
    return {"status": "sent", "to": req.to_email}


# ── Collaboration endpoints ──


@app.post("/share/{report_id}")
async def share_report(report_id: str, user_id: str = Query("default")):
    from enterprise_skills_lib.sensing.collaboration import share_report as _share
    share_id = await _share(tracking_id=report_id, user_id=user_id)
    return {"share_id": share_id}


@app.get("/shared/{share_id}")
async def get_shared(share_id: str):
    from enterprise_skills_lib.sensing.collaboration import get_shared_report
    report = await get_shared_report(share_id=share_id)
    if not report:
        raise HTTPException(404, "Shared report not found")
    return report.model_dump(mode="json")


class VoteRequest(BaseModel):
    user_id: str = "default"
    item_name: str
    proposed_ring: str


@app.post("/shared/{share_id}/vote")
async def vote(share_id: str, req: VoteRequest):
    from enterprise_skills_lib.sensing.collaboration import add_vote
    await add_vote(share_id=share_id, user_id=req.user_id,
                   item_name=req.item_name, proposed_ring=req.proposed_ring)
    return {"status": "voted"}


class CommentRequest(BaseModel):
    user_id: str = "default"
    text: str


@app.post("/shared/{share_id}/comment")
async def comment(share_id: str, req: CommentRequest):
    from enterprise_skills_lib.sensing.collaboration import add_comment
    await add_comment(share_id=share_id, user_id=req.user_id, text=req.text)
    return {"status": "commented"}


@app.get("/shared/{share_id}/feedback")
async def feedback(share_id: str):
    from enterprise_skills_lib.sensing.collaboration import get_shared_report
    report = await get_shared_report(share_id=share_id)
    if not report:
        raise HTTPException(404, "Shared report not found")
    return {
        "votes": [v.model_dump(mode="json") for v in report.votes],
        "comments": [c.model_dump(mode="json") for c in report.comments],
    }


# ── Org context endpoints ──


@app.get("/org-context")
async def get_org_context(user_id: str = Query("default")):
    from enterprise_skills_lib.sensing.org_context import load_org_context
    ctx = await load_org_context(user_id=user_id)
    return {"org_context": ctx.model_dump(mode="json") if ctx else None}


class OrgContextUpdate(BaseModel):
    tech_stack: list[str] = []
    industry: str = "Technology"
    priorities: list[str] = []
    competitors: list[str] = []


@app.put("/org-context")
async def update_org_context(req: OrgContextUpdate, user_id: str = Query("default")):
    from enterprise_skills_lib.sensing.org_context import OrgTechContext, save_org_context
    ctx = OrgTechContext(
        tech_stack=req.tech_stack,
        industry=req.industry,
        priorities=req.priorities,
        competitors=req.competitors,
    )
    await save_org_context(user_id=user_id, context=ctx)
    return {"status": "updated"}


# ── Timeline ──


@app.get("/timeline")
async def get_timeline(user_id: str = Query("default"), domain: str = Query("Generative AI")):
    from enterprise_skills_lib.llm.output_schemas.sensing import TechSensingReport
    from enterprise_skills_lib.sensing.timeline import build_timeline

    reports_dir = os.path.join("data", user_id, "sensing")
    if not os.path.isdir(reports_dir):
        return {"timelines": []}

    reports = []
    for fname in sorted(os.listdir(reports_dir)):
        if not fname.startswith("report_") or not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(reports_dir, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
            data.pop("_meta", None)
            reports.append(TechSensingReport.model_validate(data))
        except Exception:
            continue

    timelines = build_timeline(reports)
    return {"timelines": [t.model_dump(mode="json") for t in timelines]}
