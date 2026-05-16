"""
llm.py — Gemini LLM Service

BUG FIX: Prompt được cải thiện để LLM luôn dùng cụm từ rõ ràng
khi không có dữ liệu (giúp rag.py phát hiện và ẩn sources đi).
"""

import json
from app.config import settings
from app.utils.logger import app_logger
from typing import Optional

_FALLBACK = {
    "answer": (
        "Dạ, mình đang gặp chút sự cố kết nối với bộ não AI. "
        "Bạn thử lại sau giây lát nhé! 🙏"
    ),
    "suggestions": [
        "Kể về lịch sử hình thành UIT?",
        "Những thành tựu nổi bật của UIT?",
        "Đời sống sinh viên UIT ra sao?",
    ],
}


<<<<<<< HEAD
def _get_client(api_key: str = ""):
    key = api_key or settings.GOOGLE_API_KEY
    if not key:
        raise RuntimeError("Chưa có API key.")
    from google import genai
    from google.genai import types
    return genai.Client(
        api_key=key,
        http_options=types.HttpOptions(api_version="v1beta"),
    )
=======
def _get_client():
    """Lazy-init Gemini client — tránh crash khi API key chưa có lúc import."""
    if not settings.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY chưa được cấu hình trong file .env")

    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=settings.GOOGLE_API_KEY,
        http_options=types.HttpOptions(api_version="v1beta"),
    )
    return client
>>>>>>> 4fae41abd0e1045de723f8af8830902cc4219760


def _build_history_block(conversation_history: list) -> str:
    """Chuyển lịch sử hội thoại thành chuỗi văn bản cho LLM."""
    if not conversation_history:
        return ""
    lines = ["LỊCH SỬ HỘI THOẠI TRƯỚC ĐÓ:"]
    for turn in conversation_history[-settings.MAX_HISTORY_TURNS:]:
        lines.append(f"Người dùng: {turn.get('question', '')}")
        lines.append(f"Trợ lý: {turn.get('answer', '')}")
    return "\n".join(lines)


def generate_text(
    query: str,
    context: str,
    scope: str,
    is_first_message: bool = True,
    conversation_history: Optional[list] = None,
    used_web: bool = False,
<<<<<<< HEAD
    api_key: str = "",
=======
>>>>>>> 4fae41abd0e1045de723f8af8830902cc4219760
) -> dict:
    """
    Sinh câu trả lời từ Gemini LLM với hỗ trợ hội thoại nhiều lượt.

    Args:
        query: Câu hỏi người dùng.
        context: Văn bản ngữ cảnh (từ vector DB hoặc web).
        scope: "uit" hoặc "cnpm".
        is_first_message: Có phải lượt đầu tiên không.
        conversation_history: Lịch sử hội thoại.
        used_web: True nếu context lấy từ web (để note trong prompt).
    """
    from google.genai import types

    role_name = (
        "Trường Đại học Công nghệ Thông tin (UIT)"
        if scope == "uit"
        else "Khoa Công nghệ Phần mềm (CNPM) - Trường UIT"
    )

    history_block = _build_history_block(conversation_history or [])

    # Ghi chú nguồn context cho LLM
    context_note = (
        "📌 Tài liệu bên dưới được lấy từ website UIT chính thức (thời gian thực)."
        if used_web
        else "📌 Tài liệu bên dưới là dữ liệu nội bộ đã được kiểm duyệt."
    )

    sys_instruct = f"""Bạn là chuyên gia tư vấn và trợ lý AI ảo đại diện cho {role_name}.
Nhiệm vụ của bạn là cung cấp thông tin CHÍNH XÁC, ĐẦY ĐỦ và CHI TIẾT.

QUY TẮC NGHIÊM NGẶT:
1. Tuyệt đối bám sát tài liệu được cung cấp. Trình bày rõ ràng các năm tháng, sự kiện, thành tựu.
2. CẤM trả lời chung chung. Nếu tài liệu có nhiều ý, hãy dùng gạch đầu dòng (-) cho dễ đọc.
3. Nếu tài liệu HOÀN TOÀN KHÔNG chứa thông tin liên quan đến câu hỏi, hãy trả lời ĐÚNG nguyên văn:
   "Dạ, hiện tại dữ liệu của mình chưa cập nhật thông tin chi tiết về vấn đề này."
   ← QUAN TRỌNG: Phải dùng đúng cụm từ này (không paraphrase) để hệ thống nhận diện được.
4. Luôn giữ thái độ thân thiện, xưng "mình" và gọi người dùng là "bạn", dùng emoji ✨ vừa phải.
5. {"Chào người dùng tự nhiên ở đầu câu trả lời." if is_first_message else "KHÔNG chào hỏi (Xin chào, Dạ chào,...), đi thẳng vào nội dung."}
6. Nếu có LỊCH SỬ HỘI THOẠI, hãy tham chiếu ngữ cảnh đó để câu trả lời liền mạch, tự nhiên.

ĐỊNH DẠNG ĐẦU RA (JSON) — chỉ trả về JSON, không thêm bất kỳ text nào ngoài JSON:
{{
  "answer": "<câu trả lời chi tiết ở đây>",
  "suggestions": ["<gợi ý 1>", "<gợi ý 2>", "<gợi ý 3>"]
}}

QUY TẮC CHO SUGGESTIONS:
- Đúng 3 gợi ý, mỗi gợi ý tối đa 8 từ tiếng Việt
- Tiếp nối câu chuyện tự nhiên từ câu trả lời vừa rồi
- Không lặp lại nội dung câu hỏi hiện tại
- Dẫn dắt người dùng khám phá sâu hơn về {role_name}"""

    prompt_parts = []
    if history_block:
        prompt_parts.append(history_block)
    prompt_parts.append(f"{context_note}\nTÀI LIỆU CUNG CẤP:\n{context}" if context.strip() else "TÀI LIỆU CUNG CẤP: (Không có dữ liệu nội bộ liên quan)")
    prompt_parts.append(f"CÂU HỎI TỪ NGƯỜI DÙNG:\n{query}")
    prompt = "\n\n".join(prompt_parts)

    try:
<<<<<<< HEAD
        client = _get_client(api_key=api_key)
=======
        client = _get_client()
>>>>>>> 4fae41abd0e1045de723f8af8830902cc4219760
        response = client.models.generate_content(
            model=settings.LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct,
                temperature=settings.TEMPERATURE,
                max_output_tokens=settings.MAX_TOKENS,
                response_mime_type="application/json",
            ),
        )

        # Xử lý response — có thể là JSON thuần hoặc bọc trong ```json ... ```
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        data = json.loads(raw)
        return {
            "answer":      str(data.get("answer",      _FALLBACK["answer"])),
            "suggestions": list(data.get("suggestions", _FALLBACK["suggestions"]))[:3],
        }

    except RuntimeError as e:
        # API key chưa cấu hình
        app_logger.error(f"❌ LLM không khả dụng: {e}")
        return {
            "answer": "Dạ, tính năng AI chưa được cấu hình (thiếu API key). Vui lòng liên hệ quản trị viên. 🙏",
            "suggestions": _FALLBACK["suggestions"],
        }
    except json.JSONDecodeError as e:
        app_logger.error(f"❌ LLM trả về JSON không hợp lệ: {e}\nRaw: {response.text[:200]}")
        return _FALLBACK
    except Exception as e:
        app_logger.error(f"❌ Lỗi LLM: {e}", exc_info=True)
        return _FALLBACK
