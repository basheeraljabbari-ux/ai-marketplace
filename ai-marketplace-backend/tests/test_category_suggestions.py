"""اختبارات فلترة اقتراحات الفئات القادمة من النموذج.

بلا قاعدة بيانات وبلا مفتاح API — parse_category_suggestions دالة نقية على مستوى
الموديول، فما نحتاج نبني AnthropicAIProvider (اللي يتطلب عميل Anthropic).

الربط الفعلي بصفوف Category والإسناد التلقائي مغطّى بـ tasks.py ويحتاج قاعدة
بيانات، فمو من نطاق هذا الملف.
"""
from app.modules.ai.anthropic_provider import CATEGORY_SLUGS, parse_category_suggestions


def test_valid_suggestions_pass_through():
    raw = [{"slug": "electronics", "confidence": 0.9}]
    assert parse_category_suggestions(raw) == [{"slug": "electronics", "confidence": 0.9}]


def test_unknown_slug_is_dropped():
    # 'cars' و 'furniture' كانوا slugs قديمة قبل التوسعة لـ 12 فئة
    raw = [{"slug": "cars", "confidence": 0.9}, {"slug": "electronics", "confidence": 0.4}]
    assert parse_category_suggestions(raw) == [{"slug": "electronics", "confidence": 0.4}]


def test_results_are_sorted_by_confidence_desc():
    raw = [
        {"slug": "hobbies", "confidence": 0.2},
        {"slug": "electronics", "confidence": 0.8},
        {"slug": "toys-games", "confidence": 0.5},
    ]
    assert [s["slug"] for s in parse_category_suggestions(raw)] == ["electronics", "toys-games", "hobbies"]


def test_capped_at_three():
    raw = [{"slug": slug, "confidence": 0.5} for slug in CATEGORY_SLUGS]
    assert len(parse_category_suggestions(raw)) == 3


def test_duplicate_slug_keeps_first_occurrence_only():
    raw = [{"slug": "electronics", "confidence": 0.7}, {"slug": "electronics", "confidence": 0.2}]
    assert parse_category_suggestions(raw) == [{"slug": "electronics", "confidence": 0.7}]


def test_non_numeric_confidence_is_dropped():
    # الثقة تحدد الإسناد التلقائي — قيمة ما تنقرأ كرقم لازم ترمي الاقتراح كامل
    raw = [{"slug": "electronics", "confidence": "high"}, {"slug": "apparel"}]
    assert parse_category_suggestions(raw) == []


def test_confidence_is_clamped_to_unit_range():
    raw = [{"slug": "electronics", "confidence": 1.7}, {"slug": "apparel", "confidence": -0.3}]
    assert parse_category_suggestions(raw) == [
        {"slug": "electronics", "confidence": 1.0},
        {"slug": "apparel", "confidence": 0.0},
    ]


def test_non_list_input_returns_empty():
    # الـ fallback بـ _parse_json_response ما فيه المفتاح أصلاً → None
    assert parse_category_suggestions(None) == []
    assert parse_category_suggestions({"slug": "electronics"}) == []
    assert parse_category_suggestions("electronics") == []


def test_non_dict_entries_are_dropped():
    raw = ["electronics", None, 42, {"slug": "apparel", "confidence": 0.3}]
    assert parse_category_suggestions(raw) == [{"slug": "apparel", "confidence": 0.3}]


def test_empty_list_returns_empty():
    assert parse_category_suggestions([]) == []
