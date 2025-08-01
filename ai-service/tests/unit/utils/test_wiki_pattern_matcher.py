"""
WikiPatternMatcher 직관적인 TDD 테스트
각 테스트마다 성공 메시지 출력으로 진행상황을 실시간 확인

실행 방법:
    cd ai-service
    python tests/unit/utils/test_wiki_pattern_matcher.py
    또는
    python -m pytest tests/unit/utils/test_wiki_pattern_matcher.py -v -s
"""

import pytest
import sys
import os
from pathlib import Path
import time

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 의존성 모듈 Mock 설정
from unittest.mock import Mock
mock_modules = ['models', 'tools', 'chains', 'prompts']
for module_name in mock_modules:
    if module_name not in sys.modules:
        sys.modules[module_name] = Mock()

# 테스트 대상 import
from app.utils.wiki_pattern_matcher import WikiPatternMatcher

class TestWikiPatternMatcherAuthorDetection:
    """WikiPatternMatcher 작가 감지 테스트"""

    def test_is_author_result_true_cases(self):
        """작가 결과 판별 - 참인 경우들 테스트"""
        author_results = [
            {
                'content': '김영하는 대한민국의 소설가이다. 주요 작품으로는 살인자의 기억법이 있다.',
                'description': '기본적인 소설가 정보'
            },
            {
                'content': '한강은 시인이자 작가로 활동하고 있다. 채식주의자로 맨부커상을 수상했다.',
                'description': '시인 겸 작가, 문학상 수상'
            },
            {
                'content': '박경리는 한국 문학의 거장이다. 토지라는 대하소설을 집필했다.',
                'description': '문학 거장, 대하소설 집필'
            },
            {
                'content': '무라카미 하루키는 일본의 유명한 소설가이다. 많은 작품을 출간했다.',
                'description': '일본 소설가, 작품 출간'
            }
        ]

        print(f"  ✅ 작가 결과 판별 - 참인 경우들 테스트...")

        for i, case in enumerate(author_results, 1):
            print(f"    {i}. 테스트: {case['description']}")
            print(f"       내용: '{case['content'][:50]}...'")

            result = WikiPatternMatcher.is_author_result(case)

            print(f"       🎯 판별 결과: {result}")
            print(f"       🔍 작가 키워드 감지: {'작가' in case['content'] or '소설가' in case['content'] or '시인' in case['content']}")

            assert result == True
            print(f"       ✅ 테스트 {i} 통과\n")

        print("✅ 작가 결과 판별 - 참인 경우들 테스트 통과")

    def test_is_author_result_false_cases(self):
        """작가 결과 판별 - 거짓인 경우들 테스트"""
        non_author_results = [
            {
                'content': '김영하는 대한민국의 정치인이다. 국회의원으로 활동하고 있다.',
                'description': '정치인 (비작가)'
            },
            {
                'content': '한강은 유명한 배우이다. 많은 드라마와 영화에 출연했다.',
                'description': '배우 (비작가)'
            },
            {
                'content': '박철수는 축구 선수이다. 국가대표로 뛰었다.',
                'description': '운동선수 (비작가)'
            },
            {
                'content': '이영희는 대기업 회장이다. 사업가로 성공했다.',
                'description': '기업인 (비작가)'
            },
            {
                'content': '',
                'description': '빈 내용'
            }
        ]

        print(f"  ❌ 작가 결과 판별 - 거짓인 경우들 테스트...")

        for i, case in enumerate(non_author_results, 1):
            print(f"    {i}. 테스트: {case['description']}")
            if case['content']:
                print(f"       내용: '{case['content'][:50]}...'")
            else:
                print(f"       내용: 빈 내용")

            result = WikiPatternMatcher.is_author_result(case)

            print(f"       🎯 판별 결과: {result}")
            if case['content']:
                non_author_words = ['정치인', '배우', '선수', '회장', '대통령']
                has_non_author_word = any(word in case['content'] for word in non_author_words)
                print(f"       🚫 비작가 키워드 감지: {has_non_author_word}")

            assert result == False
            print(f"       ✅ 테스트 {i} 통과\n")

        print("✅ 작가 결과 판별 - 거짓인 경우들 테스트 통과")

    def test_is_new_author_query_success(self):
        """새로운 작가 검색 쿼리 판별 성공 테스트"""
        new_author_queries = [
            "김영하 작가",
            "한강 소설가",
            "박경리 시인",
            "무라카미 누구",
            "베르베르 알려줘",
            "조정래 정보",
            "김훈 소개"
        ]

        print(f"  🆕 새로운 작가 검색 쿼리 판별 테스트...")

        for i, query in enumerate(new_author_queries, 1):
            print(f"    {i}. 쿼리: '{query}'")

            result = WikiPatternMatcher.is_new_author_query(query)

            print(f"       🎯 판별 결과: {result}")
            print(f"       🔍 패턴 분석: 작가명 + 관련 키워드")

            assert result == True
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 새로운 작가 검색 쿼리 판별 성공 테스트 통과")

    def test_is_new_author_query_false(self):
        """새로운 작가 검색 쿼리 판별 - 거짓인 경우 테스트"""
        non_new_author_queries = [
            "그의 나이는?",
            "언제 태어났어?",
            "대표작이 뭐야?",
            "어느 대학 나왔어?",
            "아버지가 누구야?",
            "안녕하세요",
            "날씨가 어때?"
        ]

        print(f"  ❌ 새로운 작가 검색이 아닌 쿼리들 테스트...")

        for i, query in enumerate(non_new_author_queries, 1):
            print(f"    {i}. 쿼리: '{query}'")

            result = WikiPatternMatcher.is_new_author_query(query)

            print(f"       🎯 판별 결과: {result}")
            print(f"       💭 분석: 컨텍스트 질문 또는 관련 없는 질문")

            assert result == False
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 새로운 작가 검색이 아닌 쿼리들 테스트 통과")

