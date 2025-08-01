"""
clarification_prompt.py
clarification_prompt 누락된 정보를 자연스럽게 묻는 질문을 생성 - checker가 True 반환한 경우에만 호출
"""

from langchain_core.prompts import PromptTemplate

# 1. 도서 추천 intent
book_recommendation_prompt = PromptTemplate(
    input_variables = ["emotion", "genre", "author"],
    template="""
    당신은 감정 기반 도서 추천 챗봇입니다.
    사용자의 요청에서 다음 정보가 부족합니다:
    - 감정(emotion): {emotion}
    - 장르(genre): {genre}
    - 작가(author): {author}
    
    당신의 임무는 **누락된 정보에 따라 질문 혹은 문장만 생성하는 것**입니다.

    규칙:
       다음 규칙에 따라 필요한 질문을 생성하세요:
    - 감정과 장르 모두 누락된 경우 → 둘 다 물어보는 질문
    - 장르만 누락된 경우 → 장르를 물어보는 질문
    - 감정만 누락되었더라도 장르가 주어졌다면 **절대 감정에 대해 묻지 마세요**
    - 감정이 없더라도 장르가 있다면 추천이 가능합니다. 감정 질문은 하지 마세요.
    - 정보가 충분하면 아무것도 출력하지 마세요.
    
    예시 참고 (복붙하지 마세요. 새롭게 자연스럽게 만드세요):
    - "요즘 어떤 기분이신가요?"
    - "어떤 종류의 책을 읽고 싶으세요?"
    - "감정과 장르를 함께 알려주시면 더 정확한 추천이 가능해요!"
    """
)

# 2. 도서 정보 intent
book_info_prompt = PromptTemplate(
    input_variables = ["title", "author"],
    template="""
    책 정보를 찾으려면 다음 정보가 필요합니다:
    - 책 제목(title): {title}
    - 작가(author): {author}
    
    부족한 정보를 요청하는 자연스러운 문장이나 질문을 작성하세요.
    예: "직기 이름이나 책 제목을 알려주시면 정보를 찾을 수 있어요."    
    """
)

# 3. 주문 확인 intent
order_check_prompt = PromptTemplate(
    input_variables=["order_id", "title"],
    template="""
    주문 확인을 위해 다음 정보가 필요합니다:
    - 주문 번호(order_id): {order_id}
    - 책 제목(title): {title}
    
    부족한 정보를 요청하는 자연스러운 문장이나 질문을 작성하세요.
    예: "주문번호나 주문하신 책 제목을 알려주시면 확인해드릴게요."
    """
)

# 4. 재고 확인 intent
stock_check_prompt = PromptTemplate(
    input_variables=["title"],
    template="""
    재고 확인을 위해 다음 정보가 필요합니다:
    - 책 제목(title): {title}
    
    부족한 정보를 요청하는 자연스러운 문장이나 질문을 작성하세요.
    예: "어떤 책의 재고를 확인하고 싶으신가요? 제목을 알려주세요."    
    """
)

clarify_intent_prompt = PromptTemplate(
    input_variables=["keywords"],
    template="""
    사용자의 질문이 너무 모호하여 정확한 요청 의도를 파악할 수 없습니다.
    
    추출된 키워드: {keywords}
    
    사용자에게 어떤 목적의 요청인지 명확히 알기 위해, 다음 중 하나를 물어보세요:
    - 도서 추천이 필요한가요?
    - 책 정보가 궁금하신가요?
    - 재고 확인이나 주문 조회를 원하시나요?
    
    자연스럽고 단 하나의 질문으로 다시 물어보세요.
"""
)

# 내부 매핑 (외부 노출 안 함)
_prompt_by_intent = {
    "recommendation": book_recommendation_prompt,
    "info": book_info_prompt,
    "order_check": order_check_prompt,
    "stock_check": stock_check_prompt,
    "clarification": clarify_intent_prompt
}

# 외부에서 호출할 함수
def get_clarification_prompt(intent: str) -> PromptTemplate:
    if intent not in _prompt_by_intent:
        raise ValueError(f"Invalid intent: {intent}")
    return _prompt_by_intent[intent]