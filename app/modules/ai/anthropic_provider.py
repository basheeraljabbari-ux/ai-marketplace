import base64
import json

import httpx
from anthropic import AsyncAnthropic

from app.core.config import get_settings
from app.modules.ai.interface import AIProvider, AIAnalysisResult

settings = get_settings()

SYSTEM_PROMPT = """أنت مساعد متخصص بتحليل صور منتجات لسوق إلكتروني (marketplace).
مهمتك: تحلل الصور المرفوعة وترجع بيانات الإعلان بصيغة JSON فقط، بدون أي نص إضافي قبل أو بعد.

الصيغة المطلوبة بالضبط:
{
  "category_slug": "أقرب فئة من: electronics, cars, furniture, أو null لو مو واضح",
  "detected_brand": "اسم الماركة أو null",
  "detected_color": "اللون الأساسي أو null",
  "title": "عنوان جذاب واحترافي بالعربي، أقل من 80 حرف",
  "description": "وصف احترافي بالعربي، فقرتين تقريباً، يذكر الحالة والمواصفات الظاهرة",
  "suggested_price_min": رقم بالدولار الأسترالي,
  "suggested_price_max": رقم بالدولار الأسترالي,
  "confidence": رقم بين 0 و 1 يعكس ثقتك بتحديد الفئة والماركة
}

كن واقعي بتقدير السعر بناءً على حالة المنتج المذكورة ونوعه الظاهر بالصور."""


class AnthropicAIProvider(AIProvider):
    """يستخدم Claude (رؤية + نص) لتحليل صور المنتج وتوليد بيانات الإعلان.
    يطبّق نفس AIProvider interface بالضبط — لا شي بباقي النظام يتغير
    غير AI_PROVIDER=anthropic بالـ .env."""

    def __init__(self):
        self._client = AsyncAnthropic(api_key=settings.AI_API_KEY)

    async def analyze_and_generate(self, image_urls: list[str], condition: str) -> AIAnalysisResult:
        image_blocks = await self._urls_to_image_blocks(image_urls)

        response = await self._client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": [
                    *image_blocks,
                    {"type": "text", "text": f"حالة المنتج المذكورة من البائع: {condition}\n\nحلل الصور وأرجع JSON فقط."},
                ],
            }],
        )

        raw_text = "".join(block.text for block in response.content if block.type == "text")
        data = self._parse_json_response(raw_text)

        return AIAnalysisResult(
            category_slug=data.get("category_slug"),
            detected_brand=data.get("detected_brand"),
            detected_color=data.get("detected_color"),
            title=data.get("title", "منتج بدون عنوان — يحتاج مراجعة"),
            description=data.get("description", ""),
            suggested_price_min=data.get("suggested_price_min"),
            suggested_price_max=data.get("suggested_price_max"),
            confidence=float(data.get("confidence", 0.5)),
            raw_response=data,
        )

    async def _urls_to_image_blocks(self, image_urls: list[str]) -> list[dict]:
        """يحمّل كل صورة ويحوّلها لـ base64 — الـ Anthropic API تحتاج بيانات الصورة
        مباشرة (لا تدعم روابط عامة مباشرة بكل الحالات)."""
        blocks = []
        async with httpx.AsyncClient(timeout=15) as client:
            for url in image_urls[:10]:  # نفس حد الـ 10 صور بكل مكان بالنظام
                resp = await client.get(url)
                resp.raise_for_status()
                media_type = resp.headers.get("content-type", "image/jpeg")
                encoded = base64.b64encode(resp.content).decode("utf-8")
                blocks.append({
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": encoded},
                })
        return blocks

    def _parse_json_response(self, text: str) -> dict:
        """Claude ملتزم عادة بإرجاع JSON خام حسب system prompt، لكن نتعامل مع احتمال
        وجود ```json fences احتياطاً."""
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        try:
            return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            # فشل الـ parsing لا يوقف الطلب — نرجع مسودة تحتاج مراجعة يدوية كاملة
            return {"title": "تعذّر التحليل التلقائي — عدّل يدوياً", "confidence": 0.0}
