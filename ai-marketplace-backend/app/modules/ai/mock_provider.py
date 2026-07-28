from app.modules.ai.interface import AIProvider, AIAnalysisResult


class MockAIProvider(AIProvider):
    """يرجع بيانات وهمية ثابتة — يسمح بتطوير واختبار باقي النظام
    (queue, endpoints, frontend) قبل ما نربط مزوّد AI حقيقي ونتحمل تكلفته."""

    async def analyze_and_generate(self, image_urls: list[str], condition: str) -> AIAnalysisResult:
        return AIAnalysisResult(
            # ثقة كلها تحت عتبة الإسناد التلقائي (0.6) عمداً — تخلي مسار الاقتراحات
            # بالواجهة يظهر بالتطوير المحلي بدل ما تنسند الفئة تلقائياً وما ينختبر أبداً.
            category_suggestions=[
                {"slug": "electronics", "confidence": 0.52},
                {"slug": "toys-games", "confidence": 0.31},
                {"slug": "hobbies", "confidence": 0.14},
            ],
            detected_brand="Unknown",
            detected_color="Unknown",
            title="Sample generated title — needs review",
            description="Sample description. This is a mock response from MockAIProvider for development.",
            suggested_price_min=50.0,
            suggested_price_max=150.0,
            confidence=0.3,
            raw_response={"mock": True, "images_received": len(image_urls), "condition": condition},
        )
