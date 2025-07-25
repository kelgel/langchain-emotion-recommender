"""
parse_keyword.py
**책 추천을 위한 감정/장르/키워드 추출 결과(JSON 문자열)**를 dict로 변환하는 함수
"""
import json

def parse_keywords(output) -> dict:
    """
    다양한 intent에 대응하는 키워드를 포함한 결과를 dict로 파싱.
    누락된 필드가 있으면 기본값으로 채움.
    """

    # AIMessage 또는 기타 객체의 content 속성 접근
    if hasattr(output, "content"):
        output = output.content

    defaults = {
        "emotion": None,
        "genre": None,
        "keywords": [],
        "title": None,
        "author": None,
        "order_id": None
    }

    try:
        parsed = json.loads(output)
        if not isinstance(parsed, dict):
            raise ValueError("Parsed result is not a dict")
    except (json.JSONDecodeError, ValueError):
        # 실패 시 defaults만 반환
        return defaults

    # 누락된 필드는 기본값으로 채움
    return {**defaults, **parsed}

