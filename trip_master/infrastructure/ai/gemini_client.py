import json
import logging

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def generate_ingredients(self, dish: str, persons: int) -> list[dict]:
        prompt = (
            f"Составь список ингредиентов для блюда '{dish}' на {persons} человек. "
            f"Верни ТОЛЬКО JSON без пояснений в формате: "
            f'{{"ingredients": [{{"name": "название", "amount": "количество"}}]}}'
        )
        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                ),
            )
        except Exception as e:
            logger.exception("Gemini API call failed")
            raise RuntimeError(f"Gemini API ошибка: {e}") from e

        raw = response.text.strip()
        logger.info("Gemini response: %s", raw)
        if not raw:
            raise RuntimeError("Gemini вернул пустой ответ")

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse Gemini response: %s", raw)
            raise RuntimeError("Не удалось разобрать ответ AI (невалидный JSON)") from e

        ingredients = data.get("ingredients")
        if not isinstance(ingredients, list):
            raise RuntimeError("AI вернул некорректную структуру данных")

        return ingredients
