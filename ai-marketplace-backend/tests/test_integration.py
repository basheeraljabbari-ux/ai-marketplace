"""
Tests تكاملية كاملة (register -> login -> create listing -> publish).
تحتاج PostgreSQL حقيقي (بسبب JSONB/TSVECTOR) — ليست SQLite في الذاكرة.

تشغيل:
    createdb ai_marketplace_test
    TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_marketplace_test pytest tests/test_integration.py

لو TEST_DATABASE_URL غير موجود، الاختبارات تُتخطى تلقائياً (skip) بدل ما تفشل —
هذا يخلي `pytest` يشتغل بأي بيئة CI بدون إعداد إضافي، مع بقاء التغطية الكاملة
متاحة لمن يريد تشغيلها فعلياً مع قاعدة بيانات.
"""
import os
import uuid

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not TEST_DATABASE_URL, reason="TEST_DATABASE_URL not set — skipping integration tests")


@pytest.fixture
async def client():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_returns_tokens(client):
    resp = await client.post("/api/v1/auth/register", json={
        "email": f"{uuid.uuid4()}@test.com", "password": "SecurePass123", "full_name": "Test User",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(client):
    email = f"{uuid.uuid4()}@test.com"
    payload = {"email": email, "password": "SecurePass123", "full_name": "Test User"}

    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_login_with_wrong_password_fails(client):
    email = f"{uuid.uuid4()}@test.com"
    await client.post("/api/v1/auth/register", json={"email": email, "password": "CorrectPass123", "full_name": "Test"})

    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "WrongPassword"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_listing_requires_auth(client):
    resp = await client.post("/api/v1/listings", json={
        "title": "iPhone 13", "condition": "used_good",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_and_publish_listing_flow(client):
    email = f"{uuid.uuid4()}@test.com"
    reg = await client.post("/api/v1/auth/register", json={"email": email, "password": "SecurePass123", "full_name": "Seller"})
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post("/api/v1/listings", json={
        "title": "iPhone 13 Pro", "condition": "used_good", "price": 800,
    }, headers=headers)
    assert create_resp.status_code == 201
    listing_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "draft"

    # النشر بدون فئة يفشل (تحقق business rule بـ ListingService.publish)
    publish_fail = await client.patch(f"/api/v1/listings/{listing_id}/status", json={"status": "active"}, headers=headers)
    assert publish_fail.status_code == 400


@pytest.mark.asyncio
async def test_price_insight_empty_category_returns_zero(client):
    # فئة بلا إعلانات نشطة → count=0 وكل الأسعار None (بدون خطأ)
    resp = await client.get("/api/v1/listings/price-insight", params={"category_id": str(uuid.uuid4())})
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 0
    assert body["min_price"] is None
    assert body["avg_price"] is None
    assert body["max_price"] is None


@pytest.mark.asyncio
async def test_new_user_is_not_verified_seller(client):
    email = f"{uuid.uuid4()}@test.com"
    reg = await client.post("/api/v1/auth/register", json={"email": email, "password": "SecurePass123", "full_name": "Fresh Seller"})
    token = reg.json()["access_token"]
    me = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    user_id = me.json()["id"]

    resp = await client.get(f"/api/v1/users/{user_id}")
    assert resp.status_code == 200
    # مستخدم جديد بلا مبيعات → غير موثوق، والحقل موجود في الاستجابة
    assert resp.json()["is_verified_seller"] is False


@pytest.mark.asyncio
async def test_bump_requires_auth(client):
    resp = await client.post(f"/api/v1/listings/{uuid.uuid4()}/bump")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_bump_nonexistent_listing_returns_404(client):
    email = f"{uuid.uuid4()}@test.com"
    reg = await client.post("/api/v1/auth/register", json={"email": email, "password": "SecurePass123", "full_name": "Seller"})
    token = reg.json()["access_token"]

    resp = await client.post(f"/api/v1/listings/{uuid.uuid4()}/bump", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_bump_draft_listing_rejected(client):
    email = f"{uuid.uuid4()}@test.com"
    reg = await client.post("/api/v1/auth/register", json={"email": email, "password": "SecurePass123", "full_name": "Seller"})
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post("/api/v1/listings", json={
        "title": "Draft Bike", "condition": "used_good", "price": 150,
    }, headers=headers)
    listing_id = create_resp.json()["id"]

    # الإعلان لا يزال مسودة — الرفع مسموح فقط للنشط
    bump_resp = await client.post(f"/api/v1/listings/{listing_id}/bump", headers=headers)
    assert bump_resp.status_code == 400


@pytest.mark.asyncio
async def test_other_user_cannot_edit_listing(client):
    seller_email = f"{uuid.uuid4()}@test.com"
    other_email = f"{uuid.uuid4()}@test.com"

    seller_reg = await client.post("/api/v1/auth/register", json={"email": seller_email, "password": "SecurePass123", "full_name": "Seller"})
    seller_token = seller_reg.json()["access_token"]

    other_reg = await client.post("/api/v1/auth/register", json={"email": other_email, "password": "SecurePass123", "full_name": "Other"})
    other_token = other_reg.json()["access_token"]

    create_resp = await client.post("/api/v1/listings", json={
        "title": "Couch", "condition": "used_good", "price": 200,
    }, headers={"Authorization": f"Bearer {seller_token}"})
    listing_id = create_resp.json()["id"]

    edit_resp = await client.put(f"/api/v1/listings/{listing_id}", json={"title": "Hacked title"},
                                  headers={"Authorization": f"Bearer {other_token}"})
    assert edit_resp.status_code == 403
