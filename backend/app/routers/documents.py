from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class DocumentCreate(BaseModel):
    owner_type: str  # "person" or "team"
    owner_id: str
    source: str | None = None
    text_content: str | None = None


# In-memory store for now (we’ll switch to Supabase next)
DOCUMENTS: dict[str, dict] = {}


@router.post("/documents")
def create_document(payload: DocumentCreate):
    doc_id = str(len(DOCUMENTS) + 1)
    DOCUMENTS[doc_id] = {"id": doc_id, **payload.model_dump()}
    return {"id": doc_id}


@router.get("/documents")
def list_documents():
    return {"items": list(DOCUMENTS.values())}


@router.get("/documents/{doc_id}")
def get_document(doc_id: str):
    doc = DOCUMENTS.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
