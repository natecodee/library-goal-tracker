from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID
import re

from app.core.supabase_client import get_supabase

router = APIRouter(prefix="/extracted-goals", tags=["extracted-goals"])


class ExtractedGoalUpdate(BaseModel):
    status: Optional[str] = None
    strategic_goal_id: Optional[str] = None
    suggested_code: Optional[str] = None
    confidence: Optional[float] = None
    reviewer_id: Optional[str] = None
    decided_at: Optional[datetime] = None
    note: Optional[str] = None
    goal_text: Optional[str] = None
    normalized_text: Optional[str] = None


class ExtractedGoalDecision(BaseModel):
    status: str
    strategic_goal_id: Optional[str] = None
    note: Optional[str] = None
    reviewer_id: Optional[str] = None


VALID_STATUSES = {"suggested", "approved", "rejected", "created"}


def normalize_goal(text: str) -> str:
    if not text:
        return ""
    normalized = text.strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


@router.get("")
def list_extracted_goals(
    document_id: UUID = Query(..., description="Document ID to filter by"),
    status: Optional[str] = Query(None, description="Filter by status (suggested, approved, rejected, created)"),
):
    sb = get_supabase()

    if status is not None and status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status filter. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
        )

    try:
        query = sb.table("extracted_goals").select("*").eq("document_id", str(document_id))

        if status:
            query = query.eq("status", status)

        res = query.order("id", desc=False).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

    return {"items": res.data or []}


@router.patch("/{goal_id}")
def update_extracted_goal(goal_id: UUID, payload: ExtractedGoalUpdate):
    sb = get_supabase()

    if payload.status is not None and payload.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
        )

    update_data = payload.model_dump(exclude_unset=True)

    # If goal_text is updated, also update normalized_text
    if "goal_text" in update_data:
        if update_data["goal_text"]:
            update_data["normalized_text"] = normalize_goal(update_data["goal_text"])
        else:
            raise HTTPException(
                status_code=400,
                detail="goal_text cannot be empty (normalized_text is required)",
            )

    # If normalized_text is explicitly provided without goal_text
    if "normalized_text" in update_data and "goal_text" not in update_data:
        if not update_data["normalized_text"]:
            raise HTTPException(
                status_code=400,
                detail="normalized_text cannot be empty (NOT NULL constraint)",
            )

    # If status -> approved/rejected, set decided_at if not provided
    if payload.status in ("approved", "rejected") and "decided_at" not in update_data:
        update_data["decided_at"] = datetime.now(timezone.utc).isoformat()

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    try:
        existing = (
            sb.table("extracted_goals")
            .select("id")
            .eq("id", str(goal_id))
            .single()
            .execute()
        )
        if not existing.data:
            raise HTTPException(status_code=404, detail="Extracted goal not found")

        res = (
            sb.table("extracted_goals")
            .update(update_data)
            .eq("id", str(goal_id))
            .execute()
        )

        if not res.data:
            raise HTTPException(status_code=500, detail="Update returned no row")

        return {"id": str(goal_id), "updated": res.data[0]}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {e}")


@router.post("/{goal_id}/decision")
def make_decision(goal_id: UUID, payload: ExtractedGoalDecision):
    sb = get_supabase()

    if payload.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
        )

    update_data = {"status": payload.status}

    if payload.strategic_goal_id is not None:
        update_data["strategic_goal_id"] = payload.strategic_goal_id
    if payload.note is not None:
        update_data["note"] = payload.note
    if payload.reviewer_id is not None:
        update_data["reviewer_id"] = payload.reviewer_id

    if payload.status in ("approved", "rejected"):
        update_data["decided_at"] = datetime.now(timezone.utc).isoformat()

    try:
        existing = (
            sb.table("extracted_goals")
            .select("id")
            .eq("id", str(goal_id))
            .single()
            .execute()
        )
        if not existing.data:
            raise HTTPException(status_code=404, detail="Extracted goal not found")

        res = (
            sb.table("extracted_goals")
            .update(update_data)
            .eq("id", str(goal_id))
            .execute()
        )

        if not res.data:
            raise HTTPException(status_code=500, detail="Update returned no row")

        return {"id": str(goal_id), "updated": res.data[0]}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision update failed: {e}")