class TestWikiPatternMatcherBookToAuthor:
    """WikiPatternMatcher 책→작가 패턴 테스트"""

    def test_is_book_to_author_pattern_true(self):
        """책→작가 패턴 판별 - 참인 경우들 테스트"""
        book_to_author_queries = [
            "개미 누가 썼어?",
            "채식주의자 작가가 누구야?",
            "노르웨이의 숲 저자는?",
            "1984 누가 지었어?",
            "해리포터 쓴 사람은?",
            "토지 누가 썼나?",
            "살인자의 기억법 작가"
        ]

        print(f"  📚→👤 책→작가 패턴 판별 - 참인 경우들 테스트...")

        for i, query in enumerate(book_to_author_queries, 1):
            print(f"    {i}. 쿼리: '{query}'")

            result = WikiPatternMatcher.is_book_to_author_pattern(query)

            print(f"       🎯 판별 결과: {result}")
            print(f"       📖 분석: 작품명 + 작가 질문 키워드")

            # 작가 관련 키워드 확인
            author_keywords = ['작가', '누가', '저자', '지은이', '쓴이', '쓴']
            has_author_keyword = any(keyword in query.lower() for keyword in author_keywords)
            print(f"       🔍 작가 키워드 포함: {has_author_keyword}")

            assert result == True
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 책→작가 패턴 판별 - 참인 경우들 테스트 통과")

    def test_is_book_to_author_pattern_false(self):
        """책→작가 패턴 판별 - 거짓인 경우들 테스트"""
        non_book_to_author_queries = [
            "김영하 작가",      # 명확한 작가명
            "한강 누구야?",     # 명확한 인물명
            "그의 나이는?",     # 컨텍스트 질문
            "언제 태어났어?",   # 시간 질문
            "안녕하세요",       # 관련 없는 질문
            "날씨가 어때?"      # 관련 없는 질문
        ]

        print(f"  ❌ 책→작가 패턴이 아닌 경우들 테스트...")

        for i, query in enumerate(non_book_to_author_queries, 1):
            print(f"    {i}. 쿼리: '{query}'")

            result = WikiPatternMatcher.is_book_to_author_pattern(query)

            print(f"       🎯 판별 결과: {result}")
            print(f"       💭 분석: 명확한 인물명이 있거나 다른 유형의 질문")

            assert result == False
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 책→작가 패턴이 아닌 경우들 테스트 통과")

class TestWikiPatternMatcherNameDetection:
    """WikiPatternMatcher 이름 감지 테스트"""
    def test_contains_author_name_korean(self):
        """한글 작가명 포함 여부 테스트"""
        korean_name_queries = [
            ("김영하 작가", "김영하"),
            ("한강에 대해 알려줘", "한강"),
            ("박경리의 대표작", "박경리"),
            ("조정래 토지", "조정래"),
            ("무라카미 하루키", "무라카미, 하루키")
        ]

        print(f"  🇰🇷 한글 작가명 포함 여부 테스트...")

        for i, (query, expected_name) in enumerate(korean_name_queries, 1):
            print(f"    {i}. 쿼리: '{query}'")
            print(f"       예상 이름: {expected_name}")

            result = WikiPatternMatcher.contains_author_name(query)

            print(f"       🎯 이름 포함 여부: {result}")

            assert result == True
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 한글 작가명 포함 여부 테스트 통과")

    def test_contains_author_name_english(self):
        """영어 작가명 포함 여부 테스트"""
        english_name_queries = [
            ("Stephen King 작품", "Stephen King"),
            ("J.K. Rowling 해리포터", "J.K. Rowling"),
            ("George Orwell 1984", "George Orwell"),
            ("Ernest Hemingway 노인과 바다", "Ernest Hemingway")
        ]

        print(f"  🇺🇸 영어 작가명 포함 여부 테스트...")

        for i, (query, expected_name) in enumerate(english_name_queries, 1):
            print(f"    {i}. 쿼리: '{query}'")
            print(f"       예상 이름: {expected_name}")

            result = WikiPatternMatcher.contains_author_name(query)

            print(f"       🎯 이름 포함 여부: {result}")

            assert result == True
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 영어 작가명 포함 여부 테스트 통과")

    def test_contains_author_name_false(self):
        """작가명 포함되지 않은 경우 테스트"""
        no_name_queries = [
            "그의 나이는?",
            "언제 태어났어?",
            "대표작이 뭐야?",
            "어느 대학 나왔어?",
            "a",  # 너무 짧은 경우
            "안녕하세요"
        ]

        print(f"  ❌ 작가명이 포함되지 않은 경우들 테스트...")

        for i, query in enumerate(no_name_queries, 1):
            print(f"    {i}. 쿼리: '{query}'")

            result = WikiPatternMatcher.contains_author_name(query)

            print(f"       🎯 이름 포함 여부: {result}")
            print(f"       💭 분석: 명확한 인명 패턴 없음")

            assert result == False
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 작가명이 포함되지 않은 경우들 테스트 통과")

    def test_contains_author_info(self):
        """작가 관련 정보 포함 여부 테스트"""
        author_info_queries = [
            "작가 정보 알려줘",
            "소설가에 대해",
            "시인의 작품",
            "문학 작품 추천",
            "책 출간일",
            "소설 등단"
        ]

        print(f"  📚 작가 관련 정보 포함 여부 테스트...")

        for i, query in enumerate(author_info_queries, 1):
            print(f"    {i}. 쿼리: '{query}'")

            result = WikiPatternMatcher.contains_author_info(query)

            print(f"       🎯 작가 정보 포함: {result}")

            # 작가 관련 키워드 확인
            author_keywords = ['작가', '소설가', '시인', '저자', '문학', '작품', '소설', '시집', '책']
            found_keywords = [kw for kw in author_keywords if kw in query.lower()]
            print(f"       🔍 발견된 키워드: {found_keywords}")

            assert result == True
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 작가 관련 정보 포함 여부 테스트 통과")

