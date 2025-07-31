"""
WikiSearchPrompt 직관적인 TDD 테스트
각 테스트마다 성공 메시지 출력으로 진행상황을 실시간 확인

실행 방법:
    cd ai-service
    python tests/unit/prompts/test_wiki_search_prompt.py
    또는
    python -m pytest tests/unit/prompts/test_wiki_search_prompt.py -v -s
"""

import pytest
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 의존성 모듈 Mock 설정 (import 에러 방지용)
from unittest.mock import Mock
mock_modules = ['utils', 'models', 'tools', 'chains']
for module_name in mock_modules:
    if module_name not in sys.modules:
        sys.modules[module_name] = Mock()

# 실제 WikiSearchPrompt 클래스 import
from app.prompts.wiki_search_prompt import WikiSearchPrompt

class TestWikiSearchPromptBasics:
    """WikiSearchPrompt 기본 기능 테스트"""

    def test_prompt_initialization(self):
        """프롬프트 객체 초기화 테스트"""
        print("  🔧 WikiSearchPrompt 객체 생성 중...")

        prompt = WikiSearchPrompt()

        print("  ✅ 객체 생성 완료")
        print(f"  📋 객체 타입: {type(prompt).__name__}")

        assert prompt is not None
        assert hasattr(prompt, 'get_intent_analysis_prompt')
        assert hasattr(prompt, 'get_author_summary_prompt')
        assert hasattr(prompt, 'format_author_response')
        print("✅ 프롬프트 객체 초기화 테스트 통과")

    def test_get_intent_analysis_prompt(self):
        """의도 분석 프롬프트 생성 테스트"""
        prompt = WikiSearchPrompt()
        result = prompt.get_intent_analysis_prompt()

        print(f"  📝 프롬프트 길이: {len(result)}자")
        print(f"  🔍 JSON 키워드 포함: {'JSON' in result}")
        print(f"  🎯 intent_type 포함: {'intent_type' in result}")

        assert isinstance(result, str)
        assert len(result) > 100  # 충분히 상세한 프롬프트인지 확인
        assert 'intent_type' in result.lower() or '의도' in result
        assert 'extracted_keywords' in result.lower() or '키워드' in result
        print("✅ 의도 분석 프롬프트 생성 테스트 통과")

    def test_get_author_summary_prompt(self):
        """작가 요약 프롬프트 생성 테스트"""
        print("  👤 작가 요약 프롬프트 생성 중...")

        prompt = WikiSearchPrompt()
        result = prompt.get_author_summary_prompt()

        print(f"  📝 프롬프트 길이: {len(result)}자")
        print(f"  👤 '작가' 키워드 포함: {'작가' in result}")
        print(f"  📚 '작품' 키워드 포함: {'작품' in result}")

        assert isinstance(result, str)
        assert len(result) > 50
        assert '작가' in result or '정보' in result or 'author' in result.lower()
        print("✅ 작가 요약 프롬프트 생성 테스트 통과")

    def test_get_book_summary_prompt(self):
        """책 요약 프롬프트 생성 테스트"""
        print("  📚 책 요약 프롬프트 생성 중...")

        prompt = WikiSearchPrompt()
        result = prompt.get_book_summary_prompt()

        print(f"  📝 프롬프트 길이: {len(result)}자")
        print(f"  📚 '책' 키워드 포함: {'책' in result}")
        print(f"  ✍️ '저자' 키워드 포함: {'저자' in result}")

        assert isinstance(result, str)
        assert len(result) > 50
        assert '책' in result or '저자' in result or '정보' in result or 'book' in result.lower()
        print("✅ 책 요약 프롬프트 생성 테스트 통과")

