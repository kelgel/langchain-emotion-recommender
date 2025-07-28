#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
위키피디아 검색 에이전트 - 패턴 매칭 유틸리티
질문 패턴 인식, 작가명 패턴, 책-작가 패턴 등을 처리하는 유틸리티 함수들
"""

import re
from typing import List


class WikiPatternMatcher:
    """패턴 매칭 관련 유틸리티 클래스"""
    
    @staticmethod
    def is_author_result(search_result) -> bool:
        """검색 결과가 작가에 대한 것인지 판단."""
        if not search_result or not search_result.get('content'):
            return False
        
        content = search_result['content'].lower()
        
        # 작가임을 나타내는 강한 키워드들
        strong_author_keywords = [
            '작가', '소설가', '시인', '저자', '문학', '소설', '시집', 
            '작품', '출간', '발표', '문학상', '등단'
        ]
        
        # 작가가 아님을 나타내는 키워드들
        non_author_keywords = [
            '정치인', '대통령', '의원', '시장', '구청장', '군수',
            '배우', '가수', '연예인', '탤런트', '모델',
            '운동선수', '선수', '축구', '야구', '농구',
            '기업인', '회장', '사장', '대표이사',
            '학자', '교수', '연구원', '박사'
        ]
        
        # 비작가 키워드가 있으면 false
        if any(keyword in content for keyword in non_author_keywords):
            return False
        
        # 작가 키워드가 있으면 true
        return any(keyword in content for keyword in strong_author_keywords)

    @staticmethod
    def is_new_author_query(query: str) -> bool:
        """새로운 작가 검색 쿼리인지 판단."""
        query_lower = query.lower()
        
        # 새로운 작가 검색을 나타내는 패턴들
        new_author_patterns = [
            r'[가-힣]{2,4}\s*(?:작가|소설가|시인)',  # "한강 작가"
            r'[가-힣]{2,4}\s*(?:누구|알려줘)',       # "한강 누구"
            r'[가-힣]{2,4}\s*(?:정보|소개)',         # "한강 정보"
        ]
        
        return any(re.search(pattern, query_lower) for pattern in new_author_patterns)

    @staticmethod
    def is_book_to_author_pattern(query: str) -> bool:
        """책 제목으로 작가를 찾는 패턴인지 판단."""
        query_lower = query.lower()
        
        # 책-작가 질문 패턴들
        book_to_author_keywords = ['작가', '누가', '저자', '지은이', '쓴이', '쓴']
        
        # 작가 질문 키워드가 있고, 인물명이 명확하지 않은 경우
        has_author_keyword = any(keyword in query_lower for keyword in book_to_author_keywords)
        
        # 명확한 인물명 패턴이 없는 경우
        clear_person_patterns = [
            r'^[가-힣]{2,4}\s*(?:누구|알려줘|정보)',  # "한강 누구"
            r'^[가-힣]{2,4}\s*작가'                   # "한강 작가"
        ]
        
        has_clear_person = any(re.match(pattern, query_lower) for pattern in clear_person_patterns)
        
        return has_author_keyword and not has_clear_person

    @staticmethod
    def contains_author_name(query: str) -> bool:
        """쿼리에 작가명이 포함되어 있는지 판단."""
        # 한글 이름 패턴 (2-4글자)
        korean_name_pattern = r'[가-힣]{2,4}'
        
        # 영어 이름 패턴 (FirstName LastName)
        english_name_pattern = r'[A-Za-z]+\s+[A-Za-z]+'
        
        return bool(re.search(korean_name_pattern, query) or 
                   re.search(english_name_pattern, query))

    @staticmethod
    def contains_author_info(query: str) -> bool:
        """쿼리에 작가 관련 정보가 포함되어 있는지 판단."""
        query_lower = query.lower()
        
        author_info_keywords = [
            '작가', '소설가', '시인', '저자', '문학',
            '작품', '소설', '시집', '에세이', '책',
            '출간', '발표', '등단', '데뷔'
        ]
        
        return any(keyword in query_lower for keyword in author_info_keywords)

    @staticmethod
    def generate_search_patterns(author_name: str) -> List[str]:
        """작가명에 대한 다양한 검색 패턴 생성."""
        patterns = []
        
        if author_name:
            # 기본 패턴들
            patterns.extend([
                f"{author_name} (작가)",
                f"{author_name} 작가",
                f"{author_name} 소설가",
                f"{author_name} 시인",
                author_name
            ])
            
            # 외국 작가인 경우 추가 패턴
            if any(char.isalpha() and ord(char) > 127 for char in author_name):
                # 한글 표기가 있는 경우
                patterns.append(f"{author_name} 한국어")
                patterns.append(f"{author_name} 번역")
            
            # 띄어쓰기가 있는 이름의 경우
            if ' ' in author_name:
                # 띄어쓰기 제거 버전
                no_space_name = author_name.replace(' ', '')
                patterns.append(no_space_name)
                patterns.append(f"{no_space_name} 작가")
        
        return patterns

    @staticmethod
    def extract_context_keywords(query: str) -> List[str]:
        """컨텍스트 질문에서 키워드 추출."""
        query_lower = query.lower()
        
        # 컨텍스트 키워드 매핑
        context_keywords = {
            '대학': ['대학', '대학교', '대학원'],
            '학교': ['고등학교', '중학교', '초등학교', '학교'],
            '출생': ['태어', '출생', '생일', '태어난'],
            '나이': ['나이', '몇살', '나이가'],
            '작품': ['작품', '책', '소설', '시집', '에세이'],
            '수상': ['상', '수상', '시상', '문학상', '대상'],
            '가족': ['아버지', '어머니', '부모', '가족', '부친', '모친']
        }
        
        found_keywords = []
        for category, keywords in context_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                found_keywords.append(category)
        
        return found_keywords

    @staticmethod
    def is_clarification_response(query: str) -> bool:
        """명확화 응답인지 판단."""
        query_lower = query.lower().strip()
        
        # 숫자 선택 패턴
        number_patterns = [
            r'^\d+번?$',           # "1", "2번"
            r'^\d+$',              # "1"
            r'\d+번째',            # "2번째"
            r'첫\s*번째',          # "첫번째"
            r'두\s*번째',          # "두번째"
        ]
        
        # 직접 언급 패턴
        direct_patterns = [
            r'[가-힣]{2,4}\s*말하는',      # "한강 말하는거야"
            r'[가-힣]{2,4}\s*맞아',        # "한강 맞아"
            r'[가-힣]{2,4}\s*이야',        # "한강이야"
        ]
        
        all_patterns = number_patterns + direct_patterns
        return any(re.search(pattern, query_lower) for pattern in all_patterns)

    @staticmethod
    def detect_question_type(query: str) -> str:
        """질문 유형 감지."""
        query_lower = query.lower()
        
        # 질문 유형별 키워드 매핑
        question_types = {
            'who': ['누구', '누가', '어떤 사람', '인물'],
            'where': ['어디', '어느', '장소'],
            'when': ['언제', '몇년', '시기'],
            'what': ['뭐', '무엇', '어떤'],
            'how': ['어떻게', '방법'],
            'why': ['왜', '이유', '때문']
        }
        
        for q_type, keywords in question_types.items():
            if any(keyword in query_lower for keyword in keywords):
                return q_type
        
        return 'general'

    @staticmethod
    def has_person_name_pattern(query: str) -> bool:
        """인명 패턴이 있는지 확인."""
        # 한글 인명 패턴 (2-4글자)
        korean_name = re.search(r'[가-힣]{2,4}', query)
        
        # 영어 인명 패턴
        english_name = re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+', query)
        
        return bool(korean_name or english_name)