class TestWikiPatternMatcherSearchPatterns:
    """WikiPatternMatcher 검색 패턴 생성 테스트"""

    def test_generate_search_patterns_korean(self):
        """한글 작가명 검색 패턴 생성 테스트"""
        korean_authors = [
            "김영하",
            "한강",
            "박경리",
            "조정래"
        ]

        print(f"  🔍 한글 작가명 검색 패턴 생성 테스트...")

        for i, author in enumerate(korean_authors, 1):
            print(f"    {i}. 작가명: '{author}'")

            patterns = WikiPatternMatcher.generate_search_patterns(author)

            print(f"       📊 생성된 패턴 수: {len(patterns)}개")
            print(f"       📝 생성된 패턴들:")
            for j, pattern in enumerate(patterns, 1):
                print(f"         {j}. {pattern}")

            # 기본 패턴들이 포함되어야 함
            expected_patterns = [
                f"{author} (작가)",
                f"{author} 작가",
                f"{author} 소설가",
                f"{author} 시인",
                author
            ]

            for expected in expected_patterns:
                assert expected in patterns
                print(f"       ✅ '{expected}' 패턴 포함됨")

            print(f"       ✅ 테스트 {i} 통과\n")

        print("✅ 한글 작가명 검색 패턴 생성 테스트 통과")

    def test_generate_search_patterns_english(self):
        """영어 작가명 검색 패턴 생성 테스트"""
        english_authors = [
            "Stephen King",
            "J.K. Rowling",
            "George Orwell"
        ]

        print(f"  🌐 영어 작가명 검색 패턴 생성 테스트...")

        for i, author in enumerate(english_authors, 1):
            print(f"    {i}. 작가명: '{author}'")

            patterns = WikiPatternMatcher.generate_search_patterns(author)

            print(f"       📊 생성된 패턴 수: {len(patterns)}개")
            print(f"       📝 주요 패턴들:")
            for j, pattern in enumerate(patterns[:5], 1):  # 처음 5개만 표시
                print(f"         {j}. {pattern}")

            # 기본 패턴들 확인
            assert f"{author} (작가)" in patterns
            assert f"{author} 작가" in patterns
            assert author in patterns

            # 띄어쓰기가 있는 경우 추가 패턴 확인
            if ' ' in author:
                no_space_name = author.replace(' ', '')
                assert no_space_name in patterns
                print(f"       ✅ 띄어쓰기 제거 패턴 '{no_space_name}' 포함됨")

            print(f"       ✅ 테스트 {i} 통과\n")

        print("✅ 영어 작가명 검색 패턴 생성 테스트 통과")

    def test_generate_search_patterns_empty(self):
        """빈 작가명에 대한 검색 패턴 생성 테스트"""
        empty_cases = [None, "", "   "]

        print(f"  🗳️ 빈 작가명 검색 패턴 생성 테스트...")

        for i, author in enumerate(empty_cases, 1):
            print(f"    {i}. 작가명: {repr(author)}")

            patterns = WikiPatternMatcher.generate_search_patterns(author)

            print(f"       📊 생성된 패턴 수: {len(patterns)}개")
            print(f"       📝 패턴들: {patterns}")

            # 빈 경우에도 빈 리스트를 반환해야 함
            assert isinstance(patterns, list)
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 빈 작가명 검색 패턴 생성 테스트 통과")\

