"""
query_analysis_prompt.py
query_analysis_prompt 질의 분석 프롬프트
"""

from langchain_core.prompts import PromptTemplate

# 프롬프트 템플릿 정의
query_analysis_prompt = PromptTemplate(
    input_variables = ["user_input", "conversation_history"],
    template="""
당신은 감정 기반 도서 추천 시스템의 텍스트 분석 AI입니다.

사용자의 요청을 분석하여 다음 정보를 추출하세요(해당 필드가 없다면 null로 설정하세요) 
- 단, '주문 조회', '책 추천' 등 일반적인 행위는 order_id나 title로 추출하지 마세요.
- order_id는 실제 주문 번호처럼 보이는 숫자 또는 코드만 해당됩니다.
- 이전 대화 맥락을 참고하여 현재 질문의 의도를 파악하세요.

- emotion(감정): 예)우울, 행복, 사랑 등
- genre(장르) :  예)에세이, 판타지, 스릴러 등
- author(작가명): 예) 김영하, 김초엽, 천선란 등
- title(도서명): 예)천 개의 파랑, 채식주의자 등
- publisher(출판사): 예) 허블, 창비 등
- order_id(주문 번호): 예) 1234567890
- keywords(중요 단어): 사용자의 요구에서 중심이 되는 핵심 단어들

이전 대화:
{conversation_history}

현재 사용자 입력: {user_input}

응답 형식 (JSON):
{{
    "emotion": "...",
    "genre": "...",
    "author": "...",
    "title": "...",
    "publisher": "...",
    "order_id": "...",
    "keywords": ["...", "...", "..."]
}}
    """
)