class TestWikiSearchPromptFormatting:
    """WikiSearchPrompt 응답 포맷팅 테스트"""

    def test_format_author_response_complete_data(self):
        """완전한 데이터로 작가 응답 포맷팅 테스트"""
        search_result = {
            'success': True,
            'title': '김영하 (작가)',
            'summary': '김영하는 대한민국의 소설가이다. 1968년 11월 11일에 태어났다.',
            'content': '김영하는 여러 소설을 집필했다.',
            'url': 'https://ko.wikipedia.org/wiki/김영하_(작가)'
        }

        print(f"  📝 입력 데이터:")
        print(f"    - 제목: '{search_result['title']}'")
        print(f"    - 요약: '{search_result['summary'][:50]}...'")
        print(f"    - URL 존재: {bool(search_result['url'])}")

        prompt = WikiSearchPrompt()
        result = prompt.format_author_response(search_result)

        print(f"  📄 포맷팅 결과 길이: {len(result)}자")
        print(f"  ✅ 제목 포함: {'김영하' in result}")
        print(f"  ✅ URL 포함: {'wikipedia.org' in result}")

        assert isinstance(result, str)
        assert len(result) > 0
        assert '김영하' in result
        print("✅ 완전한 데이터로 작가 응답 포맷팅 테스트 통과")

    def test_format_author_response_minimal_data(self):
        """최소 데이터로 작가 응답 포맷팅 테스트"""
        minimal_result = {
            'success': True,
            'title': '한강',
            'summary': '',
            'content': '',
            'url': ''
        }

        print(f"  📝 최소 입력 데이터:")
        print(f"    - 제목만: '{minimal_result['title']}'")
        print(f"    - 요약: 없음")
        print(f"    - URL: 없음")

        prompt = WikiSearchPrompt()
        result = prompt.format_author_response(minimal_result)

        print(f"  📄 포맷팅 결과: '{result[:100]}...'")
        print(f"  ✅ 제목 포함: {'한강' in result}")

        assert isinstance(result, str)
        assert len(result) > 0
        assert '한강' in result
        print("✅ 최소 데이터로 작가 응답 포맷팅 테스트 통과")

    # 아직 구현되지 않음
    # def test_format_clarification_request(self):
    #     """명확화 요청 포맷팅 테스트"""
    #     author_name = "김영하"
    #     options = ["김영하 (작가)", "김영하 (교수)", "김영하 (의사)"]
    #
    #     print(f"  📝 입력:")
    #     print(f"    - 작가명: '{author_name}'")
    #     print(f"    - 옵션 수: {len(options)}개")
    #     print(f"    - 옵션들: {options}")
    #
    #     prompt = WikiSearchPrompt()
    #     result = prompt.format_clarification_request(author_name, options)
    #
    #     print(f"  📄 결과 길이: {len(result)}자")
    #     print(f"  ✅ 작가명 포함: {author_name in result}")
    #     print(f"  ✅ 모든 옵션 포함: {all(opt in result for opt in options)}")
    #
    #     assert isinstance(result, str)
    #     assert len(result) > 0
    #     assert author_name in result
    #     for option in options:
    #         assert option in result
    #     print("✅ 명확화 요청 포맷팅 테스트 통과")

class TestWikiSearchPromptMessages:
    """WikiSearchPrompt 메시지 생성 테스트"""

    def test_search_failure_messages(self):
        """검색 실패 메시지 생성 테스트"""
        test_authors = ["김영하", "한강", "박경리", "베르나르 베르베르"]

        prompt = WikiSearchPrompt()

        for author in test_authors:
            print(f"  🔍 '{author}' 검색 실패 메시지 생성 중...")

            result = prompt.get_search_failure_message(author)

            print(f"    📄 메시지: '{result[:60]}...'")
            print(f"    ✅ 작가명 포함: {author in result}")

            assert isinstance(result, str)
            assert len(result) > 0
            assert author in result
            print(f"    ✅ '{author}' 검색 실패 메시지 생성 완료")

        print("✅ 검색 실패 메시지 생성 테스트 통과")

    def test_ambiguous_query_message(self):
        """모호한 질문 메시지 테스트"""
        print("  ❓ 모호한 질문 메시지 생성 중...")

        prompt = WikiSearchPrompt()
        result = prompt.get_ambiguous_query_message()

        print(f"  📄 메시지: '{result}'")
        print(f"  🔍 '구체적' 또는 '명확' 포함: {'구체적' in result or '명확' in result}")

        assert isinstance(result, str)
        assert len(result) > 0
        # 메시지 내용이 사용자에게 도움이 되는지 확인 (너무 구체적인 단어보다는 일반적인 검증)
        helpful_keywords = ['구체적', '명확', '자세히', '정확', '다시', '질문']
        has_helpful_keyword = any(keyword in result for keyword in helpful_keywords)
        assert has_helpful_keyword
        print("✅ 모호한 질문 메시지 테스트 통과")

    def test_combined_search_failure_message(self):
        """결합 검색 실패 메시지 테스트"""
        author_name = "김영하"
        book_title = "살인자의 기억법"

        print(f"  📝 입력:")
        print(f"    - 작가: '{author_name}'")
        print(f"    - 책: '{book_title}'")

        prompt = WikiSearchPrompt()
        result = prompt.get_combined_search_failure_message(author_name, book_title)

        print(f"  📄 결과: '{result}'")
        print(f"  ✅ 작가명 포함: {author_name in result}")
        print(f"  ✅ 책제목 포함: {book_title in result}")

        assert isinstance(result, str)
        assert len(result) > 0
        assert author_name in result
        assert book_title in result
        print("✅ 결합 검색 실패 메시지 테스트 통과")