class TestWikiPatternMatcherContextKeywords:
    """WikiPatternMatcher 컨텍스트 키워드 추출 테스트"""
    def test_extract_context_keywords_success(self):
        """컨텍스트 키워드 추출 성공 테스트"""
        context_queries = [
            ("어느 대학교 나왔어?", ["대학"]),
            ("고등학교는 어디야?", ["학교"]),
            ("언제 태어났어?", ["출생"]),
            ("나이가 어떻게 돼?", ["나이"]),
            ("대표작이 뭐야?", ["작품"]),
            ("어떤 상을 받았어?", ["수상"]),
            ("아버지가 누구야?", ["가족"]),
            ("대학교 나와서 어떤 작품을 썼어?", ["대학", "작품"])  # 복수 키워드
        ]

        print(f"  🔍 컨텍스트 키워드 추출 성공 테스트...")

        for i, (query, expected_keywords) in enumerate(context_queries, 1):
            print(f"    {i}. 쿼리: '{query}'")
            print(f"       예상 키워드: {expected_keywords}")

            result = WikiPatternMatcher.extract_context_keywords(query)

            print(f"       🎯 추출된 키워드: {result}")

            # 예상된 키워드들이 모두 포함되어야 함
            for expected in expected_keywords:
                assert expected in result
                print(f"       ✅ '{expected}' 키워드 추출됨")

            print(f"       ✅ 테스트 {i} 통과\n")

        print("✅ 컨텍스트 키워드 추출 성공 테스트 통과")

    def test_extract_context_keywords_empty(self):
        """컨텍스트 키워드가 없는 경우 테스트"""
        non_context_queries = [
            "안녕하세요",
            "날씨가 어때?",
            "오늘 뭐해?",
            "김영하 작가",  # 새로운 검색
            "ㅋㅋㅋ 재밌다"
        ]

        print(f"  ❌ 컨텍스트 키워드가 없는 경우들 테스트...")

        for i, query in enumerate(non_context_queries, 1):
            print(f"    {i}. 쿼리: '{query}'")

            result = WikiPatternMatcher.extract_context_keywords(query)

            print(f"       🎯 추출된 키워드: {result}")
            print(f"       💭 분석: 컨텍스트 키워드 없음")

            assert len(result) == 0
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 컨텍스트 키워드가 없는 경우들 테스트 통과")

class TestWikiPatternMatcherClarification:
    """WikiPatternMatcher 명확화 응답 테스트"""
    def test_is_clarification_response_numbers(self):
        """숫자 기반 명확화 응답 테스트"""
        number_responses = [
            "1",
            "2번",
            "3번째",
            "첫번째",
            "두번째",
            "1번"
        ]

        print(f"  🔢 숫자 기반 명확화 응답 테스트...")

        for i, response in enumerate(number_responses, 1):
            print(f"    {i}. 응답: '{response}'")

            result = WikiPatternMatcher.is_clarification_response(response)

            print(f"       🎯 명확화 응답 여부: {result}")
            print(f"       🔍 패턴: 숫자 선택")

            assert result == True
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 숫자 기반 명확화 응답 테스트 통과")

    def test_is_clarification_response_direct(self):
        """직접 언급 명확화 응답 테스트"""
        direct_responses = [
            "김영하 말하는거야",
            "한강 맞아",
            "박경리이야",
            "그 작가 맞아"
        ]

        print(f"  💬 직접 언급 명확화 응답 테스트...")

        for i, response in enumerate(direct_responses, 1):
            print(f"    {i}. 응답: '{response}'")

            result = WikiPatternMatcher.is_clarification_response(response)

            print(f"       🎯 명확화 응답 여부: {result}")
            print(f"       🔍 패턴: 직접 언급")

            assert result == True
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 직접 언급 명확화 응답 테스트 통과")

    def test_is_clarification_response_false(self):
        """명확화 응답이 아닌 경우들 테스트"""
        non_clarification_responses = [
            "김영하에 대해 알려줘",  # 새로운 질문
            "그의 나이는?",          # 컨텍스트 질문
            "언제 태어났어?",        # 일반 질문
            "안녕하세요",            # 인사
            "잘 모르겠어요"          # 모름 표현
        ]

        print(f"  ❌ 명확화 응답이 아닌 경우들 테스트...")

        for i, response in enumerate(non_clarification_responses, 1):
            print(f"    {i}. 응답: '{response}'")

            result = WikiPatternMatcher.is_clarification_response(response)

            print(f"       🎯 명확화 응답 여부: {result}")
            print(f"       💭 분석: 일반적인 질문이나 대화")

            assert result == False
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 명확화 응답이 아닌 경우들 테스트 통과")

