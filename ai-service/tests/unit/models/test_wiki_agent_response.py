"""
WikiQueryIntent 간단한 TDD 테스트
🔴 Red → 🟢 Green → 🔵 Refactor

실행 방법:
    cd ai-service
    python -m pytest tests/unit/models/test_wiki_query_intent_tdd.py -v
"""

import pytest
import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.models.wiki_query_intent import WikiQueryIntent, IntentType, InfoType


class TestWikiQueryIntentTDD:
    """WikiQueryIntent TDD 테스트 - 간단하고 집중적으로"""

    def test_should_create_author_search_intent(self):
        """🔴 작가 검색 의도를 생성할 수 있어야 한다"""
        intent = WikiQueryIntent.create_author_search("한강")
        assert intent.intent_type == IntentType.AUTHOR_SEARCH

    def test_should_store_query_text(self):
        """🔴 쿼리 텍스트를 저장해야 한다"""
        intent = WikiQueryIntent.create_author_search("한강 작가")
        assert intent.query == "한강 작가"

    def test_should_store_keywords(self):
        """🔴 키워드를 저장해야 한다"""
        intent = WikiQueryIntent.create_author_search("한강", ["한강"])
        assert intent.extracted_keywords == ["한강"]

    def test_should_create_context_question(self):
        """🔴 컨텍스트 질문을 생성할 수 있어야 한다"""
        intent = WikiQueryIntent.create_context_question("그는 언제 태어났나요?")
        assert intent.intent_type == IntentType.CONTEXT_QUESTION

    def test_should_create_book_to_author(self):
        """🔴 책-작가 의도를 생성할 수 있어야 한다"""
        intent = WikiQueryIntent.create_book_to_author("채식주의자 작가는?", "채식주의자")
        assert intent.intent_type == IntentType.BOOK_TO_AUTHOR
        assert intent.book_title == "채식주의자"

    def test_should_convert_to_dict(self):
        """🔴 딕셔너리로 변환할 수 있어야 한다"""
        intent = WikiQueryIntent.create_author_search("한강", ["한강"])
        result = intent.to_dict()

        assert result['type'] == 'author_search'
        assert result['keywords'] == ["한강"]

    def test_should_restore_from_dict(self):
        """🔴 딕셔너리에서 객체를 복원할 수 있어야 한다"""
        data = {'type': 'author_search', 'keywords': ['한강']}
        intent = WikiQueryIntent.from_dict(data, "한강 작가")

        assert intent.intent_type == IntentType.AUTHOR_SEARCH
        assert intent.extracted_keywords == ['한강']

    def test_should_handle_specific_info_request(self):
        """🔴 구체적 정보 요청을 처리할 수 있어야 한다"""
        intent = WikiQueryIntent.create_author_search(
            "한강 대학교",
            ["한강"],
            InfoType.UNIVERSITY
        )
        assert intent.specific_info_request == InfoType.UNIVERSITY

    def test_serialization_roundtrip_should_work(self):
        """🔴 직렬화-역직렬화 왕복이 작동해야 한다"""
        original = WikiQueryIntent.create_author_search("무라카미", ["무라카미"])

        # 직렬화
        data = original.to_dict()

        # 역직렬화
        restored = WikiQueryIntent.from_dict(data, original.query)

        # 검증
        assert restored.intent_type == original.intent_type
        assert restored.query == original.query
        assert restored.extracted_keywords == original.extracted_keywords


if __name__ == "__main__":
    print("🧪 WikiQueryIntent 간단한 TDD 테스트 시작")

    # 기본 스모크 테스트
    try:
        intent = WikiQueryIntent.create_author_search("테스트")
        assert intent.intent_type == IntentType.AUTHOR_SEARCH
        print("✅ 기본 기능 동작 확인")

        # 직렬화 테스트
        data = intent.to_dict()
        restored = WikiQueryIntent.from_dict(data, intent.query)
        assert restored.intent_type == intent.intent_type
        print("✅ 직렬화/역직렬화 동작 확인")

        print("\n🎉 모든 기본 기능 정상 작동!")
        print("📝 전체 테스트 실행: python -m pytest tests/unit/models/test_wiki_query_intent_tdd.py -v")

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")