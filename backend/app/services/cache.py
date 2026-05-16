"""
cache.py — Redis Cache Service

v2.4 FIXES:
  - Thêm is_first_message vào cache key để phân biệt response có lời chào vs không
  - Thêm in-process fallback dict khi Redis không khả dụng (giới hạn 500 entry)
"""

import redis
import hashlib
import json
from app.config import settings
from app.utils.logger import app_logger

# ── Kết nối Redis ──────────────────────────────────────────────────────────────
try:
    redis_client = redis.Redis(
    host=settings.REDIS_URL,
<<<<<<< HEAD
    port=settings.REDIS_PORT,
    decode_responses=True,
    username=settings.REDIS_USERNAME,
    password=settings.REDIS_PASSWORD,
=======
    port=16634,
    decode_responses=True,
    username="default",
    password="XkuUtNwd67Pjc72jKfui9Kqn6bnERJTa",
>>>>>>> 4fae41abd0e1045de723f8af8830902cc4219760
    socket_connect_timeout=5,
    socket_timeout=5
    )
    redis_client.ping()
    app_logger.info("✅ Đã kết nối thành công với Redis Cloud!")
except Exception as e:
    app_logger.error(f"⚠️ Không thể kết nối Redis. Hệ thống sẽ dùng in-process cache. Lỗi: {e}")
    redis_client = None

# ── Fallback in-process cache khi Redis không có ──────────────────────────────
_local_cache: dict = {}
_LOCAL_CACHE_MAX = 500


def _generate_key(query: str, scope: str, is_first_message: bool = True) -> str:
    """
    Tạo cache key từ query + scope + is_first_message.
    is_first_message ảnh hưởng lời chào nên cần phân biệt.
    """
    raw_str = f"{scope}_{int(is_first_message)}_{query.lower().strip()}"
    hash_str = hashlib.md5(raw_str.encode("utf-8")).hexdigest()
    return f"chat_cache:{hash_str}"


def get_cached_answer(query: str, scope: str, is_first_message: bool = True):
    """Lấy câu trả lời từ cache (Redis ưu tiên, fallback in-process)."""
    key = _generate_key(query, scope, is_first_message)

    if redis_client:
        try:
            data = redis_client.get(key)
            if data:
                app_logger.debug("⚡ Redis cache HIT")
                return json.loads(data)
            return None
        except Exception as e:
            app_logger.error(f"Lỗi khi đọc Redis Cache: {e}")

    # Fallback: in-process dict
    return _local_cache.get(key)


def set_cached_answer(query: str, scope: str, is_first_message: bool, result_data: dict):
    """Lưu câu trả lời vào cache (Redis ưu tiên, fallback in-process)."""
    key = _generate_key(query, scope, is_first_message)

    if redis_client:
        try:
            redis_client.set(key, json.dumps(result_data), ex=settings.CACHE_TTL)
            return
        except Exception as e:
            app_logger.error(f"Lỗi khi ghi Redis Cache: {e}")

    # Fallback: in-process dict (giới hạn kích thước)
    if len(_local_cache) >= _LOCAL_CACHE_MAX:
        # Xoá 100 entry đầu
        for k in list(_local_cache.keys())[:100]:
            del _local_cache[k]
    _local_cache[key] = result_data
