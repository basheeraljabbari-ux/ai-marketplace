import base64
import json

import httpx
from anthropic import AsyncAnthropic

from app.core.config import get_settings
from app.modules.ai.interface import AIProvider, AIAnalysisResult

settings = get_settings()

# مصدر الحقيقة الوحيد للـ slugs هنا هو scripts/seed.py. لو انضافت فئة جديدة
# هناك لازم تنضاف هنا — النموذج ما يقدر يقترح slug ما يعرفه، وأي slug يرجعه
# خارج هذي القائمة يُرمى بـ tasks.py لأنه ما ينربط بصف Category حقيقي.
CATEGORY_SLUGS = [
    "vehicles", "electronics", "home-goods", "apparel",
    "sporting-goods", "toys-games", "musical-instruments", "pet-supplies",
    "garden-outdoor", "hobbies", "office-supplies", "free-stuff",
]

SYSTEM_PROMPT = f"""You are an assistant that analyses product photos for an online marketplace.
Your task: analyse the uploaded images and return the listing data as JSON only, with no extra text before or after it.

The available categories are exactly these slugs:
{', '.join(CATEGORY_SLUGS)}

Return exactly this shape:
{{
  "category_suggestions": [
    {{"slug": "one of the slugs listed above", "confidence": number between 0 and 1}}
  ],
  "detected_brand": "brand name, or null",
  "detected_color": "primary colour, or null",
  "title": "an appealing, professional title in English, under 80 characters",
  "description": "a professional description in English, around two paragraphs, covering the condition and the visible specifications",
  "suggested_price_min": number in Australian dollars,
  "suggested_price_max": number in Australian dollars,
  "confidence": number between 0 and 1 reflecting your overall confidence in the listing data
}}

Rules for category_suggestions:
- Return up to 3 entries, ordered from most to least likely.
- Use only slugs from the list above. Never invent a slug.
- Return a single entry when the category is obvious; return 2-3 when the item plausibly
  belongs to more than one (a chess set could be toys-games or hobbies).
- Return an empty array if the images are too unclear to judge.
- Confidence must reflect genuine certainty. Do not inflate it — a low score simply lets the
  seller pick from your suggestions, which is a better outcome than a confident wrong guess.

Be realistic about pricing, based on the stated condition and the product type visible in the images."""

MAX_CATEGORY_SUGGESTIONS = 3


def parse_category_suggestions(raw) -> list[dict]:
    """يفلتر اقتراحات الفئات القادمة من النموذج لـ [{"slug", "confidence"}] موثوق.

    مخرجات النموذج غير موثوقة — نرمي أي شي ما يطابق الشكل المتوقع بدل ما نمرره
    لـ tasks.py. أي slug خارج CATEGORY_SLUGS يُرمى (النموذج أحياناً يخترع slug أو
    يرجع اسم الفئة بدل الـ slug)، وأي confidence غير رقمي يُرمى معه لأن عتبة
    الإسناد التلقائي تعتمد عليه مباشرة.

    مفصولة عن الكلاس عشان تنختبر بلا مفتاح API ولا عميل Anthropic — نفس مبدأ
    extract_attribute_filters بـ listings/router.py.
    """
    if not isinstance(raw, list):
        return []

    cleaned: list[dict] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, dict):
            continue
        slug = item.get("slug")
        if slug not in CATEGORY_SLUGS or slug in seen:
            continue
        try:
            confidence = float(item.get("confidence"))
        except (TypeError, ValueError):
            continue
        seen.add(slug)
        cleaned.append({"slug": slug, "confidence": min(max(confidence, 0.0), 1.0)})

    # نرتّب بأنفسنا بدل ما نثق بترتيب النموذج — الإسناد التلقائي يقرأ العنصر الأول.
    cleaned.sort(key=lambda s: s["confidence"], reverse=True)
    return cleaned[:MAX_CATEGORY_SUGGESTIONS]


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
                    {"type": "text", "text": f"Condition stated by the seller: {condition}\n\nAnalyse the images and return JSON only."},
                ],
            }],
        )

        raw_text = "".join(block.text for block in response.content if block.type == "text")
        data = self._parse_json_response(raw_text)

        return AIAnalysisResult(
            category_suggestions=parse_category_suggestions(data.get("category_suggestions")),
            detected_brand=data.get("detected_brand"),
            detected_color=data.get("detected_color"),
            title=data.get("title", "Untitled product — needs review"),
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
            return {"title": "Automatic analysis failed — edit manually", "confidence": 0.0}
