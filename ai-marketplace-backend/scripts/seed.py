"""
تعبئة بيانات أولية: دولة أستراليا + مدن رئيسية + فئات أساسية مع attributes_schema.
تشغيل: python -m scripts.seed
"""
import asyncio
import uuid

from app.core.database import AsyncSessionLocal
from app.modules.geo.models import Country, City
from app.modules.categories.models import Category


async def seed():
    async with AsyncSessionLocal() as db:
        australia = Country(id=uuid.uuid4(), name_ar="أستراليا", name_en="Australia", iso_code="AU")
        db.add(australia)
        await db.flush()

        cities = [
            City(id=uuid.uuid4(), country_id=australia.id, name_ar="سيدني", name_en="Sydney"),
            City(id=uuid.uuid4(), country_id=australia.id, name_ar="ملبورن", name_en="Melbourne"),
            City(id=uuid.uuid4(), country_id=australia.id, name_ar="بريزبن", name_en="Brisbane"),
            City(id=uuid.uuid4(), country_id=australia.id, name_ar="بيرث", name_en="Perth"),
        ]
        db.add_all(cities)

        electronics = Category(
            id=uuid.uuid4(), name_ar="إلكترونيات", name_en="Electronics", slug="electronics",
            attributes_schema={"fields": [
                {"key": "brand", "label_ar": "الماركة", "type": "text", "required": True, "searchable": True},
                {"key": "condition_detail", "label_ar": "تفاصيل الحالة", "type": "text", "required": False},
            ]},
        )
        cars = Category(
            id=uuid.uuid4(), name_ar="سيارات", name_en="Cars", slug="cars",
            attributes_schema={"fields": [
                {"key": "brand", "label_ar": "الماركة", "type": "text", "required": True, "searchable": True},
                {"key": "year", "label_ar": "سنة الصنع", "type": "number", "required": True, "filterable": True, "min": 1990, "max": 2026},
                {"key": "transmission", "label_ar": "ناقل الحركة", "type": "select", "options": ["اوتوماتيك", "يدوي"], "filterable": True},
                {"key": "mileage_km", "label_ar": "الممشى (كم)", "type": "number", "required": False, "filterable": True},
            ]},
        )
        furniture = Category(
            id=uuid.uuid4(), name_ar="أثاث", name_en="Furniture", slug="furniture",
            attributes_schema={"fields": [
                {"key": "material", "label_ar": "الخامة", "type": "text", "required": False},
            ]},
        )
        db.add_all([electronics, cars, furniture])

        await db.commit()
        print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
