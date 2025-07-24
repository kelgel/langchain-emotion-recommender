"""
intent_classify_prompt.py
intent_classification_prompt 화행 분류 프롬프트
"""

from langchain_core.prompts import PromptTemplate

# 프롬프트 템플릿 정의
intent_classify_prompt  = PromptTemplate(
    input_variables = ["user_input"],
    template="""
다음 사용자 질문이 어떤 목적(intent)를 가지고 있는지 분석하세요.

- 도서 추천 요청이면 "recommendation"
- 도서, 작가, 출판사 등에 대한 정보 요청이면 "info"
- 주문 확인 요청이면 "order_check"
- 재고 확인 요청이면 "stock_check"
- 질문이 불명확하거나 명확한 분류가 어려우면 "clarification"

사용자 입력: {user_input}

응답 형식 (텍스트만) :
recommendation / info / order_check / stock_check / clarification
"""
)


