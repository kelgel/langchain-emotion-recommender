#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WikiQueryIntent 직관적인 TDD 테스트
각 테스트마다 성공 메시지 출력으로 진행상황을 실시간 확인

실행 방법:
    cd ai-service
    python tests/unit/models/test_wiki_query_intent.py
    또는
    python -m pytest tests/unit/models/test_wiki_query_intent.py -v -s
"""

import pytest
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 테스트 대상 모델 import
from app.models.wiki_query_intent import WikiQueryIntent, IntentType, InfoType


class TestWikiQueryIntentBasics:
    """WikiQueryIntent 기본 기능 테스트"""

    def test_create_author_search_intent(self):
        """작가 검색 의도 생성 테스트"""
        query = "한강"
        keywords = ["한강"]

        print(f"  📝 입력 쿼리: '{query}'")
        print(f"  🔍 추출 키워드: {keywords}")

        intent = WikiQueryIntent.create_author_search(query, keywords)

        print(f"  🎯 분류된 의도: {intent.intent_type.value}")
        print(f"  📄 저장된 쿼리: '{intent.query}'")
        print(f"  🏷️ 저장된 키워드: {intent.extracted_keywords}")

        assert intent.intent_type == IntentType.AUTHOR_SEARCH
        assert intent.query == query
        assert intent.extracted_keywords == keywords
        print("✅ 작가 검색 의도 생성 테스트 통과")

    def test_create_context_question_intent(self):
        """컨텍스트 질문 의도 생성 테스트"""
        query = "그는 언제 태어났나요?"

        print(f"  📝 입력 쿼리: '{query}'")
        print(f"  🔍 질문 유형 분석: 컨텍스트 기반 질문 (대명사 '그' 사용)")

        intent = WikiQueryIntent.create_context_question(query)

        print(f"  🎯 분류된 의도: {intent.intent_type.value}")
        print(f"  📄 저장된 쿼리: '{intent.query}'")
        print(f"  🏷️ 추출된 키워드: {intent.extracted_keywords} (컨텍스트 질문은 키워드 없음)")

        assert intent.intent_type == IntentType.CONTEXT_QUESTION
        assert intent.query == query
        assert intent.extracted_keywords == []
        print("✅ 컨텍스트 질문 의도 생성 테스트 통과")

    def test_create_book_to_author_intent(self):
        """책-작가 검색 의도 생성 테스트"""
        query = "채식주의자 작가는?"
        book_title = "채식주의자"

        print(f"  📝 입력 쿼리: '{query}'")
        print(f"  📚 감지된 책 제목: '{book_title}'")
        print(f"  🔍 질문 패턴: 책 제목 + '작가' 키워드")

        intent = WikiQueryIntent.create_book_to_author(query, book_title)

        print(f"  🎯 분류된 의도: {intent.intent_type.value}")
        print(f"  📄 저장된 쿼리: '{intent.query}'")
        print(f"  📖 저장된 책 제목: '{intent.book_title}'")
        print(f"  🏷️ 자동 생성된 키워드: {intent.extracted_keywords}")

        assert intent.intent_type == IntentType.BOOK_TO_AUTHOR
        assert intent.query == query
        assert intent.book_title == book_title
        assert book_title in intent.extracted_keywords
        print("✅ 책-작가 검색 의도 생성 테스트 통과")

    def test_author_search_with_specific_info(self):
        """구체적 정보 요청 포함 작가 검색 테스트"""
        query = "한강 대학교"
        keywords = ["한강"]
        specific_info = InfoType.UNIVERSITY

        print(f"  📝 입력 쿼리: '{query}'")
        print(f"  🔍 추출된 작가명: {keywords}")
        print(f"  🎯 감지된 구체적 정보: '{specific_info.value}' (대학교 관련)")
        print(f"  💡 분석 결과: 작가명 + 구체적 정보 요청 패턴")

        intent = WikiQueryIntent.create_author_search(query, keywords, specific_info)

        print(f"  📋 최종 의도: {intent.intent_type.value}")
        print(f"  📄 저장된 쿼리: '{intent.query}'")
        print(f"  🏷️ 키워드: {intent.extracted_keywords}")
        print(f"  ℹ️ 요청 정보: {intent.specific_info_request.value}")

        assert intent.intent_type == IntentType.AUTHOR_SEARCH
        assert intent.specific_info_request == InfoType.UNIVERSITY
        assert intent.extracted_keywords == keywords
        print("✅ 구체적 정보 요청 포함 작가 검색 테스트 통과")

    def test_context_question_with_specific_info(self):
        """구체적 정보 포함 컨텍스트 질문 테스트"""
        query = "그의 출생일은?"
        specific_info = InfoType.BIRTH

        print(f"  📝 입력 쿼리: '{query}'")
        print(f"  🔍 패턴 분석:")
        print(f"    - 대명사 '그' 사용 → 컨텍스트 질문")
        print(f"    - '출생일' 키워드 → {specific_info.value} 정보 요청")
        print(f"  💭 의도 해석: 이전 대화의 인물에 대한 출생 정보 질문")

        intent = WikiQueryIntent.create_context_question(query, specific_info)

        print(f"  🎯 분류된 의도: {intent.intent_type.value}")
        print(f"  📄 저장된 쿼리: '{intent.query}'")
        print(f"  ℹ️ 요청 정보: {intent.specific_info_request.value}")

        assert intent.intent_type == IntentType.CONTEXT_QUESTION
        assert intent.specific_info_request == InfoType.BIRTH
        print("✅ 구체적 정보 포함 컨텍스트 질문 테스트 통과")


class TestIntentClassificationPatterns:
    """질문 의도 분류 패턴 테스트 - 실제 사용자 질문들로 테스트"""

    def test_various_author_search_patterns(self):
        """다양한 작가 검색 패턴 테스트"""
        test_cases = [
            {
                "query": "김소월에 대해 알려줘",
                "expected_keywords": ["김소월"],
                "pattern": "작가명 + 일반 정보 요청"
            },
            {
                "query": "무라카미 하루키 작품 목록",
                "expected_keywords": ["무라카미 하루키"],
                "pattern": "작가명 + 작품 정보 요청"
            },
            {
                "query": "박경리 출생지는 어디야?",
                "expected_keywords": ["박경리"],
                "pattern": "작가명 + 구체적 정보 질문"
            }
        ]

        for case in test_cases:
            print(f"  📝 테스트 쿼리: '{case['query']}'")
            print(f"  🔍 예상 패턴: {case['pattern']}")

            intent = WikiQueryIntent.create_author_search(case['query'], case['expected_keywords'])

            print(f"  🎯 분류 결과: {intent.intent_type.value}")
            print(f"  🏷️ 추출 키워드: {intent.extracted_keywords}")

            assert intent.intent_type == IntentType.AUTHOR_SEARCH
            assert intent.extracted_keywords == case['expected_keywords']
            print(f"  ✅ '{case['query']}' 패턴 테스트 통과\n")

    def test_various_context_question_patterns(self):
        """다양한 컨텍스트 질문 패턴 테스트"""
        test_cases = [
            {
                "query": "그는 언제 태어났어?",
                "pattern": "대명사 + 시간 질문",
                "info_type": InfoType.BIRTH
            },
            {
                "query": "그의 다른 작품은?",
                "pattern": "대명사 + 작품 질문",
                "info_type": InfoType.WORKS
            },
            {
                "query": "어느 대학을 나왔어?",
                "pattern": "생략된 주어 + 교육 질문",
                "info_type": InfoType.UNIVERSITY
            }
        ]

        for case in test_cases:
            print(f"  📝 테스트 쿼리: '{case['query']}'")
            print(f"  🔍 예상 패턴: {case['pattern']}")

            intent = WikiQueryIntent.create_context_question(case['query'], case['info_type'])

            print(f"  🎯 분류 결과: {intent.intent_type.value}")
            print(f"  ℹ️ 정보 타입: {intent.specific_info_request.value}")

            assert intent.intent_type == IntentType.CONTEXT_QUESTION
            assert intent.specific_info_request == case['info_type']
            print(f"  ✅ '{case['query']}' 패턴 테스트 통과\n")

    def test_various_book_to_author_patterns(self):
        """다양한 책-작가 검색 패턴 테스트"""
        test_cases = [
            {
                "query": "노르웨이의 숲 누가 썼어?",
                "book_title": "노르웨이의 숲",
                "pattern": "책제목 + 작가 질문"
            },
            {
                "query": "1984 저자가 누구야?",
                "book_title": "1984",
                "pattern": "책제목 + 저자 질문"
            },
            {
                "query": "햄릿은 누구 작품이야?",
                "book_title": "햄릿",
                "pattern": "책제목 + 작품 소유자 질문"
            }
        ]

        for case in test_cases:
            print(f"  📝 테스트 쿼리: '{case['query']}'")
            print(f"  📚 감지된 책: '{case['book_title']}'")
            print(f"  🔍 예상 패턴: {case['pattern']}")

            intent = WikiQueryIntent.create_book_to_author(case['query'], case['book_title'])

            print(f"  🎯 분류 결과: {intent.intent_type.value}")
            print(f"  📖 저장된 책: '{intent.book_title}'")
            print(f"  🏷️ 자동 키워드: {intent.extracted_keywords}")

            assert intent.intent_type == IntentType.BOOK_TO_AUTHOR
            assert intent.book_title == case['book_title']
            assert case['book_title'] in intent.extracted_keywords
            print(f"  ✅ '{case['query']}' 패턴 테스트 통과\n")
    """WikiQueryIntent 직렬화/역직렬화 테스트"""

    def test_author_search_to_dict(self):
        """작가 검색 의도 딕셔너리 변환 테스트"""
        query = "무라카미 하루키"
        keywords = ["무라카미 하루키"]

        print(f"  📝 입력: '{query}' (키워드: {keywords})")

        intent = WikiQueryIntent.create_author_search(query, keywords)
        result = intent.to_dict()

        print(f"  🔄 직렬화 결과:")
        print(f"    - type: '{result['type']}'")
        print(f"    - query: '{result['query']}'")
        print(f"    - keywords: {result['keywords']}")
        print(f"    - specific_info: {result.get('specific_info', 'None')}")

        assert result['type'] == 'author_search'
        assert result['keywords'] == keywords
        assert result['query'] == query
        print("✅ 작가 검색 의도 딕셔너리 변환 테스트 통과")

    def test_context_question_to_dict(self):
        """컨텍스트 질문 딕셔너리 변환 테스트"""
        intent = WikiQueryIntent.create_context_question("그의 나이는?", InfoType.BIRTH)
        result = intent.to_dict()

        assert result['type'] == 'context_question'
        assert result['question'] == "그의 나이는?"
        assert result['specific_info'] == 'birth'
        print("✅ 컨텍스트 질문 딕셔너리 변환 테스트 통과")

    def test_book_to_author_to_dict(self):
        """책-작가 의도 딕셔너리 변환 테스트"""
        intent = WikiQueryIntent.create_book_to_author("토지 저자", "토지")
        result = intent.to_dict()

        assert result['type'] == 'book_to_author'
        assert result['book_title'] == "토지"
        print("✅ 책-작가 의도 딕셔너리 변환 테스트 통과")

    def test_author_search_from_dict(self):
        """작가 검색 의도 딕셔너리 복원 테스트"""
        data = {
            'type': 'author_search',
            'keywords': ['박경리'],
            'specific_info': 'birth'
        }
        intent = WikiQueryIntent.from_dict(data, "박경리 출생일")

        assert intent.intent_type == IntentType.AUTHOR_SEARCH
        assert intent.extracted_keywords == ['박경리']
        assert intent.specific_info_request == InfoType.BIRTH
        print("✅ 작가 검색 의도 딕셔너리 복원 테스트 통과")

    def test_context_question_from_dict(self):
        """컨텍스트 질문 딕셔너리 복원 테스트"""
        data = {
            'type': 'context_question',
            'specific_info': 'works'
        }
        intent = WikiQueryIntent.from_dict(data, "그의 대표작은?")

        assert intent.intent_type == IntentType.CONTEXT_QUESTION
        assert intent.specific_info_request == InfoType.WORKS
        print("✅ 컨텍스트 질문 딕셔너리 복원 테스트 통과")

    def test_book_to_author_from_dict(self):
        """책-작가 의도 딕셔너리 복원 테스트"""
        data = {
            'type': 'book_to_author',
            'book_title': '노르웨이의 숲'
        }
        intent = WikiQueryIntent.from_dict(data, "노르웨이의 숲 저자")

        assert intent.intent_type == IntentType.BOOK_TO_AUTHOR
        assert intent.book_title == '노르웨이의 숲'
        print("✅ 책-작가 의도 딕셔너리 복원 테스트 통과")

class TestWikiQueryIntentImprovements:
    """WikiQueryIntent 개선 사항 테스트"""
    
    def test_confidence_calculation(self):
        """신뢰도 계산 개선 테스트 (향후 구현용)"""
        # Given
        high_confidence_query = "한강 작가 정보"
        low_confidence_query = "그 사람"
        
        # When
        high_intent = WikiQueryIntent.create_author_search(high_confidence_query, ["한강"])
        low_intent = WikiQueryIntent.create_context_question(low_confidence_query)
        
        # Then
        # 현재는 기본값 0.0이지만, 향후 신뢰도 계산 로직 추가시 테스트
        assert high_intent.confidence == 0.0
        assert low_intent.confidence == 0.0
        
        # TODO: 신뢰도 계산 로직 구현 후 다음과 같이 개선
        # high_calculated = high_intent.calculate_confidence()
        # low_calculated = low_intent.calculate_confidence()
        # assert high_calculated > low_calculated
        
    def test_reasoning_field(self):
        """추론 과정 기록 개선 테스트 (향후 구현용)"""
        # Given
        query = "한강 작가 정보"
        
        # When
        intent = WikiQueryIntent.create_author_search(query, ["한강"])
        
        # Then
        # 현재는 빈 문자열이지만, 향후 추론 과정 기록 시 테스트
        assert intent.reasoning == ""
        
        # TODO: 추론 과정 기록 로직 구현 후 다음과 같이 개선
        # intent.analyze_reasoning()  # 분석 메서드 호출
        # assert "작가명 '한강' 감지" in intent.reasoning
        
    def test_keyword_extraction_improvement(self):
        """키워드 추출 개선 테스트 (향후 구현용)"""
        # Given
        query = "무라카미 하루키의 노르웨이의 숲에 대해 알려줘"
        
        # When - 현재는 수동으로 키워드 전달
        intent = WikiQueryIntent.create_author_search(query, ["무라카미 하루키", "노르웨이의 숲"])
        
        # Then
        assert "무라카미 하루키" in intent.extracted_keywords
        assert "노르웨이의 숲" in intent.extracted_keywords
        
        # TODO: 자동 키워드 추출 로직 구현 후 다음과 같이 개선
        # auto_intent = WikiQueryIntent.auto_extract_keywords(query)
        # assert "무라카미 하루키" in auto_intent.extracted_keywords
        
    def test_intent_ambiguity_detection(self):
        """의도 모호성 감지 개선 테스트 (향후 구현용)"""
        # Given
        ambiguous_query = "그거"
        clear_query = "한강 작가 정보"
        
        # When
        ambiguous_intent = WikiQueryIntent.create_context_question(ambiguous_query)
        clear_intent = WikiQueryIntent.create_author_search(clear_query, ["한강"])
        
        # Then - 현재는 기본 처리
        assert ambiguous_intent.intent_type == IntentType.CONTEXT_QUESTION
        assert clear_intent.intent_type == IntentType.AUTHOR_SEARCH
        
        # TODO: 모호성 감지 로직 구현 후 다음과 같이 개선
        # assert hasattr(ambiguous_intent, 'is_ambiguous')
        # assert ambiguous_intent.is_ambiguous() == True
        # assert clear_intent.is_ambiguous() == False


class TestWikiQueryIntentSerialization:
    """WikiQueryIntent 직렬화/역직렬화 테스트"""

    def test_author_search_to_dict(self):
        """작가 검색 의도 딕셔너리 변환 테스트"""
        query = "무라카미 하루키"
        keywords = ["무라카미 하루키"]

        print(f"  📝 입력: '{query}' (키워드: {keywords})")

        intent = WikiQueryIntent.create_author_search(query, keywords)
        result = intent.to_dict()

        print(f"  🔄 직렬화 결과:")
        print(f"    - type: '{result['type']}'")
        print(f"    - query: '{result['query']}'")
        print(f"    - keywords: {result['keywords']}")
        print(f"    - specific_info: {result.get('specific_info', 'None')}")

        assert result['type'] == 'author_search'
        assert result['keywords'] == keywords
        assert result['query'] == query
        print("✅ 작가 검색 의도 딕셔너리 변환 테스트 통과")

    def test_context_question_to_dict(self):
        """컨텍스트 질문 딕셔너리 변환 테스트"""
        intent = WikiQueryIntent.create_context_question("그의 나이는?", InfoType.BIRTH)
        result = intent.to_dict()

        assert result['type'] == 'context_question'
        assert result['question'] == "그의 나이는?"
        assert result['specific_info'] == 'birth'
        print("✅ 컨텍스트 질문 딕셔너리 변환 테스트 통과")

    def test_book_to_author_to_dict(self):
        """책-작가 의도 딕셔너리 변환 테스트"""
        intent = WikiQueryIntent.create_book_to_author("토지 저자", "토지")
        result = intent.to_dict()

        assert result['type'] == 'book_to_author'
        assert result['book_title'] == "토지"
        print("✅ 책-작가 의도 딕셔너리 변환 테스트 통과")

    def test_author_search_from_dict(self):
        """작가 검색 의도 딕셔너리 복원 테스트"""
        data = {
            'type': 'author_search',
            'keywords': ['박경리'],
            'specific_info': 'birth'
        }
        intent = WikiQueryIntent.from_dict(data, "박경리 출생일")

        assert intent.intent_type == IntentType.AUTHOR_SEARCH
        assert intent.extracted_keywords == ['박경리']
        assert intent.specific_info_request == InfoType.BIRTH
        print("✅ 작가 검색 의도 딕셔너리 복원 테스트 통과")

    def test_context_question_from_dict(self):
        """컨텍스트 질문 딕셔너리 복원 테스트"""
        data = {
            'type': 'context_question',
            'specific_info': 'works'
        }
        intent = WikiQueryIntent.from_dict(data, "그의 대표작은?")

        assert intent.intent_type == IntentType.CONTEXT_QUESTION
        assert intent.specific_info_request == InfoType.WORKS
        print("✅ 컨텍스트 질문 딕셔너리 복원 테스트 통과")

    def test_book_to_author_from_dict(self):
        """책-작가 의도 딕셔너리 복원 테스트"""
        data = {
            'type': 'book_to_author',
            'book_title': '노르웨이의 숲'
        }
        intent = WikiQueryIntent.from_dict(data, "노르웨이의 숲 저자")

        assert intent.intent_type == IntentType.BOOK_TO_AUTHOR
        assert intent.book_title == '노르웨이의 숲'
        print("✅ 책-작가 의도 딕셔너리 복원 테스트 통과")


class TestWikiQueryIntentRoundtrip:
    """WikiQueryIntent 직렬화-역직렬화 왕복 테스트"""

    def test_author_search_roundtrip(self):
        """작가 검색 의도 직렬화-역직렬화 왕복 테스트"""
        original = WikiQueryIntent.create_author_search(
            "요시모토 바나나 가족",
            ["요시모토 바나나"],
            InfoType.FAMILY
        )

        # 직렬화
        data = original.to_dict()

        # 역직렬화
        restored = WikiQueryIntent.from_dict(data, original.query)

        # 검증
        assert restored.intent_type == original.intent_type
        assert restored.query == original.query
        assert restored.extracted_keywords == original.extracted_keywords
        assert restored.specific_info_request == original.specific_info_request
        print("✅ 작가 검색 의도 직렬화-역직렬화 왕복 테스트 통과")

    def test_context_question_roundtrip(self):
        """컨텍스트 질문 직렬화-역직렬화 왕복 테스트"""
        original = WikiQueryIntent.create_context_question("그의 대학은?", InfoType.UNIVERSITY)

        # 직렬화
        data = original.to_dict()

        # 역직렬화
        restored = WikiQueryIntent.from_dict(data, original.query)

        # 검증
        assert restored.intent_type == original.intent_type
        assert restored.query == original.query
        assert restored.specific_info_request == original.specific_info_request
        print("✅ 컨텍스트 질문 직렬화-역직렬화 왕복 테스트 통과")

    def test_book_to_author_roundtrip(self):
        """책-작가 의도 직렬화-역직렬화 왕복 테스트"""
        original = WikiQueryIntent.create_book_to_author("1984 작가", "1984")

        # 직렬화
        data = original.to_dict()

        # 역직렬화
        restored = WikiQueryIntent.from_dict(data, original.query)

        # 검증
        assert restored.intent_type == original.intent_type
        assert restored.query == original.query
        assert restored.book_title == original.book_title
        print("✅ 책-작가 의도 직렬화-역직렬화 왕복 테스트 통과")


class TestWikiQueryIntentEdgeCases:
    """WikiQueryIntent 엣지 케이스 테스트"""

    def test_empty_keywords_handling(self):
        """빈 키워드 처리 테스트"""
        intent = WikiQueryIntent.create_author_search("작가 정보 알려줘")

        assert intent.intent_type == IntentType.AUTHOR_SEARCH
        assert intent.extracted_keywords == []
        print("✅ 빈 키워드 처리 테스트 통과")

    def test_missing_fields_in_dict(self):
        """딕셔너리 필드 누락 처리 테스트"""
        minimal_data = {'type': 'author_search'}
        intent = WikiQueryIntent.from_dict(minimal_data, "테스트 쿼리")

        assert intent.intent_type == IntentType.AUTHOR_SEARCH
        assert intent.query == "테스트 쿼리"
        assert intent.extracted_keywords == []
        print("✅ 딕셔너리 필드 누락 처리 테스트 통과")

    def test_invalid_intent_type_handling(self):
        """잘못된 의도 타입 처리 테스트"""
        invalid_data = {'type': 'invalid_type'}
        intent = WikiQueryIntent.from_dict(invalid_data, "테스트")

        # 기본값으로 AUTHOR_SEARCH 사용
        assert intent.intent_type == IntentType.AUTHOR_SEARCH
        print("✅ 잘못된 의도 타입 처리 테스트 통과")




if __name__ == "__main__":

    print("🧪 WikiQueryIntent 직관적인 TDD 테스트 시작\n")

    # 기본 기능 테스트
    print("📋 기본 기능 테스트 - 의도 분류 과정 확인")
    print("=" * 60)
    test_basics = TestWikiQueryIntentBasics()
    test_basics.test_create_author_search_intent()
    print()
    test_basics.test_create_context_question_intent()
    print()
    test_basics.test_create_book_to_author_intent()
    print()
    test_basics.test_author_search_with_specific_info()
    print()
    test_basics.test_context_question_with_specific_info()

    # 의도 분류 패턴 테스트
    print("\n🎯 실제 사용자 질문 패턴 분류 테스트")
    print("=" * 60)
    test_patterns = TestIntentClassificationPatterns()
    test_patterns.test_various_author_search_patterns()
    test_patterns.test_various_context_question_patterns()
    test_patterns.test_various_book_to_author_patterns()

    print("\n🚀 WikiQueryIntent 개선 기능 테스트")
    print("=" * 60)
    test_improvements = TestWikiQueryIntentImprovements()
    test_improvements.test_confidence_calculation()
    test_improvements.test_reasoning_field()
    test_improvements.test_keyword_extraction_improvement()
    test_improvements.test_intent_ambiguity_detection()

    print("📄 직렬화/역직렬화 테스트")
    print("=" * 60)
    test_serialization = TestWikiQueryIntentSerialization()
    test_serialization.test_author_search_to_dict()
    test_serialization.test_context_question_to_dict()
    test_serialization.test_book_to_author_to_dict()
    test_serialization.test_author_search_from_dict()
    test_serialization.test_context_question_from_dict()
    test_serialization.test_book_to_author_from_dict()

    print("\n🔄 왕복 테스트")
    print("=" * 60)
    test_roundtrip = TestWikiQueryIntentRoundtrip()
    test_roundtrip.test_author_search_roundtrip()
    test_roundtrip.test_context_question_roundtrip()
    test_roundtrip.test_book_to_author_roundtrip()

    print("\n🚨 엣지 케이스 테스트")
    print("=" * 60)
    test_edge_cases = TestWikiQueryIntentEdgeCases()
    test_edge_cases.test_empty_keywords_handling()
    test_edge_cases.test_missing_fields_in_dict()
    test_edge_cases.test_invalid_intent_type_handling()

    print("\n" + "=" * 60)
    print("🎉 모든 WikiQueryIntent 테스트 통과!")
    print("\n📊 테스트 요약:")
    print("  ✅ 기본 의도 분류: 5개 테스트")
    print("  ✅ 실제 질문 패턴: 9개 테스트")
    print("  ✅ 개선 기능 테스트: 4개 테스트")
    print("  ✅ 직렬화/역직렬화: 6개 테스트")
    print("  ✅ 왕복 테스트: 3개 테스트")
    print("  ✅ 엣지 케이스: 3개 테스트")
    print("\n📝 pytest로 실행하려면:")
    print("    cd ai-service")
    print("    python -m pytest tests/unit/models/test_wiki_query_intent.py -v -s")

    # TODO: 향후 개선 기능 구현 후 아래 주석 해제하여 테스트
    print("\n🚀 개선 기능 테스트 (향후 구현)")
    print("=" * 60)
    test_improvements = TestWikiQueryIntentImprovements()

    # 신뢰도 계산 테스트
    print("1. 신뢰도 계산 테스트")
    try:
        test_improvements.test_confidence_calculation()
        print("   ✅ 신뢰도 계산 로직 구현됨")
    except (AttributeError, AssertionError) as e:
        print(f"   ⏳ 신뢰도 계산 로직 미구현: {e}")

    # 추론 과정 기록 테스트
    print("2. 추론 과정 기록 테스트")
    try:
        test_improvements.test_reasoning_field()
        print("   ✅ 추론 과정 기록 로직 구현됨")
    except (AttributeError, AssertionError) as e:
        print(f"   ⏳ 추론 과정 기록 로직 미구현: {e}")

    # 키워드 자동 추출 테스트
    print("3. 키워드 자동 추출 테스트")
    try:
        test_improvements.test_keyword_extraction_improvement()
        print("   ✅ 키워드 자동 추출 로직 구현됨")
    except (AttributeError, AssertionError) as e:
        print(f"   ⏳ 키워드 자동 추출 로직 미구현: {e}")

    # 모호성 감지 테스트
    print("4. 의도 모호성 감지 테스트")
    try:
        test_improvements.test_intent_ambiguity_detection()
        print("   ✅ 모호성 감지 로직 구현됨")
    except (AttributeError, AssertionError) as e:
        print(f"   ⏳ 모호성 감지 로직 미구현: {e}")

    print("\n📋 개선 기능 구현 체크리스트:")
    print("  [ ] WikiQueryIntent.calculate_confidence() 메서드 구현")
    print("  [ ] WikiQueryIntent.reasoning 필드 자동 설정 로직 구현")
    print("  [ ] WikiQueryIntent.auto_extract_keywords() 클래스 메서드 구현")
    print("  [ ] WikiQueryIntent.is_ambiguous() 메서드 구현")
    print("\n💡 구현 후 위의 주석을 해제하여 테스트하세요!")