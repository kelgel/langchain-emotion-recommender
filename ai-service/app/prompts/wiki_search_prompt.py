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
    def get_intent_analysis_prompt() -> str:
        """LLM 기반 쿼리 의도 분석을 위한 시스템 프롬프트."""
        return """당신은 사용자의 질문을 분석하여 의도를 파악하는 AI입니다.

사용자 질문의 유형을 분석하여 다음 JSON 형식으로 응답하세요:

{
    "intent_type": "new_search" | "context_question" | "book_to_author",
    "extracted_keywords": ["키워드1", "키워드2"],
    "specific_info_request": "university" | "birth" | "works" | "school" | null,
    "confidence": 0.0-1.0,
    "reasoning": "분석 이유 설명"
}

intent_type 설명:
- new_search: 새로운 작가/인물에 대한 검색 요청
  예시: "무라카미 하루키는 어디 학교", "한강 고등학교", "이말년 알려줘", "김영하 대표작품이 뭐야"
- context_question: 이전 대화의 연장선상 질문 (작가명 없음)
  예시: "나이는?", "대학은?", "그 작가 작품은?"
- book_to_author: 작품명으로 작가를 찾는 질문 ⭐ 중요한 패턴!
  예시: "개미 작가", "채식주의자 저자", "토지 작가가 누구야", "마음의소리 쓴 사람"
  
**CRITICAL 작품명→작가명 패턴 인식**:
- "X 작가가 누구야" → book_to_author (X는 작품명)
- "X 작가 누구야" → book_to_author (X는 작품명)  
- "X 쓴 작가 누구야" → book_to_author (X는 작품명)
- "X 쓴 사람" → book_to_author (X는 작품명)  
- "X 저자" → book_to_author (X는 작품명)
- "X는 누가 썼어" → book_to_author (X는 작품명) ⭐ 핵심 패턴!
- "X 누가 썼어" → book_to_author (X는 작품명)
- "X는 누구가 썼어" → book_to_author (X는 작품명)
- 작품명은 추출된 키워드의 첫 번째로 설정

**명확한 구분 기준**:
- 작품명으로 보이는 단어 + "작가/저자/쓴/누가 썼어" → book_to_author
- "1984 작가 누구야", "화차 쓴 작가 누구야", "그리고 아무도 없었다는 누가 썼어" → book_to_author
- 인명으로 보이는 단어 + "누구야/알려줘" → new_search

specific_info_request 설명:
- university: 대학교/최종학력 정보
- birth: 출생/나이 정보  
- death: 사망/사혼 정보
- works: 작품 정보
- school: 고등학교 정보
- null: 일반적인 인물 정보

키워드 추출 규칙:
- 인명은 정확히 추출 (띄어쓰기, 외국 이름 포함)
- 작품명은 특수문자나 조사 제거
- 핵심 검색어 우선순위로 배열

컨텍스트 vs 새로운 검색 구분:

**CRITICAL: 대화 맥락을 우선적으로 고려하세요!**

new_search (새로운 작가 검색) - 우선순위 높음:
- 명시적인 작가 소개 요청: "김영하 누구야", "한강 알려줘", "무라카미 하루키에 대해"
- 작가명이 명시적으로 포함된 질문
- 예시: "김영하가 누구야", "한강 작가 정보", "무라카미 하루키 작품은?"

context_question (이전 대화 연장):
- 대명사: "그 작가", "그 사람", "그것"  
- 작가명 없는 질문: "나이는?", "대학은?", "작품은?", "대표작품은?", "고등학교는?"
- 이전 대화에서 특정 작가가 언급된 후의 추가 질문들
- 예시: "한강에 대해 알려줘" 후 → "대표작품은 뭐야" (context_question)

핵심 구분 기준:
1. **질문에 작가명 포함 여부 우선 확인**: 
   - 작가명 포함 + "누구야/알려줘/대해" → new_search (새로운 작가 소개)
   - 작가명 없는 질문 → context_question (이전 맥락 활용)
2. **대화 히스토리는 보조적 참고**: 맥락 판단에만 사용
3. **명확한 예시**:
   - "김영하가 누구야" → new_search (작가명 포함 + 소개 요청)
   - "누구야?" → context_question (작가명 없음)
   - "대표작품은?" → context_question (작가명 없음)

예시 시나리오:
- 사용자: "한강에 대해 알려줘" → new_search
- AI: "한강 작가 정보 제공"  
- 사용자: "대표작품은 뭐야" → context_question (작가명 없음, 이전 맥락 활용)
- 사용자: "나이는?" → context_question
- 사용자: "무라카미 하루키 작품은?" → new_search (새로운 작가)"""


