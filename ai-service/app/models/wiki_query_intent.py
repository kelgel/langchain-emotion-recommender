#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
위키피디아 검색 에이전트 - 쿼리 의도 분석 모델
사용자 질문의 의도를 분석하고 분류하는 데이터 모델
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class IntentType(Enum):
    """질문 의도 타입"""
    AUTHOR_SEARCH = "author_search"  # 새로운 작가 검색
    CONTEXT_QUESTION = "context_question"  # 기존 컨텍스트 기반 질문
    BOOK_TO_AUTHOR = "book_to_author"  # 책 제목으로 작가 찾기


class InfoType(Enum):
    """구체적인 정보 요청 타입"""
    UNIVERSITY = "university"  # 대학교 정보
    BIRTH = "birth"  # 출생 정보
    DEATH = "death"  # 사망 정보
    SCHOOL = "school"  # 학교 정보
    WORKS = "works"  # 작품 정보
    AWARDS = "awards"  # 수상 정보
    FAMILY = "family"  # 가족 정보
    FATHER = "father"  # 아버지 정보
    MOTHER = "mother"  # 어머니 정보
    GENERAL = "general"  # 일반 정보


@dataclass
class WikiQueryIntent:
    """쿼리 의도 분석 결과"""
    intent_type: IntentType
    query: str
    extracted_keywords: List[str] = field(default_factory=list)
    specific_info_request: Optional[InfoType] = None
    book_title: Optional[str] = None
    confidence: float = 0.0
    reasoning: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환 (기존 코드 호환성을 위해)"""
        if self.intent_type == IntentType.BOOK_TO_AUTHOR:
            return {
                'type': 'book_to_author',
                'book_title': self.book_title or (self.extracted_keywords[0] if self.extracted_keywords else self.query)
            }
        elif self.intent_type == IntentType.CONTEXT_QUESTION:
            return {
                'type': 'context_question',
                'question': self.query,
                'specific_info': self.specific_info_request.value if self.specific_info_request else None
            }
        else:  # AUTHOR_SEARCH
            return {
                'type': 'author_search',
                'query': self.query,
                'specific_info': self.specific_info_request.value if self.specific_info_request else None,
                'keywords': self.extracted_keywords
            }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], original_query: str) -> 'WikiQueryIntent':
        """딕셔너리에서 객체 생성 (기존 코드 호환성을 위해)"""
        intent_type_str = data.get('type', 'author_search')
        
        # IntentType 매핑
        intent_type_map = {
            'author_search': IntentType.AUTHOR_SEARCH,
            'context_question': IntentType.CONTEXT_QUESTION,
            'book_to_author': IntentType.BOOK_TO_AUTHOR
        }
        intent_type = intent_type_map.get(intent_type_str, IntentType.AUTHOR_SEARCH)
        
        # InfoType 매핑
        specific_info = None
        if data.get('specific_info'):
            info_type_map = {
                'university': InfoType.UNIVERSITY,
                'birth': InfoType.BIRTH,
                'death': InfoType.DEATH,
                'school': InfoType.SCHOOL,
                'works': InfoType.WORKS,
                'awards': InfoType.AWARDS,
                'family': InfoType.FAMILY,
                'father': InfoType.FATHER,
                'mother': InfoType.MOTHER,
                'general': InfoType.GENERAL
            }
            specific_info = info_type_map.get(data['specific_info'])
        
        return cls(
            intent_type=intent_type,
            query=original_query,
            extracted_keywords=data.get('keywords', []),
            specific_info_request=specific_info,
            book_title=data.get('book_title'),
            confidence=data.get('confidence', 0.0),
            reasoning=data.get('reasoning', '')
        )

    @classmethod
    def create_author_search(cls, query: str, keywords: List[str] = None, 
                           specific_info: InfoType = None) -> 'WikiQueryIntent':
        """작가 검색 의도 생성"""
        return cls(
            intent_type=IntentType.AUTHOR_SEARCH,
            query=query,
            extracted_keywords=keywords or [],
            specific_info_request=specific_info
        )

    @classmethod
    def create_context_question(cls, query: str, specific_info: InfoType = None) -> 'WikiQueryIntent':
        """컨텍스트 질문 의도 생성"""
        return cls(
            intent_type=IntentType.CONTEXT_QUESTION,
            query=query,
            specific_info_request=specific_info
        )

    @classmethod
    def create_book_to_author(cls, query: str, book_title: str) -> 'WikiQueryIntent':
        """책-작가 검색 의도 생성"""
        return cls(
            intent_type=IntentType.BOOK_TO_AUTHOR,
            query=query,
            book_title=book_title,
            extracted_keywords=[book_title]
        )