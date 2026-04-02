"""Tests for collaboration CRUD operations."""

import json
import os

import pytest

from enterprise_skills_lib.sensing.collaboration import (
    add_comment,
    add_vote,
    get_shared_report,
    share_report,
)


@pytest.fixture
def clean_shared_dir(tmp_path, monkeypatch):
    """Redirect shared reports to temp dir."""
    shared_dir = tmp_path / "data" / "shared_reports"
    shared_dir.mkdir(parents=True)
    monkeypatch.setattr(
        "enterprise_skills_lib.sensing.collaboration.SHARED_REPORTS_DIR",
        str(shared_dir),
    )
    return shared_dir


@pytest.mark.asyncio
async def test_share_report(clean_shared_dir):
    share_id = await share_report(tracking_id="test123", user_id="testuser")
    assert share_id is not None
    assert len(share_id) > 0

    # Verify file was created
    files = list(clean_shared_dir.iterdir())
    assert len(files) == 1


@pytest.mark.asyncio
async def test_get_shared_report(clean_shared_dir):
    share_id = await share_report(tracking_id="test456", user_id="testuser")
    report = await get_shared_report(share_id=share_id)
    assert report is not None
    assert report.tracking_id == "test456"


@pytest.mark.asyncio
async def test_add_vote(clean_shared_dir):
    share_id = await share_report(tracking_id="test789", user_id="testuser")
    await add_vote(share_id=share_id, user_id="voter1", item_name="GPT-5", proposed_ring="Adopt")

    report = await get_shared_report(share_id=share_id)
    assert len(report.votes) == 1
    assert report.votes[0].item_name == "GPT-5"


@pytest.mark.asyncio
async def test_add_comment(clean_shared_dir):
    share_id = await share_report(tracking_id="testabc", user_id="testuser")
    await add_comment(share_id=share_id, user_id="commenter1", text="Great analysis!")

    report = await get_shared_report(share_id=share_id)
    assert len(report.comments) == 1
    assert report.comments[0].text == "Great analysis!"
