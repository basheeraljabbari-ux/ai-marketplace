from fastapi import HTTPException, status

from app.modules.categories.models import Category


def validate_attributes_against_schema(category: Category, attributes: dict) -> None:
    """يتحقق من:
    1. كل حقل required بالـ attributes_schema موجود بالقيم المُرسلة
    2. القيم من النوع الصحيح (number/select ضمن الخيارات المسموحة)

    يُستدعى وقت النشر (publish) — مو وقت الحفظ كمسودة، عشان يسمح للمستخدم
    يحفظ تدريجياً وهو لسا يعبي البيانات."""
    fields = category.attributes_schema.get("fields", [])

    for field in fields:
        key = field["key"]
        value = attributes.get(key)

        if field.get("required") and (value is None or value == ""):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"الحقل '{field.get('label_ar', key)}' مطلوب لفئة '{category.name_ar}'",
            )

        if value is None or value == "":
            continue

        if field["type"] == "number":
            try:
                num = float(value)
            except (TypeError, ValueError):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"'{field.get('label_ar', key)}' لازم يكون رقم")
            if "min" in field and num < field["min"]:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"'{field.get('label_ar', key)}' أقل من الحد الأدنى المسموح")
            if "max" in field and num > field["max"]:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"'{field.get('label_ar', key)}' أكبر من الحد الأقصى المسموح")

        elif field["type"] == "select":
            options = field.get("options", [])
            if options and value not in options:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"قيمة '{field.get('label_ar', key)}' غير ضمن الخيارات المسموحة")
