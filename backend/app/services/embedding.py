"""
embedding.py — Google Gemini Embedding Service

v2.4 FIXES:
  - Thêm in-memory cache cho embedding vector (tránh gọi API lặp lại cùng câu hỏi)
  - Cache tối đa 1000 entry, tự dọn khi đầy
"""

from app.config import settings
from app.utils.logger import app_logger

_client = None

# ── In-memory embedding cache ──────────────────────────────────────────────────
_embedding_cache: dict = {}   # normalized_text → list[float]
_CACHE_MAX_SIZE = 1000
_CACHE_EVICT_COUNT = 200       # xoá bao nhiêu entry khi cache đầy


<<<<<<< HEAD
def _get_client(api_key: str = ""):
    key = api_key or settings.GOOGLE_API_KEY
    if not key:
        raise RuntimeError("Chưa có API key — người dùng cần nhập key qua giao diện.")
    from google import genai
    from google.genai import types as _types
    return genai.Client(
        api_key=key,
        http_options=_types.HttpOptions(api_version="v1beta"),
    )


def get_embedding(text: str, api_key: str = "") -> list:
=======
def _get_client():
    """Khởi tạo Gemini client theo yêu cầu (lazy init)."""
    global _client
    if _client is not None:
        return _client

    if not settings.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY chưa được cấu hình trong file .env")

    from google import genai
    from google.genai import types as _types

    _client = genai.Client(
        api_key=settings.GOOGLE_API_KEY,
        http_options=_types.HttpOptions(api_version="v1beta"),
    )
    return _client


def get_embedding(text: str) -> list:
>>>>>>> 4fae41abd0e1045de723f8af8830902cc4219760
    """
    Tạo vector embedding từ văn bản đầu vào bằng Google Gemini.
    Kết quả được cache in-memory để tránh gọi API lặp lại.

    Raises:
        ValueError: Nếu text rỗng.
        RuntimeError: Nếu API key chưa cấu hình hoặc API lỗi.
    """
    from google.genai import types

    text = text.replace("\n", " ").strip()
    if not text:
        raise ValueError("Văn bản đầu vào không được trống khi tạo embedding.")

    # ── Kiểm tra cache trước khi gọi API ──────────────────────────────────────
    cache_key = text.lower()
    if cache_key in _embedding_cache:
        app_logger.debug("⚡ Embedding cache HIT")
        return _embedding_cache[cache_key]

    try:
<<<<<<< HEAD
        client = _get_client(api_key=api_key)
=======
        client = _get_client()
>>>>>>> 4fae41abd0e1045de723f8af8830902cc4219760
        response = client.models.embed_content(
            model=settings.EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
        )
        vector = response.embeddings[0].values

        # ── Lưu vào cache (với giới hạn kích thước) ───────────────────────────
        if len(_embedding_cache) >= _CACHE_MAX_SIZE:
            keys_to_evict = list(_embedding_cache.keys())[:_CACHE_EVICT_COUNT]
            for k in keys_to_evict:
                del _embedding_cache[k]
            app_logger.debug(f"🧹 Embedding cache evicted {_CACHE_EVICT_COUNT} entries")

        _embedding_cache[cache_key] = vector
        return vector

    except RuntimeError:
        raise
    except Exception as e:
        app_logger.error(f"❌ Lỗi Embedding API: {e}", exc_info=True)
        raise RuntimeError(f"Không thể tạo embedding: {e}") from e