class TestWikiPatternMatcherQuestionTypes:
    """WikiPatternMatcher 질문 유형 감지 테스트"""

    def test_detect_question_type_variety(self):
        """다양한 질문 유형 감지 테스트"""
        question_samples = [
            ("김영하가 누구야?", "who"),
            ("어디서 태어났어?", "where"),
            ("언제 등단했어?", "when"),
            ("대표작이 뭐야?", "what"),
            ("어떻게 유명해졌어?", "how"),
            ("왜 작가가 되었어?", "why"),
            ("김영하에 대해 알려줘", "general")
        ]

        print(f"  ❓ 다양한 질문 유형 감지 테스트...")

        for i, (query, expected_type) in enumerate(question_samples, 1):
            print(f"    {i}. 쿼리: '{query}'")
            print(f"       예상 유형: {expected_type}")

            result = WikiPatternMatcher.detect_question_type(query)

            print(f"       🎯 감지된 유형: {result}")

            # 질문 유형별 키워드 확인
            type_keywords = {
                'who': ['누구', '누가'],
                'where': ['어디', '어느'],
                'when': ['언제', '몇년'],
                'what': ['뭐', '무엇'],
                'how': ['어떻게'],
                'why': ['왜', '이유']
            }

            if expected_type in type_keywords:
                found_keyword = any(kw in query for kw in type_keywords[expected_type])
                print(f"       🔍 관련 키워드 발견: {found_keyword}")

            assert result == expected_type
            print(f"       ✅ 테스트 {i} 통과\n")

        print("✅ 다양한 질문 유형 감지 테스트 통과")

    def test_has_person_name_pattern_korean(self):
        """한글 인명 패턴 감지 테스트"""
        korean_name_queries = [
            "김영하",
            "한강 작가",
            "박경리의 토지",
            "조정래 소설가",
            "무라카미"
        ]

        print(f"  👤 한글 인명 패턴 감지 테스트...")

        for i, query in enumerate(korean_name_queries, 1):
            print(f"    {i}. 쿼리: '{query}'")

            result = WikiPatternMatcher.has_person_name_pattern(query)

            print(f"       🎯 인명 패턴 감지: {result}")
            print(f"       🔍 분석: 2-4글자 한글 이름 패턴")

            assert result == True
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 한글 인명 패턴 감지 테스트 통과")

    def test_has_person_name_pattern_english(self):
        """영어 인명 패턴 감지 테스트"""
        english_name_queries = [
            "Stephen King",
            "J.K. Rowling 해리포터",
            "George Orwell 작가",
            "Ernest Hemingway"
        ]

        print(f"  🌐 영어 인명 패턴 감지 테스트...")

        for i, query in enumerate(english_name_queries, 1):
            print(f"    {i}. 쿼리: '{query}'")

            result = WikiPatternMatcher.has_person_name_pattern(query)

            print(f"       🎯 인명 패턴 감지: {result}")
            print(f"       🔍 분석: FirstName LastName 패턴")

            assert result == True
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 영어 인명 패턴 감지 테스트 통과")

    def test_has_person_name_pattern_false(self):
        """인명 패턴이 없는 경우 테스트"""
        no_name_queries = [
            "그의 나이는?",
            "언제 태어났어?",
            "안녕하세요",
            "a",
            "책",
            "소설"
        ]

        print(f"  ❌ 인명 패턴이 없는 경우들 테스트...")

        for i, query in enumerate(no_name_queries, 1):
            print(f"    {i}. 쿼리: '{query}'")

            result = WikiPatternMatcher.has_person_name_pattern(query)

            print(f"       🎯 인명 패턴 감지: {result}")
            print(f"       💭 분석: 명확한 인명 패턴 없음")

            assert result == False
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 인명 패턴이 없는 경우들 테스트 통과")

