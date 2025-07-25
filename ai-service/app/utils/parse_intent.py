"""
parse_intent.py
**질문 의도 분류 결과 (단어 하나)**를 정제된 문자열로 변환
"""
def parse_intent(output) -> str:
    # LLM이 반환한 객체가 AIMessage면 content를 꺼냄
    if hasattr(output, "content"):
        output = output.content

    return output.strip().lower() #앞뒤 공백 제거와 대소문자 통일