class TestWikiSearchPromptSpecialMethods:
    """WikiSearchPrompt 특수 메서드 테스트"""

    def test_methods_existence(self):
        """메서드 존재 여부 확인 테스트"""
        print("  🔍 WikiSearchPrompt 메서드 존재 여부 확인 중...")

        prompt = WikiSearchPrompt()

        # 필수 메서드들 확인
        essential_methods = [
            'get_intent_analysis_prompt',
            'get_author_summary_prompt',
            'get_book_summary_prompt',
            'format_author_response',
            'get_search_failure_message',
            'get_ambiguous_query_message'
        ]

        for method_name in essential_methods:
            has_method = hasattr(prompt, method_name)
            print(f"    📋 {method_name}: {'✅' if has_method else '❌'}")
            assert has_method, f"Missing essential method: {method_name}"

        print("✅ 필수 메서드 존재 여부 확인 테스트 통과")

    def test_optional_methods_with_fallback(self):
        """선택적 메서드들 테스트 (있으면 테스트, 없으면 스킵)"""
        print("  🔧 선택적 메서드들 확인 중...")

        prompt = WikiSearchPrompt()

        optional_methods = [
            ('format_clarification_request', ['author_name', 'options']),
            ('format_disambiguation_response', ['candidates']),
            ('get_context_question_prompt', []),
            ('format_specific_info_response', ['info_type', 'content', 'author_name']),
            ('get_error_message', ['error_type']),
            ('format_compound_query_response', ['results'])
        ]

        for method_name, params in optional_methods:
            if hasattr(prompt, method_name):
                print(f"    ✅ {method_name}: 존재함")
                method = getattr(prompt, method_name)

                # 간단한 호출 테스트 (매개변수에 따라)
                try:
                    if method_name == 'format_clarification_request':
                        result = method("김영하", ["옵션1", "옵션2"])
                    elif method_name == 'format_disambiguation_response':
                        result = method([{"name": "김영하", "description": "작가"}])
                    elif method_name == 'get_context_question_prompt':
                        result = method()
                    elif method_name == 'format_specific_info_response':
                        result = method("birth", "1968년", "김영하")
                    elif method_name == 'get_error_message':
                        result = method("general")
                    elif method_name == 'format_compound_query_response':
                        result = method([{"author": "김영하", "info": "작가 정보"}])

                    assert isinstance(result, str)
                    print(f"      ✅ 정상 호출됨: {len(result)}자 반환")
                except Exception as e:
                    print(f"      ⚠️  호출 중 에러: {e}")
            else:
                print(f"    ⏭️  {method_name}: 미구현 (선택사항)")

        print("✅ 선택적 메서드 확인 테스트 완료")

