import json
import logging

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self, api_key: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = "gemini-1.5-flash"

    async def generate_ingredients(self, dish: str, persons: int) -> list[dict]:
        prompt = (
            f"Составь список ингредиентов для блюда '{dish}' на {persons} человек. "
            f"Верни ТОЛЬКО JSON без пояснений в формате: "
            f'{{"ingredients": [{{"name": "название", "amount": "количество"}}]}}'
        )
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3,
            ),
        )
        raw = response.text.strip()
        logger.info("Gemini response: %s", raw)
        data = json.loads(raw)
        return data["ingredients"]
