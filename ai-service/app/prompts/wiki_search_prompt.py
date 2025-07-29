#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
위키피디아 검색 프롬프트 - Prompt 계층
사용자와의 대화 메시지 템플릿을 제공
"""

class WikiSearchPrompt:
    """위키피디아 검색 관련 프롬프트 클래스."""

    @staticmethod
    def get_clarification_request(author_name: str) -> str:
        """작가 정보가 모호할 때 사용자에게 대표작품을 요청하는 메시지."""
        msg = "'{}'으로 검색된 결과가 작가가 아닙니다. 어떤 작품을 쓴 '{}' 작가 말씀하시는 건가요? 대표작품을 말씀해주세요."
        return msg.format(author_name, author_name)

    @staticmethod  
    def get_search_failure_message(author_name: str) -> str:
        """작가 검색 실패시 대표작품을 요청하는 메시지."""
        msg = "'{}' 작가를 위키피디아에서 찾을 수 없습니다.\n\n다음 중 하나를 시도해보세요:\n1. 정확한 작가명으로 다시 검색\n2. 대표작품을 알려주세요 (예: \"채식주의자\", \"개미\" 등)\n3. 다른 작가에 대해 질문해보세요"
        return msg.format(author_name)

    @staticmethod
    def get_combined_search_failure_message(author_name: str, book_title: str) -> str:
        """작가명과 작품명으로 검색했지만 실패했을 때의 메시지."""
        msg = "'{}' 작가의 '{}' 작품으로 검색했지만 결과를 찾을 수 없습니다. 다른 대표작을 알려주세요."
        return msg.format(author_name, book_title)

    @staticmethod
    def format_author_response(wiki_result: dict) -> str:
        """작가 정보 응답을 사용자 친화적으로 포맷팅."""
        # URL의 괄호를 인코딩하여 터미널에서 클릭 가능하도록 처리
        url = wiki_result.get('url', '')
        clickable_url = url.replace('(', '%28').replace(')', '%29')
        
        title = wiki_result.get('title', '')
        response = "**{}**\n\n".format(title)
        
        # 요약 정보 (200자로 제한)
        summary = wiki_result.get('summary', '')[:200]
        response += "**요약**: {}...\n\n".format(summary)
        
        # 클릭 가능한 URL 제공  
        response += "**상세 정보**: {}\n\n".format(clickable_url)
        response += "더 궁금한 것이 있으시면 언제든 물어보세요!"
        
        return response

    @staticmethod
    def get_general_error_message() -> str:
        """일반적인 오류 메시지."""
        return "죄송합니다. 검색 중 오류가 발생했습니다. 다시 시도해주세요."


    @staticmethod
    def get_ambiguous_query_message() -> str:
        """모호한 질문에 대한 응답 메시지."""
        return "질문이 명확하지 않습니다. 어떤 작가에 대해 알고 싶으신지 구체적으로 말씀해주세요."

    @staticmethod
    def get_author_summary_prompt() -> str:
        """작가 정보 요약을 위한 LLM 프롬프트."""
        return """당신은 위키피디아 정보를 바탕으로 사용자의 질문에 답변하는 AI입니다.

사용자의 질문 유형에 따라 적절한 범위의 정보를 제공하세요:

**1. 기본 소개 질문** ("OO 작가에 대해 알려줘", "OO 정보", "OO는 누구야?")
→ 위키피디아 첫 번째 문단(서머리)의 핵심 정보만 제공
→ 출생년도, 국적, 주요 업적, 대표작 위주
→ **중요: 부모, 가족 정보는 절대 포함하지 마세요**

**2. 구체적 정보 질문** ("부모님은?", "대표작은?", "언제 태어났어?")
→ 해당 질문에 직접 관련된 정보만 제공
→ 가족 정보를 명시적으로 물어봤을 때만 부모님 정보 제공
→ "A와 B 사이에서 태어났다", "소설가 X의 딸/아들" 패턴 인식

**답변 규칙:**
- 질문 유형에 따라 엄격하게 범위 제한
- 기본 소개에서는 부모/가족 정보 언급 금지
- 정보가 없으면 "찾을 수 없습니다"라고 솔직히 답변
- 자연스러운 한국어 사용
- 간결하고 명확하게 작성

