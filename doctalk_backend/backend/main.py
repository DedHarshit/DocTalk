from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import asyncio

from config.settings import get_settings
from utils.logger import get_logger
from rag.ingestion import ingest

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    settings = get_settings()
    logger.info("=" * 60)
    logger.info("  DocTalk API — Starting up")
    logger.info("=" * 60)

    # 1. Log environment
    logger.info(f"  Environment : {settings.ENVIRONMENT}")
    logger.info(f"  AI Model    : {settings.AI_MODEL}")
    logger.info(f"  ChromaDB    : {settings.CHROMA_DB_PATH}")
    logger.info(f"  Collection  : {settings.COLLECTION_NAME}")
    logger.info(f"  Frontend URL: {settings.FRONTEND_URL}")

    logger.info("Checking ChromaDB collection …")

    async def run_ingestion():
        try:
            result = ingest(force=False)

            if result["status"] == "skipped":
                logger.info(
                    f"Collection already populated ({result['chunks']} chunks). Skipping ingestion."
                )
            else:
                logger.info(
                    f"Ingestion complete — {result['chunks']} chunks loaded into '{result['collection']}'."
                )

        except Exception as exc:
            logger.error(f"Ingestion failed: {exc}")
            logger.warning("RAG queries may not work correctly.")

    # Run ingestion in background so API starts immediately
    asyncio.create_task(run_ingestion())

    logger.info("System ready ✓")
    logger.info("=" * 60)

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────
    logger.info("DocTalk API shutting down.")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="DocTalk API",
        version="1.0.0",
        description="AI-powered medical health navigator backend",
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    origins = [settings.FRONTEND_URL]
    if settings.ENVIRONMENT == "development":
        origins += [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    from routers.medicine import router as medicine_router
    from routers.report import router as report_router
    from routers.chat import router as chat_router
    from routers.reminder import router as reminder_router
    from routers.health import router as health_router

    app.include_router(medicine_router, prefix="/api")
    app.include_router(report_router, prefix="/api")
    app.include_router(chat_router, prefix="/api")
    app.include_router(reminder_router, prefix="/api")
    app.include_router(health_router, prefix="/api")

    # ── Root endpoints ────────────────────────────────────────────────────────
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "status": "ok",
            "service": "DocTalk API",
            "version": "1.0.0",
        }

    @app.get("/api/ping", tags=["Root"])
    async def ping():
        return {
            "pong": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)