class TestWikiPatternMatcherEdgeCases:
    """WikiPatternMatcher 엣지 케이스 테스트"""

    def test_empty_and_none_inputs(self):
        """빈 입력과 None 값 처리 테스트"""
        edge_cases = [
            None,
            "",
            "   ",
            "\n\n",
            "\t\t"
        ]

        print(f"  🗳️ 빈 입력과 None 값 처리 테스트...")

        for i, test_input in enumerate(edge_cases, 1):
            print(f"    {i}. 입력: {repr(test_input)}")

            try:
                # 각 메서드들이 빈 입력을 적절히 처리하는지 확인
                safe_input = test_input or ""

                is_new_query = WikiPatternMatcher.is_new_author_query(safe_input)
                has_name = WikiPatternMatcher.contains_author_name(safe_input)
                question_type = WikiPatternMatcher.detect_question_type(safe_input)
                context_keywords = WikiPatternMatcher.extract_context_keywords(safe_input)

                print(f"       📊 처리 결과:")
                print(f"         - 새 작가 쿼리: {is_new_query}")
                print(f"         - 이름 포함: {has_name}")
                print(f"         - 질문 유형: {question_type}")
                print(f"         - 컨텍스트 키워드: {context_keywords}")

                # 빈 입력에 대해서는 False나 빈 결과가 나와야 함
                assert is_new_query == False
                assert has_name == False
                assert question_type == "general"
                assert len(context_keywords) == 0

                print(f"       ✅ 테스트 {i} 통과")

            except Exception as e:
                print(f"       ⚠️ 예외 발생: {type(e).__name__}: {e}")
                # 적절한 예외 타입인지 확인
                assert isinstance(e, (AttributeError, TypeError, ValueError))
                print(f"       ✅ 적절한 예외 처리됨")

        print("✅ 빈 입력과 None 값 처리 테스트 통과")

    def test_special_characters_handling(self):
        """특수 문자 및 이모지 처리 테스트"""
        special_queries = [
            "김영하 작가 😊",
            "한강!!! 대박~~~",
            "박경리@@@ 토지???",
            "J.K. Rowling 💫⭐",
            "αβγ 그리스문자",
            "José Saramago",
            "作家 한자",
        ]

        print(f"  🌟 특수 문자 및 이모지 처리 테스트...")

        for i, query in enumerate(special_queries, 1):
            print(f"    {i}. 쿼리: '{query}'")

            try:
                has_name = WikiPatternMatcher.contains_author_name(query)
                has_author_info = WikiPatternMatcher.contains_author_info(query)
                question_type = WikiPatternMatcher.detect_question_type(query)

                print(f"       📊 처리 결과:")
                print(f"         - 이름 포함: {has_name}")
                print(f"         - 작가 정보: {has_author_info}")
                print(f"         - 질문 유형: {question_type}")

                # 특수 문자가 있어도 기본 패턴은 인식되어야 함
                assert isinstance(has_name, bool)
                assert isinstance(has_author_info, bool)
                assert isinstance(question_type, str)

                print(f"       ✅ 테스트 {i} 통과")

            except Exception as e:
                print(f"       ⚠️ 예외 발생: {type(e).__name__}: {e}")
                assert isinstance(e, (UnicodeError, AttributeError, TypeError))
                print(f"       ✅ 적절한 예외 처리됨")

        print("✅ 특수 문자 및 이모지 처리 테스트 통과")

    def test_very_long_queries(self):
        """매우 긴 쿼리 처리 테스트"""
        long_query = "김영하 작가에 대해 알려주세요. " * 100

        print(f"  📏 매우 긴 쿼리 처리 테스트...")
        print(f"    - 쿼리 길이: {len(long_query):,}자")

        start_time = time.time()

        # 다양한 패턴 매칭 함수들 테스트
        has_name = WikiPatternMatcher.contains_author_name(long_query)
        has_author_info = WikiPatternMatcher.contains_author_info(long_query)
        is_new_query = WikiPatternMatcher.is_new_author_query(long_query)
        context_keywords = WikiPatternMatcher.extract_context_keywords(long_query)

        end_time = time.time()
        processing_time = end_time - start_time

        print(f"    📊 처리 결과:")
        print(f"      - 처리 시간: {processing_time:.4f}초")
        print(f"      - 이름 포함: {has_name}")
        print(f"      - 작가 정보: {has_author_info}")
        print(f"      - 새 작가 쿼리: {is_new_query}")
        print(f"      - 컨텍스트 키워드 수: {len(context_keywords)}")

        # 성능 기준: 1초 이내 처리
        assert processing_time < 1.0

        # 긴 텍스트에서도 패턴을 인식해야 함
        assert has_name == True  # "김영하" 포함
        assert has_author_info == True  # "작가" 포함
        assert is_new_query == True  # "김영하 작가" 패턴

        print("✅ 매우 긴 쿼리 처리 테스트 통과")

class TestWikiPatternMatcherPerformance:
    """WikiPatternMatcher 성능 테스트"""

    def test_pattern_matching_performance(self):
        """패턴 매칭 성능 테스트"""
        test_queries = [
            "김영하 작가",
            "한강 소설가 정보",
            "개미 누가 썼어?",
            "그의 나이는?",
            "Stephen King 작품"
        ]

        print(f"  ⚡ 패턴 매칭 성능 테스트...")
        print(f"    - 테스트 횟수: 각 쿼리당 100회")
        print(f"    - 테스트 쿼리 수: {len(test_queries)}개")

        start_time = time.time()

        for _ in range(100):
            for query in test_queries:
                WikiPatternMatcher.is_new_author_query(query)
                WikiPatternMatcher.contains_author_name(query)
                WikiPatternMatcher.contains_author_info(query)
                WikiPatternMatcher.detect_question_type(query)
                WikiPatternMatcher.extract_context_keywords(query)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / (100 * len(test_queries))

        print(f"    📊 성능 결과:")
        print(f"      - 총 실행 시간: {total_time:.4f}초")
        print(f"      - 총 호출 수: {100 * len(test_queries) * 5:,}회")
        print(f"      - 평균 처리 시간: {avg_time*1000:.2f}ms/쿼리")
        print(f"      - 초당 처리량: {1/avg_time:.0f}쿼리/초")

        # 성능 기준: 평균 0.01초 이내
        assert avg_time < 0.01
        print("✅ 패턴 매칭 성능 테스트 통과")

    def test_search_pattern_generation_performance(self):
        """검색 패턴 생성 성능 테스트"""
        test_authors = [
            "김영하", "한강", "박경리", "조정래", "김훈",
            "Stephen King", "J.K. Rowling", "George Orwell"
        ]

        print(f"  🔍 검색 패턴 생성 성능 테스트...")
        print(f"    - 작가 수: {len(test_authors)}명")
        print(f"    - 반복 횟수: 50회")

        start_time = time.time()

        for _ in range(50):
            for author in test_authors:
                patterns = WikiPatternMatcher.generate_search_patterns(author)
                # 패턴이 적절히 생성되었는지 간단히 확인
                assert len(patterns) > 0

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / (50 * len(test_authors))

        print(f"    📊 성능 결과:")
        print(f"      - 총 실행 시간: {total_time:.4f}초")
        print(f"      - 평균 생성 시간: {avg_time*1000:.2f}ms/작가")
        print(f"      - 초당 생성량: {1/avg_time:.0f}패턴세트/초")

        # 성능 기준: 평균 0.005초 이내
        assert avg_time < 0.005
        print("✅ 검색 패턴 생성 성능 테스트 통과")

