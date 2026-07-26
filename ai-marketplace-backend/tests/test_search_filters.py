"""اختبارات استخراج فلاتر الـ attributes الديناميكية من الـ query params.

بلا قاعدة بيانات وبلا app — نمرّر QueryParams مباشرة لأن واجهتها (.items())
نفس واجهة request.query_params بستارليت.

المطابقة الفعلية على JSONB مغطّاة بـ tests/test_integration.py لأنها تحتاج
PostgreSQL حقيقي.
"""
from httpx import QueryParams

from app.modules.listings.router import FIXED_SEARCH_PARAMS, extract_attribute_filters


def test_unknown_param_becomes_attribute_filter():
    assert extract_attribute_filters(QueryParams({"transmission": "Automatic"})) == {"transmission": "Automatic"}


def test_fixed_params_are_excluded():
    params = QueryParams({
        "q": "toyota", "city_id": "abc", "category_id": "def", "price_min": "100",
        "price_max": "900", "condition": "used", "page": "2", "limit": "24",
    })
    assert extract_attribute_filters(params) == {}


def test_every_fixed_param_is_covered_by_the_exclusion_set():
    # يمسك لو انضاف بارامتر ثابت للتوقيع ونُسي من FIXED_SEARCH_PARAMS —
    # وقتها يتسرّب كفلتر attributes ويرجع نتايج فاضية بلا أي خطأ ظاهر.
    for name in FIXED_SEARCH_PARAMS:
        assert extract_attribute_filters(QueryParams({name: "x"})) == {}


def test_fixed_and_dynamic_params_mixed():
    params = QueryParams({"q": "toyota", "page": "2", "transmission": "Manual", "year": "2019"})
    assert extract_attribute_filters(params) == {"transmission": "Manual", "year": "2019"}


def test_empty_value_is_dropped():
    # "Any" بالواجهة ترسل قيمة فاضية — لازم تعني بلا فلتر مو attributes->>'x' = ''
    assert extract_attribute_filters(QueryParams({"transmission": ""})) == {}


def test_no_params_yields_empty_dict():
    assert extract_attribute_filters(QueryParams({})) == {}


def test_multiple_attribute_filters_all_kept():
    params = QueryParams({"size": "L", "gender": "Women", "brand": "Nike"})
    assert extract_attribute_filters(params) == {"size": "L", "gender": "Women", "brand": "Nike"}
