import uuid

import redis
from rq import Queue

from app.core.config import get_settings

settings = get_settings()
_redis_conn = redis.from_url(settings.REDIS_URL)
_queue = Queue("ai_generation", connection=_redis_conn)


class AIService:
    """الموديول الوحيد اللي يلمس الـ Queue مباشرة. listings module ينادي
    enqueue_listing_generation فقط ويرجع فوراً — لا يعرف شي عن Redis/RQ."""

    def enqueue_listing_generation(self, listing_id: uuid.UUID, image_urls: list[str], condition: str) -> str:
        from app.modules.ai.tasks import run_ai_generation_job

        # بدون job_id: RQ يولّد ID تلقائياً ونرجعه من job.id. تمريره صراحةً كان
        # يخليه ينحجز كخيار داخلي لـ RQ بدل ما يوصل للدالة كباراميتر.
        job = _queue.enqueue(
            run_ai_generation_job,
            listing_id=str(listing_id),
            image_urls=image_urls,
            condition=condition,
            job_timeout=120,
        )
        return job.id

    def get_job_status(self, job_id: str) -> str:
        job = _queue.fetch_job(job_id)
        if job is None:
            return "not_found"
        return job.get_status()  # queued|started|finished|failed

    def get_job_result(self, job_id: str) -> dict | None:
        job = _queue.fetch_job(job_id)
        if job is None or not job.is_finished:
            return None
        return job.result