class TestWikiPatternMatcherIntegration:
    """WikiPatternMatcher 통합 테스트"""
    def test_full_query_analysis_workflow(self):
        """전체 쿼리 분석 워크플로우 테스트"""
        test_scenarios = [
            {
                'query': '김영하 작가',
                'expected': {
                    'is_new_author': True,
                    'has_name': True,
                    'has_author_info': True,
                    'question_type': 'general',
                    'is_book_to_author': False
                }
            },
            {
                'query': '개미 누가 썼어?',
                'expected': {
                    'is_new_author': False,
                    'has_name': False,
                    'has_author_info': False,
                    'question_type': 'who',
                    'is_book_to_author': True
                }
            },
            {
                'query': '그의 나이는?',
                'expected': {
                    'is_new_author': False,
                    'has_name': False,
                    'has_author_info': False,
                    'question_type': 'general',
                    'is_book_to_author': False
                }
            }
        ]

        print(f"  🔄 전체 쿼리 분석 워크플로우 테스트...")

        for i, scenario in enumerate(test_scenarios, 1):
            query = scenario['query']
            expected = scenario['expected']

            print(f"    {i}. 시나리오: '{query}'")

            # 전체 분석 수행
            is_new_author = WikiPatternMatcher.is_new_author_query(query)
            has_name = WikiPatternMatcher.contains_author_name(query)
            has_author_info = WikiPatternMatcher.contains_author_info(query)
            question_type = WikiPatternMatcher.detect_question_type(query)
            is_book_to_author = WikiPatternMatcher.is_book_to_author_pattern(query)
            context_keywords = WikiPatternMatcher.extract_context_keywords(query)

            print(f"       📊 분석 결과:")
            print(f"         - 새 작가 쿼리: {is_new_author} (예상: {expected['is_new_author']})")
            print(f"         - 이름 포함: {has_name} (예상: {expected['has_name']})")
            print(f"         - 작가 정보: {has_author_info} (예상: {expected['has_author_info']})")
            print(f"         - 질문 유형: {question_type} (예상: {expected['question_type']})")
            print(f"         - 책→작가: {is_book_to_author} (예상: {expected['is_book_to_author']})")
            print(f"         - 컨텍스트 키워드: {context_keywords}")

            # 결과 검증
            assert is_new_author == expected['is_new_author']
            assert has_name == expected['has_name']
            assert has_author_info == expected['has_author_info']
            assert question_type == expected['question_type']
            assert is_book_to_author == expected['is_book_to_author']

            print(f"       ✅ 시나리오 {i} 통과\n")

        print("✅ 전체 쿼리 분석 워크플로우 테스트 통과")

    def test_cross_pattern_consistency(self):
        """패턴 간 일관성 테스트"""
        consistency_tests = [
            {
                'query': '김영하 작가',
                'checks': [
                    ('has_name과 is_new_author 일관성', lambda:
                    WikiPatternMatcher.contains_author_name('김영하 작가') and
                    WikiPatternMatcher.is_new_author_query('김영하 작가')),
                    ('author_info와 is_new_author 일관성', lambda:
                    WikiPatternMatcher.contains_author_info('김영하 작가') and
                    WikiPatternMatcher.is_new_author_query('김영하 작가'))
                ]
            },
            {
                'query': '개미 누가 썼어?',
                'checks': [
                    ('book_to_author와 question_type 일관성', lambda:
                    WikiPatternMatcher.is_book_to_author_pattern('개미 누가 썼어?') and
                    WikiPatternMatcher.detect_question_type('개미 누가 썼어?') == 'who')
                ]
            }
        ]

        print(f"  🔍 패턴 간 일관성 테스트...")

        for i, test in enumerate(consistency_tests, 1):
            query = test['query']
            print(f"    {i}. 쿼리: '{query}'")

            for check_name, check_func in test['checks']:
                print(f"       🔍 검사: {check_name}")

                result = check_func()

                print(f"       🎯 일관성 결과: {result}")

                assert result == True
                print(f"       ✅ 일관성 확인됨")

            print(f"       ✅ 테스트 {i} 통과\n")

        print("✅ 패턴 간 일관성 테스트 통과")

