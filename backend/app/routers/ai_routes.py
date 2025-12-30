from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.supabase_client import get_supabase
from app.services.ai import extract_goals, suggest_alignment

router = APIRouter(prefix="/ai", tags=["ai"])


class DocRef(BaseModel):
    document_id: str


def normalize_goal(text: str) -> str:
    """
    Normalizes goal text for storage/search.
    This satisfies the NOT NULL constraint on extracted_goals.normalized_text.
    """
    return text.strip().lower()


@router.post("/extract-goals")
def extract_goals_from_doc(payload: DocRef):
    sb = get_supabase()

    doc = (
        sb.table("documents")
        .select("id,text_content")
        .eq("id", payload.document_id)
        .single()
        .execute()
    )

    if not doc.data:
        raise HTTPException(status_code=404, detail="Document not found")

    goals = extract_goals(doc.data.get("text_content") or "")
    return {"document_id": payload.document_id, "goals": goals}


@router.post("/align")
def align_goals(payload: DocRef):
    sb = get_supabase()

    # 1) fetch document text
    doc = (
        sb.table("documents")
        .select("id,text_content")
        .eq("id", payload.document_id)
        .single()
        .execute()
    )

    if not doc.data:
        raise HTTPException(status_code=404, detail="Document not found")

    text = doc.data.get("text_content") or ""

    # 2) extract goals
    goals = extract_goals(text)

    # 3) load strategic goal catalog
    cat = (
        sb.table("strategic_goals")
        .select("id,code,title,description")
        .order("code")
        .execute()
    )

    catalog = cat.data or []
    if not catalog:
        raise HTTPException(status_code=500, detail="Strategic goals catalog is empty")

    # 4) suggest alignment
    results = []
    for g in goals:
        code, conf = suggest_alignment(g, catalog)
        results.append(
            {
                "goal_text": g,
                "suggested_code": code,
                "confidence": conf,
            }
        )

    return {"document_id": payload.document_id, "results": results}


@router.post("/align-and-store")
def align_and_store(payload: DocRef):
    sb = get_supabase()

    # 1) fetch document text
    doc = (
        sb.table("documents")
        .select("id,text_content")
        .eq("id", payload.document_id)
        .single()
        .execute()
    )

    if not doc.data:
        raise HTTPException(status_code=404, detail="Document not found")

    text = doc.data.get("text_content") or ""

    # 2) extract goals
    goals = extract_goals(text)

    # 3) load strategic goals catalog
    cat = (
        sb.table("strategic_goals")
        .select("id,code,title,description")
        .order("code")
        .execute()
    )

    catalog = cat.data or []
    if not catalog:
        raise HTTPException(status_code=500, detail="Strategic goals catalog is empty")

    # Build lookup: code -> strategic_goal_id
    code_to_id = {c["code"]: c["id"] for c in catalog if c.get("code")}

    # 4) build rows for insertion
    rows = []
    for g in goals:
        g = (g or "").strip()
        if not g:
            continue

        code, conf = suggest_alignment(g, catalog)

        rows.append(
            {
                "document_id": payload.document_id,
                "goal_text": g,
                "normalized_text": normalize_goal(g),  # REQUIRED (NOT NULL)
                "suggested_code": code,
                "strategic_goal_id": code_to_id.get(code),
                "confidence": conf,
                "status": "suggested",
            }
        )

    if not rows:
        return {"document_id": payload.document_id, "inserted": 0}

    # 5) clear previous extracted goals for this document (idempotent behavior)
    sb.table("extracted_goals").delete().eq(
        "document_id", payload.document_id
    ).execute()

    # 6) insert new rows
    try:
        res = sb.table("extracted_goals").insert(rows).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "document_id": payload.document_id,
        "inserted": len(res.data or []),
    }
