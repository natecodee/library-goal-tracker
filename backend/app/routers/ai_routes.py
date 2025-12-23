from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.supabase_client import get_supabase
from app.services.ai import extract_goals

router = APIRouter(prefix="/ai", tags=["ai"])


class ExtractGoalsRequest(BaseModel):
    document_id: str


@router.post("/extract-goals")
def extract_goals_from_document(payload: ExtractGoalsRequest):
    sb = get_supabase()

    # 1) Fetch the document text from DB
    res = sb.table("documents").select("id, text_content").eq("id", payload.document_id).single().execute()
    doc = res.data
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    text = doc.get("text_content") or ""
    if not text.strip():
        raise HTTPException(status_code=400, detail="Document text is empty")

    # 2) Extract goals using AI (or fallback splitter)
    goals = extract_goals(text)

    # 3) Return goals (later we’ll save them into a table)
    return {"document_id": payload.document_id, "goals": goals}
