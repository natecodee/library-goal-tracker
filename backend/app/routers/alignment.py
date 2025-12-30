from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.supabase_client import get_supabase
from app.services.ai import suggest_alignment

router = APIRouter()

class AlignIn(BaseModel):
    document_id: str

@router.post("/ai/align")
def align_document(payload: AlignIn):
    sb = get_supabase()

    # 1) fetch doc
    doc = sb.table("documents").select("id,text_content").eq("id", payload.document_id).single().execute()
    if not doc.data:
        raise HTTPException(status_code=404, detail="Document not found")

    text = doc.data["text_content"]

    # 2) extract goals using your existing function (already working)
    from app.services.ai import extract_goals
    goals = extract_goals(text)

    # 3) load catalog (v1: inline same list)
    catalog = [
        {"code": "A1", "title": "Student Success", "description": ""},
        {"code": "A2", "title": "Student Success", "description": ""},
        {"code": "A3", "title": "Student Success", "description": ""},
        {"code": "A4", "title": "Student Success", "description": ""},
        {"code": "A5", "title": "Student Success", "description": ""},
        {"code": "A6", "title": "Student Success", "description": ""},
        {"code": "B1", "title": "Workplace Culture", "description": ""},
        {"code": "B2", "title": "Workplace Culture", "description": ""},
        {"code": "B3", "title": "Workplace Culture", "description": ""},
        {"code": "B4", "title": "Workplace Culture", "description": ""},
        {"code": "B5", "title": "Workplace Culture", "description": ""},
        {"code": "C1", "title": "Stewardship", "description": ""},
        {"code": "C2", "title": "Stewardship", "description": ""},
        {"code": "C3", "title": "Stewardship", "description": ""},
    ]

    # 4) map each goal
    results = []
    for g in goals:
        code, conf = suggest_alignment(g, catalog)
        results.append({"goal": g, "suggested_code": code, "confidence": conf})

    return {"document_id": payload.document_id, "results": results}
