#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WikiSearchResult 직관적인 TDD 테스트
각 테스트마다 성공 메시지 출력으로 진행상황을 실시간 확인

실행 방법:
    cd ai-service
    python tests/unit/models/test_wiki_search_result.py
    또는
    python -m pytest tests/unit/models/test_wiki_search_result.py -v -s
"""

import pytest
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 테스트 대상 모델 import
from app.models.wiki_search_result import WikiSearchResult


class TestWikiSearchResultBasics:
    """WikiSearchResult 기본 기능 테스트"""

    def test_create_success_result(self):
        """성공 검색 결과 생성 테스트"""
        title = "한강 (소설가)"
        summary = "한강(韓江, 1970년 11월 27일 ~ )은 대한민국의 소설가이다."
        content = "한강은 1970년 광주광역시에서 태어났다. 연세대학교 국어국문학과를 졸업했으며..."
        url = "https://ko.wikipedia.org/wiki/한강_(소설가)"

        print(f"  📝 검색 제목: '{title}'")
        print(f"  📄 요약: '{summary[:50]}...'")
        print(f"  📚 내용 길이: {len(content)}자")
        print(f"  🔗 URL: '{url}'")

        result = WikiSearchResult.create_success(title, summary, content, url)

        print(f"  ✅ 성공 여부: {result.success}")
        print(f"  📖 저장된 제목: '{result.title}'")
        print(f"  📝 저장된 요약: '{result.summary[:30]}...'")
        print(f"  🔗 저장된 URL: '{result.url}'")

        assert result.success == True
        assert result.title == title
        assert result.summary == summary
        assert result.content == content
        assert result.url == url
        assert result.error is None
        print("✅ 성공 검색 결과 생성 테스트 통과")

    def test_create_error_result(self):
        """에러 검색 결과 생성 테스트"""
        error_message = "위키피디아에서 해당 페이지를 찾을 수 없습니다."

        print(f"  🚨 에러 메시지: '{error_message}'")
        print(f"  💥 상황: 존재하지 않는 인물 검색")

        result = WikiSearchResult.create_error(error_message)

        print(f"  ❌ 성공 여부: {result.success}")
        print(f"  🚨 에러 메시지: '{result.error}'")
        print(f"  📖 제목: {result.title} (None이어야 함)")
        print(f"  📄 요약: {result.summary} (None이어야 함)")

        assert result.success == False
        assert result.error == error_message
        assert result.title is None
        assert result.summary is None
        assert result.content is None
        assert result.url is None
        print("✅ 에러 검색 결과 생성 테스트 통과")

    def test_direct_constructor_success(self):
        """직접 생성자로 성공 결과 생성 테스트"""
        print(f"  🔧 직접 생성자로 커스텀 성공 결과 생성")

        result = WikiSearchResult(
            success=True,
            title="김소월",
            summary="김소월(金素月, 1902년 9월 7일 ~ 1934년 12월 24일)은 일제강점기의 서정시인이다.",
            content="김소월은 평안북도 정주군에서 태어났다...",
            url="https://ko.wikipedia.org/wiki/김소월"
        )

        print(f"  ✅ 성공 여부: {result.success}")
        print(f"  📖 제목: '{result.title}'")

        assert result.success == True
        assert result.title == "김소월"
        assert result.error is None
        print("✅ 직접 생성자 성공 결과 테스트 통과")

    def test_direct_constructor_error(self):
        """직접 생성자로 에러 결과 생성 테스트"""
        print(f"  🔧 직접 생성자로 에러 결과 생성")

        result = WikiSearchResult(
            success=False,
            error="네트워크 연결 실패"
        )

        print(f"  ❌ 성공 여부: {result.success}")
        print(f"  🚨 에러: '{result.error}'")

        assert result.success == False
        assert result.error == "네트워크 연결 실패"
        assert result.title is None
        print("✅ 직접 생성자 에러 결과 테스트 통과")


class TestWikiSearchResultMethods:
    """WikiSearchResult 메서드 테스트"""

    def test_is_success_method(self):
        """성공 여부 확인 메서드 테스트"""
        success_result = WikiSearchResult.create_success("제목", "요약", "내용", "URL")
        error_result = WikiSearchResult.create_error("에러")

        print(f"  ✅ 성공 결과 확인: {success_result.is_success()}")
        print(f"  ❌ 에러 결과 확인: {error_result.is_success()}")

        assert success_result.is_success() == True
        assert error_result.is_success() == False
        print("✅ 성공 여부 확인 메서드 테스트 통과")

    def test_has_content_method(self):
        """컨텐츠 존재 여부 확인 메서드 테스트"""
        # 컨텐츠가 있는 성공 결과
        content_result = WikiSearchResult.create_success("제목", "요약", "상세한 내용", "URL")

        # 컨텐츠가 없는 성공 결과
        no_content_result = WikiSearchResult(success=True, title="제목", summary="요약", content="", url="URL")

        # 에러 결과
        error_result = WikiSearchResult.create_error("에러")

        print(f"  📚 컨텐츠 있는 결과: {content_result.has_content()}")
        print(f"  📄 컨텐츠 없는 결과: {no_content_result.has_content()}")
        print(f"  ❌ 에러 결과: {error_result.has_content()}")

        assert content_result.has_content() == True
        assert no_content_result.has_content() == False
        assert error_result.has_content() == False
        print("✅ 컨텐츠 존재 여부 확인 메서드 테스트 통과")

    def test_get_content_length_method(self):
        """컨텐츠 길이 반환 메서드 테스트"""
        content = "이것은 테스트 컨텐츠입니다. 길이를 측정합니다."
        result_with_content = WikiSearchResult.create_success("제목", "요약", content, "URL")
        result_without_content = WikiSearchResult.create_error("에러")

        print(f"  📏 컨텐츠 길이: {result_with_content.get_content_length()}자")
        print(f"  📏 실제 길이: {len(content)}자 (검증용)")
        print(f"  📏 에러 결과 길이: {result_without_content.get_content_length()}자")

        assert result_with_content.get_content_length() == len(content)
        assert result_without_content.get_content_length() == 0
        print("✅ 컨텐츠 길이 반환 메서드 테스트 통과")

    def test_get_summary_length_method(self):
        """요약 길이 반환 메서드 테스트"""
        summary = "한강은 대한민국의 소설가이다."
        result_with_summary = WikiSearchResult.create_success("제목", summary, "내용", "URL")
        result_without_summary = WikiSearchResult.create_error("에러")

        print(f"  📏 요약 길이: {result_with_summary.get_summary_length()}자")
        print(f"  📏 실제 길이: {len(summary)}자 (검증용)")
        print(f"  📏 에러 결과 요약 길이: {result_without_summary.get_summary_length()}자")

        assert result_with_summary.get_summary_length() == len(summary)
        assert result_without_summary.get_summary_length() == 0
        print("✅ 요약 길이 반환 메서드 테스트 통과")


class TestWikiSearchResultSerialization:
    """WikiSearchResult 직렬화/역직렬화 테스트"""

    def test_success_result_to_dict(self):
        """성공 결과 딕셔너리 변환 테스트"""
        title = "박경리"
        summary = "박경리(朴景利, 1926년 10월 2일 ~ 2008년 5월 5일)는 대한민국의 소설가이다."
        content = "박경리는 경상남도 통영에서 태어났다..."
        url = "https://ko.wikipedia.org/wiki/박경리"

        print(f"  📝 입력 데이터:")
        print(f"    - 제목: '{title}'")
        print(f"    - 요약: '{summary[:30]}...'")
        print(f"    - URL: '{url}'")

        result = WikiSearchResult.create_success(title, summary, content, url)
        dict_data = result.to_dict()

        print(f"  🔄 직렬화 결과:")
        print(f"    - success: {dict_data['success']}")
        print(f"    - title: '{dict_data['title']}'")
        print(f"    - summary: '{dict_data['summary'][:30]}...'")
        print(f"    - url: '{dict_data['url']}'")

        assert dict_data['success'] == True
        assert dict_data['title'] == title
        assert dict_data['summary'] == summary
        assert dict_data['content'] == content
        assert dict_data['url'] == url
        assert 'error' not in dict_data  # 성공 시에는 error 필드 없음
        print("✅ 성공 결과 딕셔너리 변환 테스트 통과")

    def test_error_result_to_dict(self):
        """에러 결과 딕셔너리 변환 테스트"""
        error_message = "페이지를 찾을 수 없습니다"

        result = WikiSearchResult.create_error(error_message)
        dict_data = result.to_dict()

        print(f"  📊 에러 결과 변환:")
        print(f"    - success: {dict_data['success']}")
        print(f"    - error: '{dict_data['error']}'")

        assert dict_data['success'] == False
        assert dict_data['error'] == error_message
        # 에러 시에는 컨텐츠 관련 필드들이 포함되지 않음
        assert 'title' not in dict_data
        assert 'summary' not in dict_data
        assert 'content' not in dict_data
        assert 'url' not in dict_data
        print("✅ 에러 결과 딕셔너리 변환 테스트 통과")

    def test_success_result_from_dict(self):
        """성공 결과 딕셔너리 복원 테스트"""
        data = {
            'success': True,
            'title': '이효석',
            'summary': '이효석(李孝石, 1907년 2월 23일 ~ 1942년 5월 25일)은 일제강점기의 소설가이다.',
            'content': '이효석은 강원도 평창군에서 태어났다...',
            'url': 'https://ko.wikipedia.org/wiki/이효석'
        }

        print(f"  📥 입력 딕셔너리: {list(data.keys())}")

        result = WikiSearchResult.from_dict(data)

        print(f"  📤 복원된 객체:")
        print(f"    - success: {result.success}")
        print(f"    - title: '{result.title}'")
        print(f"    - summary: '{result.summary[:30]}...'")

        assert result.success == True
        assert result.title == '이효석'
        assert result.summary == data['summary']
        assert result.content == data['content']
        assert result.url == data['url']
        assert result.error is None
        print("✅ 성공 결과 딕셔너리 복원 테스트 통과")

    def test_error_result_from_dict(self):
        """에러 결과 딕셔너리 복원 테스트"""
        data = {
            'success': False,
            'error': 'API 호출 실패'
        }

        result = WikiSearchResult.from_dict(data)

        assert result.success == False
        assert result.error == 'API 호출 실패'
        assert result.title is None
        assert result.summary is None
        assert result.content is None
        assert result.url is None
        print("✅ 에러 결과 딕셔너리 복원 테스트 통과")


class TestWikiSearchResultRoundtrip:
    """WikiSearchResult 직렬화-역직렬화 왕복 테스트"""

    def test_success_result_roundtrip(self):
        """성공 결과 직렬화-역직렬화 왕복 테스트"""
        original = WikiSearchResult.create_success(
            "윤동주",
            "윤동주(尹東柱, 1917년 12월 30일 ~ 1945년 2월 16일)는 일제강점기의 저항문학 시인이다.",
            "윤동주는 북간도 명동촌에서 태어났다. 연희전문학교 문과를 졸업하고...",
            "https://ko.wikipedia.org/wiki/윤동주"
        )

        print(f"  📤 원본 결과:")
        print(f"    - title: '{original.title}'")
        print(f"    - summary: '{original.summary[:40]}...'")
        print(f"    - content_length: {original.get_content_length()}자")

        # 직렬화
        data = original.to_dict()
        print(f"  🔄 직렬화 완료")

        # 역직렬화
        restored = WikiSearchResult.from_dict(data)
        print(f"  📥 역직렬화 완료")

        print(f"  🔍 복원된 결과:")
        print(f"    - title: '{restored.title}'")
        print(f"    - summary: '{restored.summary[:40]}...'")
        print(f"    - content_length: {restored.get_content_length()}자")

        # 검증
        assert restored.success == original.success
        assert restored.title == original.title
        assert restored.summary == original.summary
        assert restored.content == original.content
        assert restored.url == original.url
        assert restored.error == original.error
        print("✅ 성공 결과 직렬화-역직렬화 왕복 테스트 통과")

    def test_error_result_roundtrip(self):
        """에러 결과 직렬화-역직렬화 왕복 테스트"""
        original = WikiSearchResult.create_error("위키피디아 서버 접속 실패")

        # 직렬화
        data = original.to_dict()

        # 역직렬화
        restored = WikiSearchResult.from_dict(data)

        # 검증
        assert restored.success == original.success
        assert restored.error == original.error
        assert restored.title == original.title  # None
        assert restored.summary == original.summary  # None
        assert restored.content == original.content  # None
        assert restored.url == original.url  # None
        print("✅ 에러 결과 직렬화-역직렬화 왕복 테스트 통과")


class TestWikiSearchResultEdgeCases:
    """WikiSearchResult 엣지 케이스 테스트"""

    def test_missing_fields_in_dict(self):
        """딕셔너리 필드 누락 처리 테스트"""
        minimal_data = {
            'success': True
            # title, summary, content, url 모두 누락
        }

        print(f"  📥 최소 딕셔너리: {minimal_data}")

        result = WikiSearchResult.from_dict(minimal_data)

        print(f"  📤 복원된 객체 (기본값 적용):")
        print(f"    - success: {result.success}")
        print(f"    - title: {result.title} (기본값)")
        print(f"    - summary: {result.summary} (기본값)")

        assert result.success == True
        assert result.title is None  # 기본값
        assert result.summary is None  # 기본값
        assert result.content is None  # 기본값
        assert result.url is None  # 기본값
        assert result.error is None  # 기본값
        print("✅ 딕셔너리 필드 누락 처리 테스트 통과")

    def test_empty_string_fields(self):
        """빈 문자열 필드 처리 테스트"""
        result = WikiSearchResult.create_success("", "", "", "")

        print(f"  📝 빈 문자열 필드들:")
        print(f"    - title: '{result.title}'")
        print(f"    - summary: '{result.summary}'")
        print(f"    - content: '{result.content}'")
        print(f"    - url: '{result.url}'")

        assert result.success == True
        assert result.title == ""
        assert result.summary == ""
        assert result.content == ""
        assert result.url == ""
        assert result.has_content() == False  # 빈 문자열은 컨텐츠 없음으로 처리
        assert result.get_content_length() == 0
        assert result.get_summary_length() == 0
        print("✅ 빈 문자열 필드 처리 테스트 통과")

    def test_none_fields_handling(self):
        """None 필드 처리 테스트"""
        result = WikiSearchResult(
            success=True,
            title=None,
            summary=None,
            content=None,
            url=None
        )

        print(f"  📝 None 필드들:")
        print(f"    - title: {result.title}")
        print(f"    - has_content: {result.has_content()}")
        print(f"    - content_length: {result.get_content_length()}")

        assert result.title is None
        assert result.has_content() == False
        assert result.get_content_length() == 0
        assert result.get_summary_length() == 0
        print("✅ None 필드 처리 테스트 통과")

    def test_very_long_content(self):
        """매우 긴 컨텐츠 처리 테스트"""
        long_content = "긴 컨텐츠 " * 1000  # 10,000자 정도
        long_summary = "긴 요약 " * 100      # 1,000자 정도

        result = WikiSearchResult.create_success(
            "테스트 제목",
            long_summary,
            long_content,
            "https://test.url"
        )

        print(f"  📏 긴 컨텐츠 처리:")
        print(f"    - summary_length: {result.get_summary_length():,}자")
        print(f"    - content_length: {result.get_content_length():,}자")
        print(f"    - has_content: {result.has_content()}")

        # 실제 길이를 기반으로 한 검증
        actual_summary_length = result.get_summary_length()
        actual_content_length = result.get_content_length()

        assert actual_summary_length >= 500  # 여유있게 600자 이상
        assert actual_content_length >= 4000  # 여유있게 4000자 이상
        assert result.has_content() == True
        print(f"  ✅ 매우 긴 컨텐츠 처리 테스트 통과 (요약: {actual_summary_length}자, 내용: {actual_content_length}자)")



class TestWikiSearchResultUsageScenarios:
    """WikiSearchResult 실제 사용 시나리오 테스트"""

    def test_successful_author_search_scenario(self):
        """성공적인 작가 검색 시나리오"""
        print("  📚 시나리오: 사용자가 '김유정 작가'를 검색하여 성공적으로 정보를 찾음")

        result = WikiSearchResult.create_success(
            "김유정 (소설가)",
            "김유정(金裕貞, 1908년 1월 11일 ~ 1937년 3월 29일)은 일제강점기의 소설가이다.",
            "김유정은 강원도 춘천에서 태어났다. 연희전문학교에서 영어영문학을 전공했으며, 1935년 '조선일보' 신춘문예에 단편소설 '소나기'가 당선되면서 문단에 데뷔했다. 대표작으로는 '봄봄', '동백꽃', '소나기' 등이 있다.",
            "https://ko.wikipedia.org/wiki/김유정_(소설가)"
        )

        print(f"  ✅ 검색 성공: {result.is_success()}")
        print(f"  📖 작가명: '{result.title}'")
        print(f"  📝 요약 길이: {result.get_summary_length()}자")
        print(f"  📚 컨텐츠 존재: {result.has_content()}")
        print(f"  📄 상세 정보 길이: {result.get_content_length()}자")

        assert result.is_success() == True
        assert "김유정" in result.title
        assert result.has_content() == True
        assert result.get_content_length() > 50
        assert "소설가" in result.summary
        print("✅ 성공적인 작가 검색 시나리오 테스트 통과")

    def test_page_not_found_scenario(self):
        """페이지를 찾을 수 없는 시나리오"""
        print("  🚨 시나리오: 존재하지 않는 작가명으로 검색하여 페이지를 찾을 수 없음")

        result = WikiSearchResult.create_error(
            "위키피디아에서 '홍길동작가'에 해당하는 페이지를 찾을 수 없습니다."
        )

        print(f"  ❌ 검색 실패: {not result.is_success()}")
        print(f"  🚨 에러 메시지: '{result.error}'")
        print(f"  📚 컨텐츠 존재: {result.has_content()}")

        assert result.is_success() == False
        assert "찾을 수 없습니다" in result.error
        assert result.has_content() == False
        assert result.title is None
        print("✅ 페이지를 찾을 수 없는 시나리오 테스트 통과")

    def test_network_error_scenario(self):
        """네트워크 오류 시나리오"""
        print("  🌐 시나리오: 위키피디아 API 호출 중 네트워크 오류 발생")

        result = WikiSearchResult.create_error(
            "위키피디아 서버에 연결할 수 없습니다. 네트워크 연결을 확인하고 다시 시도해주세요."
        )

        print(f"  🚨 네트워크 오류: {result.error}")
        print(f"  📊 결과 상태: success={result.success}")

        assert result.is_success() == False
        assert "네트워크" in result.error or "연결" in result.error
        print("✅ 네트워크 오류 시나리오 테스트 통과")

    def test_partial_information_scenario(self):
        """부분 정보만 있는 시나리오"""
        print("  📄 시나리오: 위키피디아에서 제목과 요약만 있고 상세 내용이 적은 경우")

        result = WikiSearchResult.create_success(
            "신인 작가",
            "최근 등단한 신인 작가입니다.",
            "상세한 정보가 아직 부족합니다.",  # 짧은 내용
            "https://ko.wikipedia.org/wiki/신인작가"
        )

        print(f"  ✅ 검색 성공: {result.is_success()}")
        print(f"  📝 요약 길이: {result.get_summary_length()}자")
        print(f"  📄 내용 길이: {result.get_content_length()}자 (짧음)")
        print(f"  📚 컨텐츠 존재: {result.has_content()}")

        assert result.is_success() == True
        assert result.has_content() == True  # 짧아도 컨텐츠는 존재
        assert result.get_content_length() < 50  # 상대적으로 짧은 내용
        print("✅ 부분 정보만 있는 시나리오 테스트 통과")

    def test_disambiguation_page_scenario(self):
        """동명이인 페이지 시나리오"""
        print("  🤔 시나리오: 동명이인이 많아서 구분이 필요한 경우")

        result = WikiSearchResult.create_success(
            "김철수 (동명이인)",
            "김철수는 다음과 같은 동명이인들이 있습니다.",
            "1. 김철수 (시인, 1920년생) - 일제강점기의 저항시인\n2. 김철수 (소설가, 1945년생) - 현대문학 작가\n3. 김철수 (수필가, 1960년생) - 에세이 전문 작가",
            "https://ko.wikipedia.org/wiki/김철수_(동명이인)"
        )

        print(f"  🔍 동명이인 페이지: '{result.title}'")
        print(f"  📝 구분 정보 길이: {result.get_content_length()}자")
        print(f"  📚 유용한 정보: {result.has_content()}")

        assert result.is_success() == True
        assert "동명이인" in result.title
        assert result.has_content() == True
        assert "김철수" in result.content
        print("✅ 동명이인 페이지 시나리오 테스트 통과")


if __name__ == "__main__":

    print("🧪 WikiSearchResult 직관적인 TDD 테스트 시작\n")

    # 기본 기능 테스트
    print("📋 기본 기능 테스트 - 검색 결과 생성 과정 확인")
    print("=" * 60)
    test_basics = TestWikiSearchResultBasics()
    test_basics.test_create_success_result()
    print()
    test_basics.test_create_error_result()
    print()
    test_basics.test_direct_constructor_success()
    print()
    test_basics.test_direct_constructor_error()

    # 메서드 테스트
    print("\n🔧 메서드 기능 테스트")
    print("=" * 60)
    test_methods = TestWikiSearchResultMethods()
    test_methods.test_is_success_method()
    test_methods.test_has_content_method()
    test_methods.test_get_content_length_method()
    test_methods.test_get_summary_length_method()

    # 직렬화/역직렬화 테스트
    print("\n📄 직렬화/역직렬화 테스트")
    print("=" * 60)
    test_serialization = TestWikiSearchResultSerialization()
    test_serialization.test_success_result_to_dict()
    test_serialization.test_error_result_to_dict()
    test_serialization.test_success_result_from_dict()
    test_serialization.test_error_result_from_dict()

    # 왕복 테스트
    print("\n🔄 왕복 테스트")
    print("=" * 60)
    test_roundtrip = TestWikiSearchResultRoundtrip()
    test_roundtrip.test_success_result_roundtrip()
    test_roundtrip.test_error_result_roundtrip()

    # 엣지 케이스 테스트
    print("\n🚨 엣지 케이스 테스트")
    print("=" * 60)
    test_edge_cases = TestWikiSearchResultEdgeCases()
    test_edge_cases.test_missing_fields_in_dict()
    test_edge_cases.test_empty_string_fields()
    test_edge_cases.test_none_fields_handling()
    test_edge_cases.test_very_long_content()

    # 실제 사용 시나리오 테스트
    print("\n🎭 실제 사용 시나리오 테스트")
    print("=" * 60)
    test_scenarios = TestWikiSearchResultUsageScenarios()
    test_scenarios.test_successful_author_search_scenario()
    test_scenarios.test_page_not_found_scenario()
    test_scenarios.test_network_error_scenario()
    test_scenarios.test_partial_information_scenario()
    test_scenarios.test_disambiguation_page_scenario()

    print("\n" + "=" * 60)
    print("🎉 모든 WikiSearchResult 테스트 통과!")
    print("\n📊 테스트 요약:")
    print("  ✅ 기본 결과 생성: 4개 테스트")
    print("  ✅ 메서드 기능: 4개 테스트")
    print("  ✅ 직렬화/역직렬화: 4개 테스트")
    print("  ✅ 왕복 테스트: 2개 테스트")
    print("  ✅ 엣지 케이스: 4개 테스트")
    print("  ✅ 실제 시나리오: 5개 테스트")
    print("\n📝 pytest로 실행하려면:")
    print("    cd ai-service")
    print("    python -m pytest tests/unit/models/test_wiki_search_result.py -v -s")

    print("\n💡 WikiSearchResult 사용 예시:")
    print("=" * 60)
    print("# 성공 결과 생성")
    print("success_result = WikiSearchResult.create_success(")
    print("    '한강 (소설가)',")
    print("    '한강은 대한민국의 소설가이다.',")
    print("    '상세한 작가 정보...',")
    print("    'https://ko.wikipedia.org/wiki/한강_(소설가)'")
    print(")")
    print("print(f'검색 성공: {success_result.is_success()}')")
    print("print(f'컨텐츠 길이: {success_result.get_content_length()}자')")
    print()
    print("# 에러 결과 생성")
    print("error_result = WikiSearchResult.create_error('페이지를 찾을 수 없습니다')")
    print("print(f'검색 실패: {not error_result.is_success()}')")
    print()
    print("# 컨텐츠 존재 확인")
    print("if success_result.has_content():")
    print("    print(f'요약: {success_result.summary}')")
    print("    print(f'상세 정보: {success_result.content[:100]}...')")
    print()
    print("# API 응답용 딕셔너리 변환")
    print("api_response = success_result.to_dict()")
    print("# {'success': True, 'title': '한강 (소설가)', ...}")
    print()
    print("# 딕셔너리에서 객체 복원")
    print("restored = WikiSearchResult.from_dict(api_response)")
    print("print(f'복원된 제목: {restored.title}')")

    print("\n🔍 WikiSearchResult vs WikiAgentResponse 차이점:")
    print("=" * 60)
    print("📚 WikiSearchResult:")
    print("  - 위키피디아 검색의 '데이터' 결과를 담음")
    print("  - title, summary, content, url 등 실제 검색된 정보")
    print("  - 성공/실패와 함께 구체적인 컨텐츠 제공")
    print("  - 검색 엔진의 Raw 데이터 표현")
    print()
    print("🤖 WikiAgentResponse:")
    print("  - AI 에이전트의 '처리' 결과를 담음")
    print("  - message, action, should_continue 등 에이전트 동작")
    print("  - 사용자와의 대화 흐름 제어")
    print("  - 에이전트의 의사결정과 다음 행동 지시")
    print()
    print("🔄 실제 사용 흐름:")
    print("  1. WikiSearchResult ← 위키피디아에서 데이터 검색")
    print("  2. AI 에이전트가 WikiSearchResult 분석")
    print("  3. WikiAgentResponse ← 사용자에게 어떻게 응답할지 결정")
    print("  4. 사용자에게 최종 응답 전달")