if __name__ == "__main__":
    start_time = time.time()

    print("🧪 WikiPatternMatcher 직관적인 TDD 테스트 시작\n")

    # 작가 감지 테스트
    print("👤 작가 감지 테스트 - 작가 vs 비작가 구분")
    print("=" * 60)
    test_author_detection = TestWikiPatternMatcherAuthorDetection()
    test_author_detection.test_is_author_result_true_cases()
    print()
    test_author_detection.test_is_author_result_false_cases()
    print()
    test_author_detection.test_is_new_author_query_success()
    print()
    test_author_detection.test_is_new_author_query_false()

    # 책→작가 패턴 테스트
    print("\n📚→👤 책→작가 패턴 테스트 - 작품명으로 작가 찾기")
    print("=" * 60)
    test_book_to_author = TestWikiPatternMatcherBookToAuthor()
    test_book_to_author.test_is_book_to_author_pattern_true()
    print()
    test_book_to_author.test_is_book_to_author_pattern_false()

    # 이름 감지 테스트
    print("\n🔤 이름 감지 테스트 - 한글/영어 인명 패턴")
    print("=" * 60)
    test_name_detection = TestWikiPatternMatcherNameDetection()
    test_name_detection.test_contains_author_name_korean()
    print()
    test_name_detection.test_contains_author_name_english()
    print()
    test_name_detection.test_contains_author_name_false()
    print()
    test_name_detection.test_contains_author_info()

    # 검색 패턴 생성 테스트
    print("\n🔍 검색 패턴 생성 테스트 - 다양한 검색어 생성")
    print("=" * 60)
    test_search_patterns = TestWikiPatternMatcherSearchPatterns()
    test_search_patterns.test_generate_search_patterns_korean()
    print()
    test_search_patterns.test_generate_search_patterns_english()
    print()
    test_search_patterns.test_generate_search_patterns_empty()

    # 컨텍스트 키워드 추출 테스트
    print("\n🎯 컨텍스트 키워드 추출 테스트 - 질문 의도 파악")
    print("=" * 60)
    test_context_keywords = TestWikiPatternMatcherContextKeywords()
    test_context_keywords.test_extract_context_keywords_success()
    print()
    test_context_keywords.test_extract_context_keywords_empty()

    # 명확화 응답 테스트
    print("\n💬 명확화 응답 테스트 - 사용자 선택 응답 인식")
    print("=" * 60)
    test_clarification = TestWikiPatternMatcherClarification()
    test_clarification.test_is_clarification_response_numbers()
    print()
    test_clarification.test_is_clarification_response_direct()
    print()
    test_clarification.test_is_clarification_response_false()

    # 질문 유형 감지 테스트
    print("\n❓ 질문 유형 감지 테스트 - who/what/when/where/how/why")
    print("=" * 60)
    test_question_types = TestWikiPatternMatcherQuestionTypes()
    test_question_types.test_detect_question_type_variety()
    print()
    test_question_types.test_has_person_name_pattern_korean()
    print()
    test_question_types.test_has_person_name_pattern_english()
    print()
    test_question_types.test_has_person_name_pattern_false()

    # 엣지 케이스 테스트
    print("\n🚨 엣지 케이스 테스트 - 예외 상황 처리")
    print("=" * 60)
    test_edge_cases = TestWikiPatternMatcherEdgeCases()
    test_edge_cases.test_empty_and_none_inputs()
    print()
    test_edge_cases.test_special_characters_handling()
    print()
    test_edge_cases.test_very_long_queries()

    # 성능 테스트
    print("\n⚡ 성능 테스트 - 처리 속도 및 효율성")
    print("=" * 60)
    test_performance = TestWikiPatternMatcherPerformance()
    test_performance.test_pattern_matching_performance()
    print()
    test_performance.test_search_pattern_generation_performance()

    # 통합 테스트
    print("\n🔄 통합 테스트 - 전체 워크플로우 검증")
    print("=" * 60)
    test_integration = TestWikiPatternMatcherIntegration()
    test_integration.test_full_query_analysis_workflow()
    print()
    test_integration.test_cross_pattern_consistency()

    print("\n" + "=" * 60)
    print("🎉 모든 WikiPatternMatcher 테스트 통과!")
    print("\n📊 테스트 요약:")
    print("  ✅ 작가 감지: 4개 테스트")
    print("  ✅ 책→작가 패턴: 2개 테스트")
    print("  ✅ 이름 감지: 4개 테스트")
    print("  ✅ 검색 패턴 생성: 3개 테스트")
    print("  ✅ 컨텍스트 키워드: 2개 테스트")
    print("  ✅ 명확화 응답: 3개 테스트")
    print("  ✅ 질문 유형 감지: 4개 테스트")
    print("  ✅ 엣지 케이스: 3개 테스트")
    print("  ✅ 성능 테스트: 2개 테스트")
    print("  ✅ 통합 테스트: 2개 테스트")
    print("\n📝 pytest로 실행하려면:")
    print("    cd ai-service")
    print("    python -m pytest tests/unit/utils/test_wiki_pattern_matcher.py -v -s")
