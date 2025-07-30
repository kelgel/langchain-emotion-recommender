"""
intent_classify_prompt.py
intent_classification_prompt 화행 분류 프롬프트
"""

from langchain_core.prompts import PromptTemplate

# 프롬프트 템플릿 정의
intent_classify_prompt  = PromptTemplate(
    input_variables = ["user_input", "conversation_history"],
    template="""당신은 사용자 질문의 의도(intent)를 분석하는 AI입니다.
**이전 대화 맥락을 반드시 참고하여** 현재 질문의 가장 적절한 의도를 파악하세요.

[의도 종류]
- recommendation: 특정 조건(감정, 장르, 키워드 등)에 맞는 도서를 추천해달라는 요청
- info: 특정 도서, 작가, 출판사 등에 대한 사실적 정보를 묻는 요청
- order_check: 주문 상태나 내역을 확인하려는 요청
- stock_check: 특정 도서의 재고 유무를 확인하려는 요청
- clarification: 의도가 매우 불분명하거나 여러 의도로 해석될 수 있는 모호한 질문

[분석 규칙]
1.  **가장 중요한 규칙: 이전 대화가 'info' 또는 'recommendation'이었고, 현재 질문이 해당 주제(예: 특정 작가, 특정 책)에 대한 후속 질문(예: "그 사람 가족 정보 알려줘", "다른 작품은 없어?")이라면, 현재 질문의 의도도 이전과 동일하게 유지하세요.**
2.  사용자 질문이 명확하게 새로운 주제로 전환된 경우에만 의도를 새로 판단하세요.
3.  인사,雑談, 감정 표현 등은 이전 의도를 유지하거나, 맥락이 없으면 'clarification'으로 처리하세요.

[대화 예시]
- 이전 대화:
  user: 베르나르 베르베르에 대해 알려줘
  assistant: (베르나르 베르베르 정보)
- 현재 사용자 입력: 그의 가족 관계는?
- 분석 결과: info (이전 'info' 의도를 이어받은 후속 질문)

- 이전 대화:
  user: 요즘 읽을 만한 소설 추천해줘
  assistant: (소설 추천 목록)
- 현재 사용자 입력: 그 중에서 가장 인기 있는 건 뭐야?
- 분석 결과: recommendation (이전 'recommendation' 의도를 이어받은 후속 질문)

- 이전 대화:
  (대화 없음)
- 현재 사용자 입력: 안녕하세요
- 분석 결과: clarification (명확한 의도 없음)

---
[실제 분석 작업]
이전 대화:
{conversation_history}

현재 사용자 입력: {user_input}

분석된 의도 (오직 한 단어):
"""
)


