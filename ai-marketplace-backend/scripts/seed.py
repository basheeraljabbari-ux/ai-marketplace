"""
تعبئة بيانات أولية: دولة أستراليا + مدن رئيسية + الفئات الـ12 مع attributes_schema.
تشغيل: python -m scripts.seed

هذا السكربت للتنصيب الجديد فقط (قاعدة بيانات فاضية). لقاعدة بيانات شغّالة
فيها فئات قديمة استخدم scripts/expand_categories.py بدلاً منه.
"""
import asyncio
import uuid

from app.core.database import AsyncSessionLocal
from app.modules.geo.models import Country, City
from app.modules.categories.models import Category

# التعريف المرجعي للفئات الـ12 — مشترك مع scripts/expand_categories.py.
# أي تعديل هنا لازم ينعكس هناك (والعكس).
CATEGORIES = [
    {
        "slug": "vehicles", "name_ar": "مركبات", "name_en": "Vehicles",
        "fields": [
            {"key": "vehicle_type", "label_ar": "نوع المركبة", "label_en": "Vehicle type", "type": "select", "options": ["Car", "Motorcycle", "Other"], "required": True, "filterable": True},
            {"key": "brand", "label_ar": "الماركة", "label_en": "Brand", "type": "text", "required": True, "searchable": True},
            {"key": "year", "label_ar": "سنة الصنع", "label_en": "Year", "type": "number", "required": True, "filterable": True, "min": 1990, "max": 2026},
            {"key": "transmission", "label_ar": "ناقل الحركة", "label_en": "Transmission", "type": "select", "options": ["Automatic", "Manual"], "filterable": True},
            {"key": "mileage_km", "label_ar": "الممشى (كم)", "label_en": "Mileage (km)", "type": "number", "required": False, "filterable": True},
        ],
    },
    {
        "slug": "electronics", "name_ar": "إلكترونيات", "name_en": "Electronics",
        "fields": [
            {"key": "brand", "label_ar": "الماركة", "label_en": "Brand", "type": "text", "required": True, "searchable": True},
            {"key": "condition_detail", "label_ar": "تفاصيل الحالة", "label_en": "Condition details", "type": "text", "required": False},
        ],
    },
    {
        "slug": "home-goods", "name_ar": "مستلزمات منزلية", "name_en": "Home Goods",
        "fields": [
            {"key": "room_type", "label_ar": "الغرفة", "label_en": "Room", "type": "select", "options": ["Living room", "Bedroom", "Kitchen", "Bathroom", "Dining room", "Other"], "required": False, "filterable": True},
            {"key": "material", "label_ar": "الخامة", "label_en": "Material", "type": "text", "required": False},
        ],
    },
    {
        "slug": "apparel", "name_ar": "ملابس", "name_en": "Apparel",
        "fields": [
            {"key": "brand", "label_ar": "الماركة", "label_en": "Brand", "type": "text", "required": False, "searchable": True},
            {"key": "size", "label_ar": "المقاس", "label_en": "Size", "type": "select", "options": ["XS", "S", "M", "L", "XL", "XXL", "Other"], "required": True, "filterable": True},
            {"key": "gender", "label_ar": "الفئة", "label_en": "Gender", "type": "select", "options": ["Men", "Women", "Unisex", "Kids"], "required": False, "filterable": True},
        ],
    },
    {
        "slug": "sporting-goods", "name_ar": "مستلزمات رياضية", "name_en": "Sporting Goods",
        "fields": [
            {"key": "sport_type", "label_ar": "نوع الرياضة", "label_en": "Sport", "type": "text", "required": False, "searchable": True},
            {"key": "brand", "label_ar": "الماركة", "label_en": "Brand", "type": "text", "required": False, "searchable": True},
        ],
    },
    {
        "slug": "toys-games", "name_ar": "ألعاب", "name_en": "Toys & Games",
        "fields": [
            {"key": "age_range", "label_ar": "الفئة العمرية", "label_en": "Age range", "type": "select", "options": ["0-2", "3-5", "6-8", "9-12", "13+", "Adult"], "required": False, "filterable": True},
            {"key": "brand", "label_ar": "الماركة", "label_en": "Brand", "type": "text", "required": False, "searchable": True},
        ],
    },
    {
        "slug": "musical-instruments", "name_ar": "آلات موسيقية", "name_en": "Musical Instruments",
        "fields": [
            {"key": "instrument_type", "label_ar": "نوع الآلة", "label_en": "Instrument type", "type": "text", "required": True, "searchable": True},
            {"key": "brand", "label_ar": "الماركة", "label_en": "Brand", "type": "text", "required": False, "searchable": True},
        ],
    },
    {
        "slug": "pet-supplies", "name_ar": "مستلزمات الحيوانات الأليفة", "name_en": "Pet Supplies",
        "fields": [
            {"key": "pet_type", "label_ar": "نوع الحيوان", "label_en": "Pet type", "type": "select", "options": ["Dog", "Cat", "Bird", "Fish", "Small pet", "Other"], "required": False, "filterable": True},
            {"key": "brand", "label_ar": "الماركة", "label_en": "Brand", "type": "text", "required": False, "searchable": True},
        ],
    },
    {
        "slug": "garden-outdoor", "name_ar": "حديقة وخارجية", "name_en": "Garden & Outdoor",
        "fields": [
            {"key": "item_type", "label_ar": "نوع الغرض", "label_en": "Item type", "type": "text", "required": False, "searchable": True},
            {"key": "material", "label_ar": "الخامة", "label_en": "Material", "type": "text", "required": False},
        ],
    },
    {
        "slug": "hobbies", "name_ar": "هوايات", "name_en": "Hobbies",
        "fields": [
            {"key": "hobby_type", "label_ar": "نوع الهواية", "label_en": "Hobby type", "type": "text", "required": False, "searchable": True},
        ],
    },
    {
        "slug": "office-supplies", "name_ar": "مستلزمات مكتبية", "name_en": "Office Supplies",
        "fields": [
            {"key": "item_type", "label_ar": "نوع الغرض", "label_en": "Item type", "type": "text", "required": False, "searchable": True},
            {"key": "brand", "label_ar": "الماركة", "label_en": "Brand", "type": "text", "required": False, "searchable": True},
        ],
    },
    {
        # بلا حقول إضافية عن قصد — الهدف نشر سريع بأقل احتكاك
        "slug": "free-stuff", "name_ar": "أشياء مجانية", "name_en": "Free Stuff",
        "fields": [],
    },
]


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

        db.add_all([
            Category(
                id=uuid.uuid4(),
                name_ar=c["name_ar"],
                name_en=c["name_en"],
                slug=c["slug"],
                attributes_schema={"fields": c["fields"]},
            )
            for c in CATEGORIES
        ])

        await db.commit()
        print(f"Seed complete. {len(CATEGORIES)} categories created.")


if __name__ == "__main__":
    asyncio.run(seed())