**답변 예시:**
- 기본 소개: "홍성훈은 1945년 출생의 대한민국 아동문학가, 언론인, 연극인, 풍수지리가입니다."
- 가족 질문: "한강은 소설가 한승원의 딸입니다."
"""

    @staticmethod
    def get_book_summary_prompt() -> str:
        """책 정보 요약을 위한 LLM 프롬프트."""
        return """당신은 위키피디아 정보를 바탕으로 사용자의 질문에 답변하는 AI입니다.

주어진 위키피디아 정보를 바탕으로, 다음 항목을 포함하여 책을 자연스럽게 소개해주세요.

1.  **저자(작가)**: 이 책을 쓴 사람을 명확히 언급해주세요. (예: "재러드 다이아몬드가 쓴 책입니다.")
2.  **핵심 내용**: 책의 주제와 핵심 주장을 2~3문장으로 요약해주세요.
3.  **특징 및 평가**: 책의 의의, 수상 내역, 영향력 등을 간략하게 포함해주세요.

**답변 규칙:**
- 반드시 저자를 먼저 언급하고 책 내용을 설명하세요.
- 모든 정보를 조합하여 자연스러운 문장으로 만드세요.
- 정보가 부족하면 있는 내용만으로 구성하세요.
- 간결하고 명확하게 작성하세요.

**답변 예시:**
"총, 균, 쇠는 재러드 다이아몬드가 쓴 문화 이론서입니다. 이 책은 유라시아 문명이 다른 문명을 정복할 수 있었던 이유가 지리적 차이 때문이라고 주장하며, 1998년 퓰리처상을 수상했습니다."
"""

    @staticmethod
    def get_intent_analysis_prompt() -> str:
        """[수정 3.0] LLM 기반 쿼리 의도 분석. 단일 명사 처리 규칙 강화."""
        return """당신은 사용자의 질문을 분석하여 의도를 파악하는 AI입니다.

**CRITICAL RULE: 사용자의 새 질문이 이전 대화 주제와 명백한 관련이 없다면, 반드시 'author_search' 또는 'book_to_author'로 분류해야 합니다. '현재 대화 주제'에 현혹되지 마세요.**

사용자 질문의 유형을 분석하여 다음 JSON 형식으로 응답하세요:
{
    "intent_type": "author_search" | "context_question" | "book_to_author",
    "extracted_keywords": ["키워드1", "키워드2"],
    "specific_info_request": "author" | "university" | "birth" | "works" | "school" | null,
    "confidence": 0.0-1.0,
    "reasoning": "분석 이유 설명"
}

**의도 분류 기준 (우선순위 순):**

1.  **`book_to_author` (가장 높은 우선순위):**
    - **CASE A (단일 고유명사):** 질문이 책 제목으로 보이는 1~2개의 단어로만 이루어진 경우. **이 규칙을 최우선으로 적용하세요.**
        - 예: "개미", "토지", "채식주의자", "희랍어 시간"
        - **주의: "요시모토 바나나", "한강", "박경리" 등 작가명은 author_search입니다**
        - 이 경우, `specific_info_request`는 `null`입니다.
    - **CASE B (명시적 저자 질문):** 질문에 '작가', '저자', '쓴 사람', '누가 썼어' 등의 키워드가 포함된 경우.
        - 예: "총균쇠 저자", "채식주의자는 누가 썼어?"
        - 이 경우, `specific_info_request`를 **'author'**로 설정하세요.

2.  **`author_search`:**
    - `book_to_author`가 아니면서, 이전 대화와 관련 없는 새로운 인물, 책, 개념이 명시된 경우.
    - **작가명이 명시적으로 포함된 모든 질문은 author_search입니다.**
    - 예: "김영하 작가 정보", "무라카미 하루키의 대표작은?", "다자이 오사무 출생일과 사망일"
    - **중요: "다자이 오사무", "한강", "박경리", "요시모토 바나나", "무라카미 하루키" 등 작가명이 직접 언급되면 무조건 author_search입니다.**
    - **예시: "한강 부모님 이름", "한강 가족 정보", "김영하 나이" 등도 모두 author_search입니다.**
    - **인명 패턴: 한글 2-4글자 + 공백 + 한글 2-4글자 (예: "요시모토 바나나")도 작가명으로 간주**

3.  **`context_question`:**
    - 질문에 새로운 고유명사가 **전혀 없고**, '그 작가', '나이는?', '대학은 어디야?', '저자는 누구야?' 와 같이 명백히 이전 대화에 의존하는 경우.
    - **작가명이 직접 언급되면 절대 context_question이 아닙니다.**
    - 만약 "저자", "작가"를 묻는다면 `specific_info_request`를 **'author'**로 설정하세요.
"""


