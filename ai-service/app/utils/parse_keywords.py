"""
parse_keyword.py
**책 추천을 위한 감정/장르/키워드 추출 결과(JSON 문자열)**를 dict로 변환하는 함수
"""
import json

def parse_keywords(output) -> dict:
    """
    다양한 intent에 대응하는 키워드를 포함한 결과를 dict로 파싱
    """

    # AIMessage일 경우 content를 꺼냄
    if hasattr(output, "content"):
        output = output.content

    try:
        return json.loads(output) #JSON 형식의 문자열을 파이썬 dict로 변환
    except json.JSONDecodeError:
        # 기본 필드만 빈 값으로 구성
        return {
            "emotion": None,
            "genre": None,
            "keywords": [],
            "title": None,
            "author": None,
            "order_id": None
        }

    # 누락된 필드는 기본값으로 채우기
    defaults = {
        "emotion": None,
        "genre": None,
        "keywords": [],
        "title": None,
        "author": None,
        "order_id": None
    }
    return {**defaults, **parsed}
