import os
import sys
import argparse
import chromadb
from chromadb.utils import embedding_functions

# Allow running as script directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.settings import get_settings
from utils.logger import get_logger

logger = get_logger("rag.ingestion")


def load_chunks(filepath: str) -> list[str]:
    """Read medicine_knowledge.txt and split by double newline."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Knowledge file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    chunks = [chunk.strip() for chunk in raw.split("\n\n") if chunk.strip()]
    return chunks


def get_chroma_client(db_path: str) -> chromadb.PersistentClient:
    os.makedirs(db_path, exist_ok=True)
    return chromadb.PersistentClient(path=db_path)


def ingest(force: bool = False) -> dict:
    settings = get_settings()

    data_file = os.path.join(
        os.path.dirname(__file__), "..", "data", "medicine_knowledge.txt"
    )
    data_file = os.path.normpath(data_file)

    client = get_chroma_client(settings.CHROMA_DB_PATH)

    ef = embedding_functions.DefaultEmbeddingFunction()

    collection = client.get_or_create_collection(
        name=settings.COLLECTION_NAME,
        embedding_function=ef,
        metadata={"description": "DocTalk medicine knowledge base"},
    )

    existing_count = collection.count()

    if existing_count > 0 and not force:
        logger.info(
            f"Collection '{settings.COLLECTION_NAME}' already has {existing_count} documents. Skipping ingestion."
        )
        return {
            "status": "skipped",
            "chunks": existing_count,
            "collection": settings.COLLECTION_NAME,
            "db_path": settings.CHROMA_DB_PATH,
        }

    if force and existing_count > 0:
        logger.info("Force flag set. Clearing existing collection data...")
        client.delete_collection(settings.COLLECTION_NAME)
        collection = client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            embedding_function=ef,
            metadata={"description": "DocTalk medicine knowledge base"},
        )

    logger.info(f"Loading chunks from: {data_file}")
    chunks = load_chunks(data_file)
    logger.info(f"Found {len(chunks)} medicine entries to ingest.")

    ids = [f"medicine_{i}" for i in range(len(chunks))]

    collection.upsert(
        ids=ids,
        documents=chunks,
    )

    summary = {
        "status": "success",
        "chunks": len(chunks),
        "collection": settings.COLLECTION_NAME,
        "db_path": settings.CHROMA_DB_PATH,
    }

    logger.info(
        f"Ingestion complete — {summary['chunks']} chunks → "
        f"collection '{summary['collection']}' at '{summary['db_path']}'"
    )
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DocTalk RAG Ingestion")
    parser.add_argument(
        "--force", action="store_true", help="Re-ingest even if data exists"
    )
    args = parser.parse_args()
    result = ingest(force=args.force)
    print(result)
