import os
import chromadb
from chromadb.utils import embedding_functions

from config.settings import get_settings
from utils.logger import get_logger

logger = get_logger("rag.query")

SYSTEM_PROMPT = """You are DocTalk's medical AI assistant.

Use ONLY the context below to answer the question.

If the answer is not present in the context say:
"I don't have specific information about that. Please consult a doctor."

Always remind users that this information is educational only and not a substitute for professional medical advice.

Context:
{context}

Question:
{question}

Answer:"""


def get_confidence(distance: float) -> str:
    if distance < 0.3:
        return "high"
    elif distance < 0.6:
        return "medium"
    return "low"


def _get_collection():
    settings = get_settings()
    ef = embedding_functions.DefaultEmbeddingFunction()
    client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
    collection = client.get_or_create_collection(
        name=settings.COLLECTION_NAME,
        embedding_function=ef,
    )
    return collection


async def query_rag(question: str) -> dict:
    from services.ai_service import AIService

    settings = get_settings()

    try:
        collection = _get_collection()

        results = collection.query(
            query_texts=[question],
            n_results=min(5, collection.count()) if collection.count() > 0 else 1,
        )

        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        if not documents:
            return {
                "answer": "I don't have specific information about that. Please consult a doctor.",
                "sources": [],
                "confidence": "low",
            }

        context = "\n\n---\n\n".join(documents)

        prompt = SYSTEM_PROMPT.format(context=context, question=question)

        ai = AIService()
        answer = await ai.generate_text(prompt)

        avg_distance = sum(distances) / len(distances) if distances else 1.0
        confidence = get_confidence(avg_distance)

        sources = []
        for i, doc in enumerate(documents):
            first_line = doc.split("\n")[0] if doc else ""
            sources.append(
                {
                    "id": ids[i] if i < len(ids) else f"source_{i}",
                    "excerpt": first_line,
                    "distance": round(distances[i], 4) if i < len(distances) else None,
                }
            )

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
        }

    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        return {
            "answer": "I encountered an error processing your question. Please consult a doctor.",
            "sources": [],
            "confidence": "low",
        }


async def semantic_search(query: str, n_results: int = 3) -> list[dict]:
    try:
        collection = _get_collection()
        count = collection.count()
        if count == 0:
            return []

        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, count),
        )

        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        hits = []
        for i, doc in enumerate(documents):
            hits.append(
                {
                    "id": ids[i] if i < len(ids) else f"result_{i}",
                    "content": doc,
                    "distance": round(distances[i], 4) if i < len(distances) else None,
                    "relevance": get_confidence(distances[i] if i < len(distances) else 1.0),
                }
            )
        return hits

    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        return []
