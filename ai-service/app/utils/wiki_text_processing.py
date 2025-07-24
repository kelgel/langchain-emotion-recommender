#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
위키피디아 검색 에이전트 - 텍스트 처리 유틸리티
작가명 추출, 텍스트 파싱 등 텍스트 처리 관련 유틸리티 함수들
"""

import re
import json
from typing import Optional, List


class WikiTextProcessor:
    """텍스트 처리 관련 유틸리티 클래스"""
    
    @staticmethod
    def extract_author_name(query: str, llm_client=None) -> str:
        """쿼리에서 작가명을 추출 - 개선된 방식."""
        
        # 먼저 LLM으로 시도
        if llm_client:
            try:
                system_prompt = """사용자 질문에서 작가명만 추출하세요.

JSON 형식으로 응답:
{
    "author_name": "추출된 작가명",
    "confidence": 0.0-1.0
}

예시:
"한강이 누구야" -> {"author_name": "한강", "confidence": 0.9}
"무라카미 하루키 작가 알려줘" -> {"author_name": "무라카미 하루키", "confidence": 0.95}
"개미 쓴 작가 누구야" -> {"author_name": null, "confidence": 0.1}"""

                response = llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.1,
                    max_tokens=100
                )
                
                result = json.loads(response.choices[0].message.content)
                if result.get('author_name') and result.get('confidence', 0) > 0.7:
                    return result['author_name']
                    
            except Exception as e:
                pass  # 폴백으로 진행
        
        # 폴백: 기존 방식
        return WikiTextProcessor._fallback_extract_author_name(query)
    
    @staticmethod
    def _fallback_extract_author_name(query: str) -> str:
        """폴백용 작가명 추출."""
        
        # 1단계: "X가/이 누구야" 패턴 우선 처리 - 조사를 명확히 분리
        who_patterns = [
            r'^([가-힣]{2,4})가\s*누구',     # "한강가 누구" - "가" 조사
            r'^([가-힣]{2,4})이\s*누구',     # "한강이 누구" - "이" 조사  
            r'^([가-힣]{2,4})\s+누구',       # "한강 누구" - 조사 없음
        ]
        
        for pattern in who_patterns:
            match = re.match(pattern, query.strip())
            if match:
                return match.group(1)
        
        # 2단계: 외국 이름 우선 추출 (띄어쓰기 포함)
        foreign_patterns = [
            r'^([A-Za-z]+\s+[A-Za-z]+)',  # "무라카미 하루키"
            r'^([가-힣]+\s+[가-힣]+)',    # "무라카미 하루키" (한글 표기)
        ]
        
        for pattern in foreign_patterns:
            match = re.match(pattern, query.strip())
            if match:
                return match.group(1).strip()
        
        # 3단계: 한글 이름 (2-4글자) - 질문 단어가 없는 경우만
        if not any(word in query for word in ['누구', '뭐', '어떤', '언제', '어디', '알려줘']):
            korean_match = re.match(r'^([가-힣]{2,4})', query.strip())
            if korean_match:
                return korean_match.group(1)
        
        # 4단계: 키워드 제거 방식 (폴백)
        safe_keywords = [
            '어디', '언제', '몇', '어떤', '누구', '나이',
            '대학', '대학교', '학교', '고등학교', '중학교', '초등학교',
            '출신', '졸업', '나옴', '나왔', '다녔', '공부했',
            '작가', '소설가', '시인', '저자', '정보', '알려줘', '말해줘',
            '?', '!', '.', '은', '는', '이', '가', '야'
        ]
        
        cleaned = query.strip()
        for keyword in safe_keywords:
            cleaned = cleaned.replace(keyword, ' ')
        
        # 정리하고 추출
        cleaned = ' '.join(cleaned.split())
        if cleaned and len(cleaned) >= 2:
            # 첫 번째 단어가 작가명일 가능성이 높음
            first_word = cleaned.split()[0] if cleaned.split() else ''
            if len(first_word) >= 2:
                return first_word
        
        return ''

    @staticmethod
    def parse_clarification_response(query: str, context) -> Optional[str]:
        """명확화 응답을 파싱하여 작가명을 추출."""
        import re
        
        # 숫자 선택 패턴 (예: "1", "2번", "첫번째")
        number_patterns = [
            r'^(\d+)번?$',           # "1", "2번"
            r'^(\d+)$',              # "1"
            r'(\d+)번째',            # "2번째"
            r'첫\s*번째',            # "첫번째"
            r'두\s*번째',            # "두번째"  
            r'세\s*번째',            # "세번째"
        ]
        
        for pattern in number_patterns:
            match = re.search(pattern, query.strip())
            if match:
                if '첫' in query:
                    choice_num = 1
                elif '두' in query:
                    choice_num = 2
                elif '세' in query:
                    choice_num = 3
                else:
                    choice_num = int(match.group(1))
                
                # context에서 해당하는 작가명 선택
                candidates = context.get('clarification_candidates', [])
                if 1 <= choice_num <= len(candidates):
                    return candidates[choice_num - 1]
        
        # 직접 작가명 언급 (예: "한강 말하는거야")
        direct_patterns = [
            r'([가-힣]{2,4})\s*말하는',      # "한강 말하는거야"
            r'([가-힣]{2,4})\s*맞아',        # "한강 맞아"
            r'([가-힣]{2,4})\s*이야',        # "한강이야"
            r'([가-힣]{2,4})\s*요',          # "한강요"
        ]
        
        for pattern in direct_patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1)
        
        return None

    @staticmethod
    def extract_author_from_context_question(query: str) -> Optional[str]:
        """컨텍스트 질문에서 작가명을 추출."""
        import re
        
        # "이말년은 어디 대학" 같은 패턴
        context_patterns = [
            r'^([가-힣]{2,4})(?:은|는|이|가)?\s*(?:어디|언제|몇|어떤)',  # "이말년은 어디"
            r'^([가-힣]{2,4})\s+(?:대학|고등학교|출생|나이)',        # "이말년 대학"
        ]
        
        for pattern in context_patterns:
            match = re.match(pattern, query.strip())
            if match:
                return match.group(1)
        
        return None

    @staticmethod
    def extract_book_title_from_query(query: str) -> str:
        """쿼리에서 책 제목을 추출."""
        
        # 기본 정리
        book_title = query.lower().strip()
        
        # 제거할 키워드들
        keywords_to_remove = [
            '작가', '누가', '저자', '지은이', '쓴이', '쓴', '정보', '누구야', '누구',
            '는', '은', '이', '가', '를', '을', '의', '에', '와', '과',
            '?', '!', '.', ':', ';', '알려줘', '말해줘', '어떤', '뭐', '무엇'
        ]
        
        for keyword in keywords_to_remove:
            book_title = book_title.replace(keyword, ' ')
        
        # 연속된 공백 정리
        book_title = ' '.join(book_title.split())
        
        # 특수 패턴 처리
        book_title = WikiTextProcessor._handle_conjunction_in_title(book_title)
        
        return book_title.strip()

    @staticmethod
    def _handle_conjunction_in_title(title: str) -> str:
        """책 제목의 접속사 처리."""
        import re
        
        # "그리고" 패턴 처리
        if '그리고' in title:
            # "A 그리고 B" -> "A와 B" 또는 "A, B"로 정규화
            title = re.sub(r'그리고', '와', title)
        
        # 기타 접속사 처리
        conjunctions = {
            '하고': '와',
            '랑': '와', 
            '이랑': '와'
        }
        
        for old, new in conjunctions.items():
            title = title.replace(old, new)
        
        return title