from rag.query import query_rag, semantic_search
from utils.logger import get_logger

logger = get_logger("services.rag_service")

DISCLAIMER = (
    "This information is for educational purposes only and is not a substitute "
    "for professional medical advice. Always consult a qualified healthcare provider."
)


async def ask_medicine_question(question: str) -> dict:
    result = await query_rag(question)
    result["disclaimer"] = DISCLAIMER
    return result


async def search_medicines(query: str, n: int = 3) -> list[dict]:
    return await semantic_search(query, n_results=n)


async def analyze_interactions(medicines: list[str]) -> dict:
    from services.ai_service import AIService

    if len(medicines) < 2:
        return {
            "interactions": [],
            "summary": "At least two medicines are required for interaction analysis.",
            "disclaimer": DISCLAIMER,
        }

    pairs = []
    for i in range(len(medicines)):
        for j in range(i + 1, len(medicines)):
            pairs.append((medicines[i], medicines[j]))

    pair_text = "\n".join([f"- {a} + {b}" for a, b in pairs])

    prompt = f"""You are a clinical pharmacist assistant. Analyze the drug interactions between these medication pairs:

{pair_text}

For each pair provide:
1. Interaction severity (none / minor / moderate / major / contraindicated)
2. Mechanism of interaction
3. Clinical effect
4. Recommendation

Format your response as structured analysis per pair.

Important: This is for educational purposes only. Always advise consulting a healthcare professional."""

    ai = AIService()
    analysis = await ai.generate_text(prompt)

    return {
        "medicines": medicines,
        "pairs_analyzed": [{"pair": list(p)} for p in pairs],
        "analysis": analysis,
        "disclaimer": DISCLAIMER,
    }
