"""
WikiQueryIntent 모델 테스트
사용자 쿼리 의도 분석 모델의 모든 기능을 검증

실행 방법:
    python -m pytest tests/unit/models/test_wiki_query_intent.py -v
"""

import pytest
from typing import List, Optional

# 테스트 대상 모델 import
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app'))

from app.models.wiki_query_intent import WikiQueryIntent, IntentType, InfoType


class TestWikiQueryIntent:
    """WikiQueryIntent 모델 기본 기능 테스트"""

    def test_create_author_search_basic(self):
        """기본 작가 검색 의도 생성 테스트"""
        # Given
        query = "한강 작가 정보"
        keywords = ["한강"]

        # When
        intent = WikiQueryIntent.create_author_search(query, keywords)

        # Then
        assert intent.intent_type == IntentType.AUTHOR_SEARCH
        assert intent.query == query
        assert intent.extracted_keywords == keywords
        assert intent.specific_info_request is None
        assert intent.book_title is None
        assert intent.confidence == 0.0
        assert intent.reasoning == ""

    def test_create_author_search_width_specific_info(self):
        """구체적 정보 요청이 포함된 작가 검색 의도 생성 테스트"""
        # Given
        query = "한강 작가 대학교"
        keywords = ["한강"]
        specific_info = InfoType.UNIVERSITY

        # When
        intent = WikiQueryIntent.create_author_search(query, keywords, specific_info)

        # Then
        assert intent.intent_type == IntentType.AUTHOR_SEARCH
        assert intent.query == query
        assert intent.extracted_keywords == keywords
        assert intent.specific_info_request == InfoType.UNIVERSITY

    def test_create_author_search_empty_keywords(self):
        """키워드가 없는 작가 검색 의도 생성 테스트"""
        # Given
        query = "작가 정보 알려줘"

        # When
        intent = WikiQueryIntent.create_author_search(query)

        # Then
        assert intent.intent_type == IntentType.AUTHOR_SEARCH
        assert intent.query == query
        assert intent.extracted_keywords == []

    def test_create_book_to_author(self):
        """책-작가 검색 의도 생성 테스트"""
        # Given
        query = "채식주의자는 누가 썼어?"
        book_title = "채식주의자"

        # When
        intent = WikiQueryIntent.create_book_to_author(query, book_title)

        # Then
        assert intent.intent_type == IntentType.BOOK_TO_AUTHOR
        assert intent.query == query
        assert intent.book_title == book_title
        assert book_title in intent.extracted_keywords
        assert intent.specific_info_request is None

    def test_create_context_question_basic(self):
        """기본 컨텍스트 질문 의도 생성 테스트"""
        # Given
        query = "그는 언제 태어났어?"

        # When
        intent = WikiQueryIntent.create_context_question(query)

        # Then
        assert intent.intent_type == IntentType.CONTEXT_QUESTION
        assert intent.query == query
        assert intent.specific_info_request is None
        assert intent.extracted_keywords == []

    def test_create_context_question_with_specific_info(self):
        """구체적 정보가 포함된 컨텍스트 질문 의도 생성 테스트"""
        # Given
        query = "그의 나이는?"
        specific_info = InfoType.BIRTH

        # When
        intent = WikiQueryIntent.create_context_question(query, specific_info)

        # Then
        assert intent.intent_type == IntentType.CONTEXT_QUESTION
        assert intent.query == query
        assert intent.specific_info_request == InfoType.BIRTH

    def test_to_dict_author_search_with_specific_info(self):
        """구체적 정보가 포함된 작가 검색 의도의 딕셔너리 변환 테스트"""
        # Given
        intent = WikiQueryIntent.create_author_search(
            "무라카미 하루키 대학교",
            ["무라카미 하루키"],
            InfoType.UNIVERSITY
        )

        # When
        result_dict = intent.to_dict()

        # Then
        assert result_dict['type'] == 'author_search'
        assert result_dict['specific_info'] == 'university'
        assert result_dict['keywords'] == ["무라카미 하루키"]

    def test_to_dict_book_to_author(self):
        """책-작가 의도의 딕셔너리 변환 테스트"""
        # Given
        intent = WikiQueryIntent.create_book_to_author("토지 저자", "토지")

        # When
        result_dict = intent.to_dict()

        # Then
        assert result_dict['type'] == 'book_to_author'
        assert result_dict['book_title'] == "토지"

    def test_to_dict_context_question(self):
        """컨텍스트 질문 의도의 딕셔너리 변환 테스트"""
        # Given
        intent = WikiQueryIntent.create_context_question("그의 출생일은?", InfoType.BIRTH)

        # When
        result_dict = intent.to_dict()

        # Then
        assert result_dict['type'] == 'context_question'
        assert result_dict['question'] == "그의 출생일은?"
        assert result_dict['specific_info'] == 'birth'

    def test_from_dict_author_search(self):
        """작가 검색 의도의 딕셔너리 복원 테스트"""
        # Given
        data = {
            'type': 'author_search',
            'keywords': ['박경리'],
            'specific_info': 'birth'
        }
        original_query = "박경리 출생일"

        # When
        intent = WikiQueryIntent.from_dict(data, original_query)

        # Then
        assert intent.intent_type == IntentType.AUTHOR_SEARCH
        assert intent.query == original_query
        assert intent.extracted_keywords == ['박경리']
        assert intent.specific_info_request == InfoType.BIRTH

    def test_from_dict_book_to_author(self):
        """책-작가 의도의 딕셔너리 복원 테스트"""
        # Given
        data = {
            'type': 'book_to_author',
            'book_title': '노르웨이의 숲'
        }
        original_query = "노르웨이의 숲 저자"

        # When
        intent = WikiQueryIntent.from_dict(data, original_query)

        # Then
        assert intent.intent_type == IntentType.BOOK_TO_AUTHOR
        assert intent.query == original_query
        assert intent.book_title == '노르웨이의 숲'

    def test_from_dict_context_question(self):
        """컨텍스트 질문 의도의 딕셔너리 복원 테스트"""
        # Given
        data = {
            'type': 'context_question',
            'specific_info': 'works'
        }
        original_query = "그의 대표작은?"

        # When
        intent = WikiQueryIntent.from_dict(data, original_query)

        # Then
        assert intent.intent_type == IntentType.CONTEXT_QUESTION
        assert intent.query == original_query
        assert intent.specific_info_request == InfoType.WORKS

    def test_serialization_roundtrip(self):
        """직렬화-역직렬화 왕복 테스트"""
        # Given
        original_intent = WikiQueryIntent.create_author_search(
            "요시모토 바나나 가족",
            ["요시모토 바나나"],
            InfoType.FAMILY
        )

        # When
        dict_data = original_intent.to_dict()
        restored_intent = WikiQueryIntent.from_dict(dict_data, original_intent.query)

        # Then
        assert restored_intent.intent_type == original_intent.intent_type
        assert restored_intent.query == original_intent.query
        assert restored_intent.extracted_keywords == original_intent.extracted_keywords
        assert restored_intent.specific_info_request == original_intent.specific_info_request


