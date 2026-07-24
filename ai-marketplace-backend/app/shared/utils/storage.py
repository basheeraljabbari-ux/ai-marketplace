import uuid
from io import BytesIO

import boto3
from PIL import Image

from app.core.config import get_settings

settings = get_settings()

THUMBNAIL_SIZE = (200, 200)
OPTIMIZED_MAX_SIZE = (1200, 1200)


class StorageService:
    """يتعامل مع أي S3-compatible storage (AWS S3, Cloudflare R2, Supabase Storage —
    كلهم يدعمون نفس الـ S3 API). التبديل بينهم = تغيير STORAGE_ENDPOINT_URL بالـ .env فقط."""

    def __init__(self):
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.STORAGE_ENDPOINT_URL,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_SECRET_KEY,
        )
        self._bucket = settings.STORAGE_BUCKET
        # قاعدة الروابط العامة للقراءة — منفصلة عن endpoint الرفع (راجع STORAGE_PUBLIC_URL)
        self._public_base = (settings.STORAGE_PUBLIC_URL or "").rstrip("/")

    def upload_listing_image(self, file_bytes: bytes, content_type: str) -> dict:
        """يرفع 3 نسخ (original/thumbnail/optimized) ويرجع الروابط + الأبعاد الأصلية.
        Pillow processing (resize) يصير هنا بشكل متزامن — مقبول لحجم صور اعتيادي؛
        لو صار bottleneck لاحقاً، ينتقل لنفس queue تبع الـ AI بدون تغيير الـ interface."""
        image = Image.open(BytesIO(file_bytes))
        image = image.convert("RGB") if image.mode in ("RGBA", "P") else image
        width, height = image.size

        key_prefix = f"listings/{uuid.uuid4()}"
        original_key = f"{key_prefix}/original.jpg"
        thumbnail_key = f"{key_prefix}/thumbnail.webp"
        optimized_key = f"{key_prefix}/optimized.webp"

        self._put(original_key, file_bytes, content_type)

        thumb = image.copy()
        thumb.thumbnail(THUMBNAIL_SIZE)
        self._put(thumbnail_key, self._to_bytes(thumb, "WEBP"), "image/webp")

        optimized = image.copy()
        optimized.thumbnail(OPTIMIZED_MAX_SIZE)
        self._put(optimized_key, self._to_bytes(optimized, "WEBP", quality=85), "image/webp")

        return {
            "original_url": self._public_url(original_key),
            "thumbnail_url": self._public_url(thumbnail_key),
            "optimized_url": self._public_url(optimized_key),
            "width": width,
            "height": height,
        }

    def _public_url(self, key: str) -> str:
        """الرابط اللي يُخزَّن بالـ DB ويُعطى للعميل/الـ AI. لو STORAGE_PUBLIC_URL
        محدد نستخدمه مباشرة بلا جزء bucket (صيغة R2)، وإلا نرجع للصيغة القديمة
        base/bucket/key حتى ما ينكسر أي إعداد S3 قائم."""
        if self._public_base:
            return f"{self._public_base}/{key}"
        base_url = settings.STORAGE_ENDPOINT_URL or f"https://{self._bucket}.s3.amazonaws.com"
        return f"{base_url}/{self._bucket}/{key}"

    def _put(self, key: str, data: bytes, content_type: str) -> None:
        self._client.put_object(Bucket=self._bucket, Key=key, Body=data, ContentType=content_type)

    def delete_listing_images(self, image_urls: list[str]) -> None:
        """يحذف original/thumbnail/optimized دفعة واحدة. يتعامل مع الصيغتين:
        الجديدة (public_base/key) والقديمة (base/bucket/key) — لأن الروابط
        المخزّنة بالـ DB قبل إضافة STORAGE_PUBLIC_URL لسه بالصيغة القديمة."""
        keys = []
        for url in image_urls:
            if not url:
                continue
            key = self._key_from_url(url)
            if key:
                keys.append(key)
        if not keys:
            return
        self._client.delete_objects(
            Bucket=self._bucket,
            Delete={"Objects": [{"Key": k} for k in keys]},
        )

    def _key_from_url(self, url: str) -> str | None:
        if self._public_base and url.startswith(f"{self._public_base}/"):
            return url[len(self._public_base) + 1:]
        marker = f"{self._bucket}/"
        if marker in url:
            return url.split(marker, 1)[1]
        return None

    def _to_bytes(self, image: Image.Image, fmt: str, **kwargs) -> bytes:
        buf = BytesIO()
        image.save(buf, format=fmt, **kwargs)
        return buf.getvalue()
