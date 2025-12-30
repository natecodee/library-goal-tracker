from fastapi import APIRouter, HTTPException
from app.core.supabase_client import get_supabase

router = APIRouter()


@router.get("/strategic-goals")
def get_strategic_goals():
    """
    Returns the strategic goals catalog from the database.
    Returns code, id, title, and description for each goal.
    """
    sb = get_supabase()
    
    try:
        res = (
            sb.table("strategic_goals")
            .select("id,code,title,description")
            .order("code")
            .execute()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")
    
    return {"items": res.data or []}