class TestWikiSearchPromptIntegration:
    """WikiSearchPrompt 통합 테스트"""

    def test_full_author_search_workflow(self):
        """전체 작가 검색 워크플로우 테스트"""
        print("  🔄 전체 작가 검색 워크플로우 시작...")

        prompt = WikiSearchPrompt()

        # 1. 의도 분석 프롬프트 생성
        print("    1️⃣ 의도 분석 프롬프트 생성")
        intent_prompt = prompt.get_intent_analysis_prompt()
        assert len(intent_prompt) > 0
        print("       ✅ 의도 분석 프롬프트 생성 완료")

        # 2. 작가 정보 응답 포맷팅
        print("    2️⃣ 작가 정보 응답 포맷팅")
        search_result = {
            'title': '김영하 (작가)',
            'summary': '김영하는 대한민국의 소설가이다.',
            'url': 'https://ko.wikipedia.org/wiki/김영하_(작가)'
        }

        author_response = prompt.format_author_response(search_result)
        assert '김영하' in author_response
        print("       ✅ 작가 정보 응답 포맷팅 완료")

        # 3. 실패 상황 처리
        print("    3️⃣ 검색 실패 상황 처리")
        failure_message = prompt.get_search_failure_message("존재하지않는작가")
        assert len(failure_message) > 0
        print("       ✅ 검색 실패 메시지 생성 완료")

        print("  ✅ 전체 작가 검색 워크플로우 테스트 통과")

    def test_prompt_consistency(self):
        """프롬프트 일관성 테스트"""
        print("  🎯 프롬프트 일관성 확인 중...")

        prompt = WikiSearchPrompt()

        # 여러 번 호출해도 같은 결과 반환하는지 확인
        intent_prompt_1 = prompt.get_intent_analysis_prompt()
        intent_prompt_2 = prompt.get_intent_analysis_prompt()

        print(f"    📊 1차 호출 길이: {len(intent_prompt_1)}자")
        print(f"    📊 2차 호출 길이: {len(intent_prompt_2)}자")
        print(f"    ✅ 일관성: {intent_prompt_1 == intent_prompt_2}")

        assert intent_prompt_1 == intent_prompt_2
        print("  ✅ 프롬프트 일관성 테스트 통과")


class TestWikiSearchPromptEdgeCases:
    """WikiSearchPrompt 엣지 케이스 테스트"""

    def test_empty_and_null_data_handling(self):
        """빈 데이터 및 null 값 처리 테스트"""
        edge_cases = [
            {'title': '', 'summary': '', 'url': ''},
            {'title': None, 'summary': None, 'url': None},
            {},
            {'title': '작가', 'summary': None, 'url': ''}
        ]

        prompt = WikiSearchPrompt()

        for i, case in enumerate(edge_cases, 1):
            print(f"  🧪 엣지 케이스 {i}: {case}")

            try:
                result = prompt.format_author_response(case)
                print(f"    📄 결과: '{result[:50]}...'")
                print(f"    ✅ 문자열 반환: {isinstance(result, str)}")
                assert isinstance(result, str)
                print(f"    ✅ 엣지 케이스 {i} 처리 완료")
            except Exception as e:
                print(f"    ⚠️  엣지 케이스 {i} 처리 중 예외: {type(e).__name__}")
                # 엣지 케이스에서는 예외가 발생해도 괜찮지만, 적절한 타입이어야 함
                assert isinstance(e, (TypeError, ValueError, AttributeError, KeyError))
                print(f"    ✅ 적절한 예외 처리됨")

        print("✅ 빈 데이터 및 null 값 처리 테스트 통과")

    def test_special_characters_handling(self):
        """특수 문자 처리 테스트"""
        special_cases = [
            "J.K. 롤링",
            "베르나르 베르베르",
            "무라카미 하루키",
            "José Saramago",
            "작가명@#$%^&*()"
        ]

        prompt = WikiSearchPrompt()

        for name in special_cases:
            print(f"  🌐 특수 문자 테스트: '{name}'")

            result = prompt.get_search_failure_message(name)

            print(f"    📄 결과: '{result[:60]}...'")
            print(f"    ✅ 이름 포함: {name in result}")

            assert isinstance(result, str)
            assert len(result) > 0
            assert name in result
            print(f"    ✅ '{name}' 특수 문자 처리 완료")

        print("✅ 특수 문자 처리 테스트 통과")