class TestWikiQueryIntentSerialization:
    """WikiQueryIntent 직렬화/역직렬화 테스트"""

    def test_to_dict_author_search(self):
        """작가 검색 의도의 딕셔너리 변환 테스트"""
        # Given
        intent = WikiQueryIntent.create_author_search("김영하", ["김영하"])

        # When
        result_dict = intent.to_dict()

        # Then
        assert result_dict['type'] == 'author_search'
        assert result_dict['query'] == "김영하"
        assert result_dict['keywords'] == ["김영하"]
        assert result_dict['specific_info'] is None

if __name__ == "__main__":
    # 직접 실행시 간단한 스모크 테스트
    print("🧪 WikiQueryIntent 모델 테스트 시작")

    try:
        # 기본 기능 테스트
        intent = WikiQueryIntent.create_author_search("한강", ["한강"])
        assert intent.intent_type == IntentType.AUTHOR_SEARCH
        print("✅ 작가 검색 의도 생성 성공")

        # 직렬화 테스트
        dict_data = intent.to_dict()
        restored = WikiQueryIntent.from_dict(dict_data, intent.query)
        assert restored.intent_type == intent.intent_type
        print("✅ 직렬화/역직렬화 성공")
        #
        # # 모든 의도 타입 테스트
        # book_intent = WikiQueryIntent.create_book_to_author("책", "책")
        # context_intent = WikiQueryIntent.create_context_question("질문")
        # assert book_intent.intent_type == IntentType.BOOK_TO_AUTHOR
        # assert context_intent.intent_type == IntentType.CONTEXT_QUESTION
        # print("✅ 모든 의도 타입 생성 성공")
        #
        # print("\n🎉 WikiQueryIntent 기본 기능 테스트 통과!")
        # print("\n📝 전체 테스트 실행 명령어:")
        # print("    pytest tests/test_wiki_query_intent.py -v")
        # print("    pytest tests/test_wiki_query_intent.py::TestWikiQueryIntent -v")
        # print("    pytest tests/test_wiki_query_intent.py::TestWikiQueryIntentImprovements -v")

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()