from app.core.dependencies import Pagination


def test_pagination_defaults():
    p = Pagination()
    assert p.page == 1
    assert p.limit == 20
    assert p.offset == 0


def test_pagination_offset_calculation():
    p = Pagination(page=3, limit=10)
    assert p.offset == 20  # صفحة 3 بحجم 10 = تخطي أول 20 سجل


def test_pagination_rejects_page_below_one():
    p = Pagination(page=0, limit=10)
    assert p.page == 1  # يُصحَّح تلقائياً بدل ما يرمي خطأ


def test_pagination_caps_limit_at_100():
    p = Pagination(page=1, limit=99999)
    assert p.limit == 100  # حماية من طلب صفحات ضخمة تضغط على DB


def test_pagination_rejects_negative_limit():
    p = Pagination(page=1, limit=-5)
    assert p.limit == 1