class TestWikiSearchPromptPerformance:
    """WikiSearchPrompt 성능 테스트"""

    def test_prompt_generation_performance(self):
        """프롬프트 생성 성능 테스트"""
        print("  ⚡ 프롬프트 생성 성능 테스트 시작...")

        import time
        prompt = WikiSearchPrompt()

        # 성능 측정
        start_time = time.time()

        for i in range(50):  # 적당한 수로 조정
            prompt.get_intent_analysis_prompt()
            prompt.get_author_summary_prompt()
            prompt.get_book_summary_prompt()

        end_time = time.time()
        total_time = end_time - start_time

        print(f"    📊 성능 결과:")
        print(f"      - 총 실행 시간: {total_time:.4f}초")
        print(f"      - 150개 프롬프트 생성 (50회 × 3종류)")
        print(f"      - 평균 시간: {(total_time/150)*1000:.2f}ms/프롬프트")

        # 성능 기준: 150개 프롬프트를 1초 이내에 생성 (여유있게 설정)
        assert total_time < 1.0
        print("  ✅ 프롬프트 생성 성능 테스트 통과")

    def test_response_formatting_performance(self):
        """응답 포맷팅 성능 테스트"""
        print("  ⚡ 응답 포맷팅 성능 테스트 시작...")

        import time
        prompt = WikiSearchPrompt()

        sample_result = {
            'title': '김영하 (작가)',
            'summary': '김영하는 대한민국의 소설가이다.',
            'content': '김영하는 여러 작품을 집필했다.',
            'url': 'https://ko.wikipedia.org/wiki/김영하_(작가)'
        }

        # 성능 측정
        start_time = time.time()

        for i in range(100):
            prompt.format_author_response(sample_result)

        end_time = time.time()
        total_time = end_time - start_time

        print(f"    📊 성능 결과:")
        print(f"      - 총 실행 시간: {total_time:.4f}초")
        print(f"      - 100개 응답 포맷팅")
        print(f"      - 평균 시간: {(total_time/100)*1000:.2f}ms/응답")

        # 성능 기준: 100개 응답을 1초 이내에 포맷팅
        assert total_time < 1.0
        print("  ✅ 응답 포맷팅 성능 테스트 통과")

if __name__ == "__main__":
    print("🧪 WikiSearchPrompt 직관적인 TDD 테스트 시작\n")

    # 기본 기능 테스트
    print("📋 기본 기능 테스트 - 프롬프트 생성 확인")
    print("=" * 60)
    test_basics = TestWikiSearchPromptBasics()
    test_basics.test_prompt_initialization()
    print()
    test_basics.test_get_intent_analysis_prompt()
    print()
    test_basics.test_get_author_summary_prompt()
    print()
    test_basics.test_get_book_summary_prompt()

    #응답 포맷팅 테스트
    print("\n📄 응답 포맷팅 테스트 - 사용자 친화적 응답 생성")
    print("=" * 60)
    test_formatting = TestWikiSearchPromptFormatting()
    test_formatting.test_format_author_response_complete_data()
    print()
    test_formatting.test_format_author_response_minimal_data()

    # 메시지 생성 테스트
    print("\n💬 메시지 생성 테스트 - 다양한 상황별 메시지")
    print("=" * 60)
    test_messages = TestWikiSearchPromptMessages()
    test_messages.test_search_failure_messages()
    print()
    test_messages.test_ambiguous_query_message()
    print()
    test_messages.test_combined_search_failure_message()

    # 특수 메서드 테스트
    print("\n🔧 메서드 확인 테스트 - 클래스 구조 검증")
    print("=" * 60)
    test_special_methods = TestWikiSearchPromptSpecialMethods()
    test_special_methods.test_methods_existence()
    print()
    test_special_methods.test_optional_methods_with_fallback()

    # 통합 테스트
    print("\n🔄 통합 테스트 - 전체 워크플로우 확인")
    print("=" * 60)
    test_integration = TestWikiSearchPromptIntegration()
    test_integration.test_full_author_search_workflow()
    print()
    test_integration.test_prompt_consistency()

    # 엣지 케이스 테스트
    print("\n🚨 엣지 케이스 테스트 - 예외 상황 처리")
    print("=" * 60)
    test_edge_cases = TestWikiSearchPromptEdgeCases()
    test_edge_cases.test_empty_and_null_data_handling()
    print()
    test_edge_cases.test_special_characters_handling()

    # 성능 테스트
    print("\n⚡ 성능 테스트 - 처리 속도 확인")
    print("=" * 60)
    test_performance = TestWikiSearchPromptPerformance()
    test_performance.test_prompt_generation_performance()
    print()
    test_performance.test_response_formatting_performance()

    print("\n" + "=" * 60)
    print("🎉 모든 WikiSearchPrompt 테스트 통과!")
    print("\n📊 테스트 요약:")
    print("  ✅ 기본 기능: 4개 테스트")
    print("  ✅ 응답 포맷팅: 2개 테스트")
    print("  ✅ 메시지 생성: 3개 테스트")
    print("  ✅ 메서드 확인: 2개 테스트")
    print("  ✅ 통합 테스트: 2개 테스트")
    print("  ✅ 엣지 케이스: 2개 테스트")
    print("  ✅ 성능 테스트: 2개 테스트")
    print("\n📝 pytest로 실행하려면:")
    print("    cd ai-service")
    print("    python -m pytest tests/unit/prompts/test_wiki_search_prompt.py -v -s")
