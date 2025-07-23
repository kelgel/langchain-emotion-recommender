"""
intent_classify_prompt.py
intent_classification_prompt 화행 분류 프롬프트
"""

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# 1. .env 파일에서 환경변수 불러오기
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set.")

# 프롬프트 템플릿 정의
intent_classify_prompt  = PromptTemplate(
    input_variables = ["user_input"],
    template="""
다음 사용자 질문이 어떤 목적(intent)를 가지고 있는지 분석하세요.

- 도서 추천 요청이면 "recommendation"
- 도서, 작가, 출판사 등에 대한 정보 요청이면 "info"
- 주문/재고 확인 요청이면 "order_check"
- 질문이 불명확하거나 명확한 분류가 어려우면 "clarification"

사용자 입력: {user_input}

응답 형식 (텍스트만) :
recommendation / info / order_check / clarification
    """
)

# LLM 객체 정의 (실행은 다른 곳에서 사용)
intent_classify_llm = ChatOpenAI(api_key=openai_api_key, temperature=0.0)