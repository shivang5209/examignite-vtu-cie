from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import admin, attempts, auth, catalog, practice
from app.core.config import settings
from app.core.db import Base, SessionLocal, engine
from app.services.db_seed import seed_demo_data


app = FastAPI(
    title="VTU CIE App API",
    version="1.0.0",
    description="Hybrid rubric + retrieval backend for VTU CSE CIE practice.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(catalog.router, tags=["catalog"])
app.include_router(practice.router, tags=["practice"])
app.include_router(attempts.router, tags=["attempts"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])


@app.on_event("startup")
def startup() -> None:
    if settings.auto_create_schema:
        Base.metadata.create_all(bind=engine)
    if settings.auto_seed_data:
        with SessionLocal() as session:
            seed_demo_data(session)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
