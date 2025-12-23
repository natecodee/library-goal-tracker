from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.core.supabase_client import get_supabase

router = APIRouter()

class DocumentIn(BaseModel):
    owner_type: str   # "person" or "team"
    owner_id: str
    source: str       # "paste" for now
    text_content: str

@router.post("/documents")
def create_document(payload: DocumentIn):
    sb = get_supabase()
    try:
        res = sb.table("documents").insert(payload.model_dump()).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insert failed: {e}")

    data = res.data or []
    if not data:
        raise HTTPException(status_code=500, detail="Insert returned no row")

    # return { id: <new id> } to match what you saw earlier
    return {"id": data[0]["id"]}

@router.get("/documents")
def list_documents(owner_type: Optional[str] = None, owner_id: Optional[str] = None):
    sb = get_supabase()
    try:
        q = sb.table("documents").select("*").order("id", desc=False)
        if owner_type:
            q = q.eq("owner_type", owner_type)
        if owner_id:
            q = q.eq("owner_id", owner_id)

        res = q.execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Select failed: {e}")

    return {"items": res.data or []}
