"""
parse_keyword.py
**책 추천을 위한 감정/장르/키워드 추출 결과(JSON 문자열)**를 dict로 변환하는 함수
"""
import json

def parse_keywords(output) -> dict:

    # AIMessage일 경우 content를 꺼냄
    if hasattr(output, "content"):
        output = output.content

    try:
        return json.loads(output) #JSON 형식의 문자열을 파이썬 dict로 변환
    except json.JSONDecodeError: #파싱에 실패하면 기본 빈 구조 반환
        return {
            "emotion": None,
            "genre": None,
            "keywords": []
        }
