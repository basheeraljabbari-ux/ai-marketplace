import pytest
from fastapi import HTTPException

from app.modules.categories.models import Category
from app.modules.listings.validators import validate_attributes_against_schema


def make_category(fields: list[dict]) -> Category:
    cat = Category(name_ar="سيارات", name_en="Cars", slug="cars")
    cat.attributes_schema = {"fields": fields}
    return cat


def test_required_field_missing_raises():
    cat = make_category([{"key": "brand", "label_ar": "الماركة", "type": "text", "required": True}])
    with pytest.raises(HTTPException) as exc:
        validate_attributes_against_schema(cat, {})
    assert exc.value.status_code == 400


def test_required_field_present_passes():
    cat = make_category([{"key": "brand", "label_ar": "الماركة", "type": "text", "required": True}])
    validate_attributes_against_schema(cat, {"brand": "Toyota"})  # ما يرمي شي


def test_optional_field_missing_passes():
    cat = make_category([{"key": "notes", "label_ar": "ملاحظات", "type": "text", "required": False}])
    validate_attributes_against_schema(cat, {})


def test_number_field_out_of_range_raises():
    cat = make_category([{"key": "year", "label_ar": "السنة", "type": "number", "min": 1990, "max": 2026}])
    with pytest.raises(HTTPException):
        validate_attributes_against_schema(cat, {"year": 1980})


def test_number_field_in_range_passes():
    cat = make_category([{"key": "year", "label_ar": "السنة", "type": "number", "min": 1990, "max": 2026}])
    validate_attributes_against_schema(cat, {"year": 2020})


def test_number_field_non_numeric_raises():
    cat = make_category([{"key": "year", "label_ar": "السنة", "type": "number"}])
    with pytest.raises(HTTPException):
        validate_attributes_against_schema(cat, {"year": "not-a-number"})


def test_select_field_invalid_option_raises():
    cat = make_category([{"key": "transmission", "label_ar": "ناقل الحركة", "type": "select", "options": ["اوتوماتيك", "يدوي"]}])
    with pytest.raises(HTTPException):
        validate_attributes_against_schema(cat, {"transmission": "كهربائي"})


def test_select_field_valid_option_passes():
    cat = make_category([{"key": "transmission", "label_ar": "ناقل الحركة", "type": "select", "options": ["اوتوماتيك", "يدوي"]}])
    validate_attributes_against_schema(cat, {"transmission": "اوتوماتيك"})


def test_empty_schema_always_passes():
    cat = make_category([])
    validate_attributes_against_schema(cat, {"anything": "goes"})
