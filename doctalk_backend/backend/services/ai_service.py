import time
import base64
from openai import AsyncOpenAI

from config.settings import get_settings
from utils.logger import get_logger

logger = get_logger("services.ai_service")


class AIService:
    def __init__(self):
        settings = get_settings()
        self.model = settings.AI_MODEL
        # AFTER
        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url="https://models.inference.ai.azure.com",
)

    async def generate_text(self, prompt: str) -> str:
        start = time.time()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
            )
            elapsed = round(time.time() - start, 3)
            usage = response.usage
            logger.info(
                f"generate_text: {elapsed}s | "
                f"prompt_tokens={usage.prompt_tokens} completion_tokens={usage.completion_tokens}"
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"generate_text error: {e}")
            raise

    async def generate_with_history(self, messages: list[dict]) -> str:
        start = time.time()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1024,
            )
            elapsed = round(time.time() - start, 3)
            usage = response.usage
            logger.info(
                f"generate_with_history: {elapsed}s | "
                f"prompt_tokens={usage.prompt_tokens} completion_tokens={usage.completion_tokens}"
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"generate_with_history error: {e}")
            raise

    async def analyze_image(self, image_bytes: bytes, prompt: str) -> str:
        start = time.time()
        try:
            b64 = base64.b64encode(image_bytes).decode("utf-8")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{b64}"
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                max_tokens=1500,
            )
            elapsed = round(time.time() - start, 3)
            logger.info(f"analyze_image: {elapsed}s")
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"analyze_image error: {e}")
            raise

    async def analyze_document_text(self, text: str, prompt: str) -> str:
        start = time.time()
        try:
            full_prompt = f"{prompt}\n\nDocument Content:\n{text}"
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=2000,
            )
            elapsed = round(time.time() - start, 3)
            usage = response.usage
            logger.info(
                f"analyze_document_text: {elapsed}s | "
                f"prompt_tokens={usage.prompt_tokens} completion_tokens={usage.completion_tokens}"
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"analyze_document_text error: {e}")
            raise
