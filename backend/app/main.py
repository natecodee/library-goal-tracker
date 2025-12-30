from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.health import router as health_router
from app.routers.documents import router as documents_router
from app.routers.ai_routes import router as ai_router
from app.routers.catalog import router as catalog_router
from app.routers.alignment import router as alignment_router
from app.routers.extracted_goals import router as extracted_goals_router



app = FastAPI(title="Library Strategic Goals Tracker API")

origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(catalog_router, prefix="/api")
app.include_router(alignment_router, prefix="/api")
app.include_router(extracted_goals_router, prefix="/api")


