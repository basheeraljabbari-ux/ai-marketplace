from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AIAnalysisResult:
    category_slug: str | None
    detected_brand: str | None
    detected_color: str | None
    title: str
    description: str
    suggested_price_min: float | None
    suggested_price_max: float | None
    confidence: float
    raw_response: dict


class AIProvider(ABC):
    """عقد ثابت لأي مزوّد AI. نطاق الـ MVP: تحليل صور + توليد نص + اقتراح سعر فقط
    (البحث بلغة طبيعية والرد التلقائي مؤجلان — يُضافان كدوال جديدة هنا لاحقاً
    بدون كسر أي شي موجود)."""

    @abstractmethod
    async def analyze_and_generate(self, image_urls: list[str], condition: str) -> AIAnalysisResult: ...
