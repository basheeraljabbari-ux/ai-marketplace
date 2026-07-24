from app.modules.ai.interface import AIProvider, AIAnalysisResult


class MockAIProvider(AIProvider):
    """يرجع بيانات وهمية ثابتة — يسمح بتطوير واختبار باقي النظام
    (queue, endpoints, frontend) قبل ما نربط مزوّد AI حقيقي ونتحمل تكلفته."""

    async def analyze_and_generate(self, image_urls: list[str], condition: str) -> AIAnalysisResult:
        return AIAnalysisResult(
            category_slug=None,  # confidence واطئة عمداً → يفرض اختيار فئة يدوي بالـ UI
            detected_brand="Unknown",
            detected_color="Unknown",
            title="Sample generated title — needs review",
            description="Sample description. This is a mock response from MockAIProvider for development.",
            suggested_price_min=50.0,
            suggested_price_max=150.0,
            confidence=0.3,
            raw_response={"mock": True, "images_received": len(image_urls), "condition": condition},
        )
