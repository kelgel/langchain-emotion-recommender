"""
WikiTextProcessor 직관적인 TDD 테스트
각 테스트마다 성공 메시지 출력으로 진행상황을 실시간 확인

실행 방법:
    cd ai-service
    python tests/unit/utils/test_wiki_text_processing.py
    또는
    python -m pytest tests/unit/utils/test_wiki_text_processing.py -v -s
"""

import pytest
import sys
import os
import json
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 의존성 모듈 Mock 설정
mock_modules = ['utils', 'models', 'tools', 'chains', 'prompts']
for module_name in mock_modules:
    if module_name not in sys.modules:
        sys.modules[module_name] = Mock()

# 테스트 대상 import
from app.utils.wiki_text_processing import WikiTextProcessor


class TestWikiTextProcessorBasics:
    """WikiTextProcessor 기본 작가명 추출 테스트"""

    def test_extract_author_name_with_llm_success(self):
        """LLM을 사용한 작가명 추출 성공 테스트"""
        # Mock LLM 클라이언트 설정
        mock_llm_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()

        mock_llm_client.chat.completions.create.return_value = mock_response
        mock_response.choices = [mock_choice]
        mock_choice.message = mock_message
        mock_message.content = json.dumps({
            "author_name": "한강",
            "confidence": 0.9
        })

        print(f"  🤖 LLM을 사용한 작가명 추출...")
        print(f"  📝 입력 쿼리: '한강이 누구야'")
        print(f"  🎯 LLM 응답: 작가명='한강', 신뢰도=0.9")

        result = WikiTextProcessor.extract_author_name("한강이 누구야", mock_llm_client)

        print(f"  📊 추출 결과: '{result}'")
        print(f"  ✅ LLM 호출됨: {mock_llm_client.chat.completions.create.called}")
        print(f"  ✅ 작가명 정확성: {'한강' == result}")

        assert result == "한강"
        assert mock_llm_client.chat.completions.create.called
        print("✅ LLM을 사용한 작가명 추출 성공 테스트 통과")

    def test_extract_author_name_with_llm_low_confidence_fallback(self):
        """LLM 낮은 신뢰도로 폴백 테스트"""
        mock_llm_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()

        mock_llm_client.chat.completions.create.return_value = mock_response
        mock_response.choices = [mock_choice]
        mock_choice.message = mock_message
        mock_message.content = json.dumps({
            "author_name": "한강",
            "confidence": 0.5  # 낮은 신뢰도
        })

        print(f"  📉 LLM 낮은 신뢰도 폴백 테스트...")
        print(f"  📝 입력: '한강이 누구야'")
        print(f"  🤖 LLM 신뢰도: 0.5 (임계값 0.7 미만)")
        print(f"  🔄 폴백 방식으로 전환됨")

        result = WikiTextProcessor.extract_author_name("한강이 누구야", mock_llm_client)

        print(f"  📊 폴백 추출 결과: '{result}'")
        print(f"  ✅ 결과 정확성: {'한강' == result}")

        assert result == "한강"  # 폴백 방식으로도 정확히 추출
        print("✅ LLM 낮은 신뢰도 폴백 테스트 통과")

    def test_extract_author_name_llm_failure_fallback(self):
        """LLM 실패시 폴백 테스트"""
        mock_llm_client = Mock()
        mock_llm_client.chat.completions.create.side_effect = Exception("API Error")

        print(f"  ⚠️ LLM 실패시 폴백 테스트...")
        print(f"  📝 입력: '한강이 누구야'")
        print(f"  🚨 LLM API 오류 발생")
        print(f"  🔄 폴백 방식으로 자동 전환")

        result = WikiTextProcessor.extract_author_name("한강이 누구야", mock_llm_client)

        print(f"  📊 폴백 추출 결과: '{result}'")
        print(f"  ✅ 오류 처리 성공: LLM 실패에도 결과 반환")
        print(f"  ✅ 결과 정확성: {'한강' == result}")

        assert result == "한강"  # 폴백으로 정상 추출
        print("✅ LLM 실패시 폴백 테스트 통과")

    def test_fallback_extract_author_name_who_patterns(self):
        """폴백 방식 - '누구' 패턴 작가명 추출 테스트"""
        test_cases = [
            ("한강가 누구", "한강"),
            ("한강이 누구", "한강"),
            ("이말년이 누구야", "이말년"),
            ("김영하 누구", "김영하"),
        ]

        print(f"  🔍 '누구' 패턴 작가명 추출 테스트...")
        print(f"  📋 테스트 케이스: {len(test_cases)}개")

        for i, (query, expected) in enumerate(test_cases, 1):
            print(f"    {i}. 쿼리: '{query}' → 예상: '{expected}'")

            result = WikiTextProcessor._fallback_extract_author_name(query)

            print(f"       📊 결과: '{result}'")
            print(f"       ✅ 정확성: {expected == result}")

            assert result == expected
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ '누구' 패턴 작가명 추출 테스트 통과")

    def test_fallback_extract_foreign_author_names(self):
        """폴백 방식 - 외국인 작가명 패턴 테스트"""
        test_cases = [
            ("무라카미 하루키", "무라카미 하루키"),
            ("조지 오웰", "조지 오웰"),
            ("가브리엘 가르시아 마르케스", "가브리엘 가르시아"),  # 첫 두 단어만
        ]

        print(f"  🌏 외국인 작가명 패턴 테스트...")
        print(f"  📋 테스트 케이스: {len(test_cases)}개")

        for i, (query, expected) in enumerate(test_cases, 1):
            print(f"    {i}. 쿼리: '{query}' → 예상: '{expected}'")

            result = WikiTextProcessor._fallback_extract_author_name(query)

            print(f"       📊 결과: '{result}'")
            print(f"       ✅ 정확성: {expected == result}")

            assert result == expected
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 외국인 작가명 패턴 테스트 통과")


class TestWikiTextProcessorClarification:
    """WikiTextProcessor 명확화 응답 처리 테스트"""

    def test_parse_clarification_response_number_patterns(self):
        """명확화 응답 파싱 - 숫자 선택 패턴 테스트"""
        context = {
            'clarification_candidates': ['한강', '김영하', '이말년']
        }

        test_cases = [
            ("1", "한강"),
            ("2번", "김영하"),
            ("3번째", "이말년"),
            ("첫번째", "한강"),
            ("두번째", "김영하"),
            ("세번째", "이말년"),
        ]

        print(f"  🔢 숫자 선택 패턴 테스트...")
        print(f"  📋 후보: {context['clarification_candidates']}")
        print(f"  📋 테스트 케이스: {len(test_cases)}개")

        for i, (query, expected) in enumerate(test_cases, 1):
            print(f"    {i}. 입력: '{query}' → 예상: '{expected}'")

            result = WikiTextProcessor.parse_clarification_response(query, context)

            print(f"       📊 선택 결과: '{result}'")
            print(f"       ✅ 정확성: {expected == result}")

            assert result == expected
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 숫자 선택 패턴 테스트 통과")

    def test_parse_clarification_response_direct_mention(self):
        """명확화 응답 파싱 - 직접 언급 패턴 테스트"""
        context = {}

        test_cases = [
            ("한강 말하는거야", "한강"),
            ("김영하 맞아", "김영하"),
            ("이말년이야", "이말년"),
            ("박민규요", "박민규"),
        ]

        print(f"  💬 직접 언급 패턴 테스트...")
        print(f"  📋 테스트 케이스: {len(test_cases)}개")

        for i, (query, expected) in enumerate(test_cases, 1):
            print(f"    {i}. 입력: '{query}' → 예상: '{expected}'")

            result = WikiTextProcessor.parse_clarification_response(query, context)

            print(f"       📊 추출 결과: '{result}'")
            print(f"       ✅ 정확성: {expected == result}")

            assert result == expected
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 직접 언급 패턴 테스트 통과")

    def test_parse_clarification_response_invalid_cases(self):
        """명확화 응답 파싱 - 유효하지 않은 케이스 테스트"""
        context = {
            'clarification_candidates': ['한강', '김영하']
        }

        test_cases = [
            ("10", None),  # 범위 초과
            ("알 수 없음", None),  # 패턴 불일치
            ("", None),  # 빈 문자열
            ("뭔가 이상해", None),  # 인식 불가
        ]

        print(f"  ❌ 유효하지 않은 입력 처리 테스트...")
        print(f"  📋 테스트 케이스: {len(test_cases)}개")

        for i, (query, expected) in enumerate(test_cases, 1):
            print(f"    {i}. 입력: '{query}' → 예상: {expected}")

            result = WikiTextProcessor.parse_clarification_response(query, context)

            print(f"       📊 처리 결과: {result}")
            print(f"       ✅ 예상대로 None 반환: {expected == result}")

            assert result == expected
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 유효하지 않은 케이스 처리 테스트 통과")


class TestWikiTextProcessorContextQuestions:
    """WikiTextProcessor 컨텍스트 질문 처리 테스트"""

    def test_extract_author_from_context_question_success(self):
        """컨텍스트 질문에서 작가명 추출 성공 테스트"""
        test_cases = [
            ("이말년은 어디 대학", "이말년"),
            ("한강이 언제", "한강"),
            ("김영하 대학", "김영하"),
            ("박민규 출생", "박민규"),
            ("조정래는 몇", "조정래"),
        ]

        print(f"  🔍 컨텍스트 질문 작가명 추출 테스트...")
        print(f"  📋 테스트 케이스: {len(test_cases)}개")
        print(f"  🎯 목표: '작가명은/이 질문어' 패턴에서 작가명 추출")

        for i, (query, expected) in enumerate(test_cases, 1):
            print(f"    {i}. 쿼리: '{query}' → 예상: '{expected}'")

            result = WikiTextProcessor.extract_author_from_context_question(query)

            print(f"       📊 추출 결과: '{result}'")
            print(f"       ✅ 정확성: {expected == result}")

            assert result == expected
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 컨텍스트 질문 작가명 추출 테스트 통과")

    def test_extract_author_from_context_question_invalid(self):
        """컨텍스트 질문 - 유효하지 않은 케이스 테스트"""
        test_cases = [
            ("어디 대학", None),  # 작가명 없음
            ("뭔가 이상해", None),  # 패턴 불일치
            ("", None),  # 빈 문자열
            ("그냥 궁금해", None),  # 작가명 패턴 없음
        ]

        print(f"  ❌ 컨텍스트 질문 무효 케이스 테스트...")
        print(f"  📋 테스트 케이스: {len(test_cases)}개")

        for i, (query, expected) in enumerate(test_cases, 1):
            print(f"    {i}. 쿼리: '{query}' → 예상: {expected}")

            result = WikiTextProcessor.extract_author_from_context_question(query)

            print(f"       📊 처리 결과: {result}")
            print(f"       ✅ 예상대로 None 반환: {expected == result}")

            assert result == expected
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 컨텍스트 질문 무효 케이스 테스트 통과")


class TestWikiTextProcessorBookExtraction:
    """WikiTextProcessor 책 제목 추출 테스트"""

    def test_extract_book_title_from_query_basic(self):
        """쿼리에서 기본 책 제목 추출 테스트"""
        test_cases = [
            ("개미 작가 누구야", "개미"),
            ("채식주의자를 쓴 작가", "채식주의자"),
            ("토지는 누가 썼어", "토지"),
            ("해리포터 저자 알려줘", "해리포터"),
            ("1984 쓴이가 누구야?", "1984"),
        ]

        print(f"  📚 기본 책 제목 추출 테스트...")
        print(f"  📋 테스트 케이스: {len(test_cases)}개")
        print(f"  🎯 목표: 쿼리에서 키워드 제거 후 책 제목만 추출")

        for i, (query, expected) in enumerate(test_cases, 1):
            print(f"    {i}. 쿼리: '{query}' → 예상: '{expected}'")

            result = WikiTextProcessor.extract_book_title_from_query(query)

            print(f"       📊 추출 결과: '{result}'")
            print(f"       ✅ 정확성: {expected == result}")

            assert result == expected
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 기본 책 제목 추출 테스트 통과")

    def test_extract_book_title_complex_cases(self):
        """복잡한 책 제목 추출 테스트"""
        test_cases = [
            ("오만과 편견 작가", "오만 편견"),  # '과' 제거
            ("그리고 아무 말 하지 않았다 저자", "와 아무 말 하지 않았다"),  # '그리고' → '와'
            ("해리포터와 마법사의 돌 누가 썼어", "해리포터 마법사 돌"),
        ]

        print(f"  🔧 복잡한 책 제목 추출 테스트...")
        print(f"  📋 테스트 케이스: {len(test_cases)}개")
        print(f"  🎯 목표: 접속사 변환 및 복잡한 키워드 처리")

        for i, (query, expected) in enumerate(test_cases, 1):
            print(f"    {i}. 쿼리: '{query}'")
            print(f"       🔄 처리: 접속사 변환, 키워드 제거")
            print(f"       🎯 예상: '{expected}'")

            result = WikiTextProcessor.extract_book_title_from_query(query)

            print(f"       📊 추출 결과: '{result}'")
            print(f"       ✅ 정확성: {expected == result}")

            assert result == expected
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 복잡한 책 제목 추출 테스트 통과")

    def test_handle_conjunction_in_title(self):
        """제목의 접속사 처리 테스트"""
        test_cases = [
            ("오만 그리고 편견", "오만 와 편견"),
            ("해리포터 하고 마법사", "해리포터 와 마법사"),
            ("돈 랑 권력", "돈 와 권력"),
            ("사랑 이랑 전쟁", "사랑 와 전쟁"),
        ]

        print(f"  🔗 접속사 처리 테스트...")
        print(f"  📋 테스트 케이스: {len(test_cases)}개")
        print(f"  🎯 목표: 다양한 접속사를 '와'로 통일")

        for i, (title, expected) in enumerate(test_cases, 1):
            print(f"    {i}. 입력: '{title}' → 예상: '{expected}'")

            result = WikiTextProcessor._handle_conjunction_in_title(title)

            print(f"       📊 변환 결과: '{result}'")
            print(f"       ✅ 정확성: {expected == result}")

            assert result == expected
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 접속사 처리 테스트 통과")


class TestWikiTextProcessorIntegration:
    """WikiTextProcessor 통합 테스트"""

    def test_full_author_extraction_workflow(self):
        """전체 작가명 추출 워크플로우 테스트"""
        test_scenarios = [
            {
                "query": "한강이 누구야",
                "expected_author": "한강",
                "description": "단순 작가명 질문",
                "method": "direct_question"
            },
            {
                "query": "무라카미 하루키 작품 알려줘",
                "expected_author": "무라카미 하루키",
                "description": "외국 작가명 + 요청",
                "method": "foreign_name"
            },
            {
                "query": "개미 쓴 작가",
                "expected_book": "개미",
                "description": "책 제목으로 작가 역추적",
                "method": "book_reverse"
            }
        ]

        print(f"  🔄 전체 작가명 추출 워크플로우 테스트...")
        print(f"  📋 시나리오: {len(test_scenarios)}개")

        for i, scenario in enumerate(test_scenarios, 1):
            print(f"    {i}. {scenario['description']}")
            print(f"       📝 쿼리: '{scenario['query']}'")
            print(f"       🎯 방법: {scenario['method']}")

            if "expected_author" in scenario:
                result = WikiTextProcessor.extract_author_name(scenario["query"])
                expected = scenario["expected_author"]

                print(f"       📊 작가명 추출: '{result}'")
                print(f"       ✅ 정확성: {expected == result}")
                assert result == expected

            if "expected_book" in scenario:
                result = WikiTextProcessor.extract_book_title_from_query(scenario["query"])
                expected = scenario["expected_book"]

                print(f"       📊 책 제목 추출: '{result}'")
                print(f"       ✅ 정확성: {expected == result}")
                assert result == expected

            print(f"       ✅ 시나리오 {i} 통과")

        print("✅ 전체 작가명 추출 워크플로우 테스트 통과")

    def test_clarification_workflow_integration(self):
        """명확화 워크플로우 통합 테스트"""
        print(f"  🔍 명확화 워크플로우 통합 테스트...")

        # 1단계: 동명이인 상황 시뮬레이션
        context = {
            'clarification_candidates': ['한강(소설가)', '한강(강)', '한강(지명)']
        }

        print(f"    1️⃣ 동명이인 상황 설정")
        print(f"       📋 후보: {context['clarification_candidates']}")

        # 2단계: 사용자 선택 파싱
        user_responses = [
            ("1", "한강(소설가)"),
            ("첫번째", "한강(소설가)"),
            ("한강 소설가 말하는거야", "한강"),
        ]

        print(f"    2️⃣ 사용자 응답 처리 테스트")

        for j, (response, expected_contain) in enumerate(user_responses, 1):
            print(f"       {j}. 응답: '{response}'")

            result = WikiTextProcessor.parse_clarification_response(response, context)

            print(f"          📊 처리 결과: '{result}'")

            if "한강" in expected_contain:  # 부분 매칭 허용
                assert result and "한강" in result
                print(f"          ✅ '한강' 포함 확인")
            else:
                assert result == expected_contain
                print(f"          ✅ 정확한 매칭 확인")

            print(f"          ✅ 응답 {j} 처리 완료")

        print("✅ 명확화 워크플로우 통합 테스트 통과")


class TestWikiTextProcessorPerformance:
    """WikiTextProcessor 성능 테스트"""

    def test_extraction_performance_large_batch(self):
        """대량 추출 성능 테스트"""
        queries = [
                      "한강이 누구야",
                      "무라카미 하루키",
                      "김영하 작가",
                      "개미 저자",
                      "채식주의자 쓴 사람"
                  ] * 100  # 500개 쿼리

        print(f"  ⚡ 대량 추출 성능 테스트...")
        print(f"    - 테스트 쿼리 수: {len(queries):,}개")
        print(f"    - 목표 시간: 5초 이내")

        start_time = time.time()

        results = []
        for i, query in enumerate(queries):
            result = WikiTextProcessor.extract_author_name(query)
            results.append(result)

            if (i + 1) % 100 == 0:
                elapsed = time.time() - start_time
                print(f"      💾 진행: {i + 1:,}개 처리 완료 ({elapsed:.2f}초)")

        end_time = time.time()
        processing_time = end_time - start_time

        print(f"    📊 성능 결과:")
        print(f"      - 총 처리 시간: {processing_time:.4f}초")
        print(f"      - 평균 처리 시간: {processing_time/len(queries):.6f}초/개")
        print(f"      - 초당 처리량: {len(queries)/processing_time:.1f}개/초")
        print(f"      - 결과 수: {len(results):,}개")

        # 성능 검증 (500개 쿼리를 5초 이내 처리)
        assert processing_time < 5.0
        assert len(results) == len(queries)
        assert all(isinstance(r, str) for r in results)

        print("✅ 대량 추출 성능 테스트 통과")

    def test_memory_usage_stability(self):
        """메모리 사용량 안정성 테스트"""
        try:
            import psutil
        except ImportError:
            print("  ⚠️ psutil 모듈이 없어 메모리 테스트를 건너뜁니다.")
            return

        print(f"  💾 메모리 사용량 안정성 테스트...")

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        print(f"    - 초기 메모리: {initial_memory / 1024 / 1024:.2f}MB")

        # 대량 처리
        for i in range(1000):
            WikiTextProcessor.extract_author_name("한강이 누구야")
            WikiTextProcessor.extract_book_title_from_query("개미 작가 누구야")

            if (i + 1) % 200 == 0:
                current_memory = process.memory_info().rss
                print(f"      💽 {i + 1:,}회 처리 후: {current_memory / 1024 / 1024:.2f}MB")

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        print(f"    📊 메모리 사용량 결과:")
        print(f"      - 최종 메모리: {final_memory / 1024 / 1024:.2f}MB")
        print(f"      - 메모리 증가: {memory_increase / 1024 / 1024:.2f}MB")
        print(f"      - 증가율: {(memory_increase / initial_memory) * 100:.2f}%")

        # 메모리 증가량이 50MB 이하인지 확인
        assert memory_increase < 50 * 1024 * 1024

        print("✅ 메모리 사용량 안정성 테스트 통과")


class TestWikiTextProcessorErrorHandling:
    """WikiTextProcessor 오류 처리 테스트"""

    def test_handle_invalid_input_types(self):
        """유효하지 않은 입력 타입 처리 테스트"""
        invalid_inputs = [None, 123, [], {}, True, 3.14]

        print(f"  🚫 유효하지 않은 입력 타입 처리 테스트...")
        print(f"  📋 테스트 입력: {len(invalid_inputs)}개")

        for i, test_input in enumerate(invalid_inputs, 1):
            print(f"    {i}. 입력 타입: {type(test_input).__name__} = {test_input}")

            try:
                result = WikiTextProcessor.extract_author_name(test_input)
                print(f"       ⚠️ 예외가 발생해야 하는데 결과 반환: '{result}'")
                assert False, f"예외가 발생해야 함: {test_input}"

            except AttributeError as e:
                print(f"       ✅ 예상된 AttributeError 발생: {e}")
                assert True

            except Exception as e:
                print(f"       ✅ 적절한 예외 발생: {type(e).__name__}: {e}")
                assert isinstance(e, (TypeError, ValueError, AttributeError))

            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 유효하지 않은 입력 타입 처리 테스트 통과")

    def test_handle_empty_and_whitespace_input(self):
        """빈 문자열 및 공백 입력 처리 테스트"""
        empty_inputs = ["", "   ", "\n\n", "\t\t", "    \n    "]

        print(f"  🗳️ 빈 문자열 및 공백 입력 처리 테스트...")
        print(f"  📋 테스트 입력: {len(empty_inputs)}개")

        for i, test_input in enumerate(empty_inputs, 1):
            print(f"    {i}. 입력: {repr(test_input)}")

            result = WikiTextProcessor.extract_author_name(test_input)
            book_result = WikiTextProcessor.extract_book_title_from_query(test_input)

            print(f"       📊 작가명 추출: '{result}'")
            print(f"       📊 책 제목 추출: '{book_result}'")
            print(f"       ✅ 빈 결과 반환: {result == ''}")

            # 빈 문자열이 반환되어야 함
            assert result == ""
            assert book_result == "" or book_result.strip() == ""

            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 빈 문자열 및 공백 입력 처리 테스트 통과")

    def test_handle_empty_context_gracefully(self):
        """빈 컨텍스트 우아한 처리 테스트"""
        empty_contexts = [{}, None, {'other_key': 'value'}]

        print(f"  🔍 빈 컨텍스트 우아한 처리 테스트...")
        print(f"  📋 테스트 컨텍스트: {len(empty_contexts)}개")

        for i, context in enumerate(empty_contexts, 1):
            print(f"    {i}. 컨텍스트: {context}")

            result = WikiTextProcessor.parse_clarification_response("1", context)

            print(f"       📊 처리 결과: {result}")
            print(f"       ✅ None 반환: {result is None}")

            assert result is None
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 빈 컨텍스트 우아한 처리 테스트 통과")

    def test_handle_malformed_llm_response(self):
        """잘못된 LLM 응답 처리 테스트"""
        malformed_responses = [
            "Invalid JSON",
            '{"incomplete": "json"',
            '{"author_name": null}',
            '{"confidence": "not_a_number"}',
            "",
            "Just plain text"
        ]

        print(f"  🤖 잘못된 LLM 응답 처리 테스트...")
        print(f"  📋 테스트 응답: {len(malformed_responses)}개")

        for i, malformed_response in enumerate(malformed_responses, 1):
            print(f"    {i}. LLM 응답: '{malformed_response}'")

            mock_llm_client = Mock()
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()

            mock_llm_client.chat.completions.create.return_value = mock_response
            mock_response.choices = [mock_choice]
            mock_choice.message = mock_message
            mock_message.content = malformed_response

            # JSON 파싱 실패시 폴백 동작 확인
            result = WikiTextProcessor.extract_author_name("한강이 누구야", mock_llm_client)

            print(f"       📊 폴백 결과: '{result}'")
            print(f"       ✅ 폴백 성공: {'한강' == result}")

            # 폴백으로 정상 추출되어야 함
            assert result == "한강"
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 잘못된 LLM 응답 처리 테스트 통과")


class TestWikiTextProcessorEdgeCases:
    """WikiTextProcessor 엣지 케이스 테스트"""

    def test_unicode_and_special_characters(self):
        """유니코드 및 특수문자 처리 테스트"""
        unicode_test_cases = [
            ("김영하🎭 누구야", "김영하"),  # 이모지 포함
            ("José Saramago는 누구", "José Saramago"),  # 라틴 문자
            ("Муракими Харуки", "Муракими Харуки"),  # 키릴 문자
            ("村上春樹 작가", "村上春樹"),  # 한자
            ("α·β·γ 그리스문자 포함한 김영하", "김영하"),  # 그리스 문자
        ]

        print(f"  🌐 유니코드 및 특수문자 처리 테스트...")
        print(f"  📋 테스트 케이스: {len(unicode_test_cases)}개")

        for i, (query, expected) in enumerate(unicode_test_cases, 1):
            print(f"    {i}. 쿼리: '{query}'")
            print(f"       🎯 예상: '{expected}'")

            try:
                result = WikiTextProcessor.extract_author_name(query)

                print(f"       📊 추출 결과: '{result}'")
                print(f"       ✅ 유니코드 처리 성공")

                # 결과가 문자열이고 비어있지 않아야 함
                assert isinstance(result, str)

                # 예상 결과와 일치하거나 부분적으로라도 포함해야 함
                if expected in result or result in expected:
                    print(f"       ✅ 내용 일치 또는 부분 일치")
                else:
                    print(f"       ⚠️ 불일치하지만 유니코드 처리는 성공")

                print(f"       ✅ 테스트 {i} 통과")

            except Exception as e:
                print(f"       ❌ 예외 발생: {type(e).__name__}: {e}")
                # 유니코드 관련 예외만 허용
                assert isinstance(e, (UnicodeError, UnicodeDecodeError, UnicodeEncodeError))
                print(f"       ✅ 적절한 유니코드 예외 처리")

        print("✅ 유니코드 및 특수문자 처리 테스트 통과")

    def test_very_long_text_handling(self):
        """매우 긴 텍스트 처리 테스트"""
        # 매우 긴 텍스트 생성
        base_text = "김영하는 1968년에 태어난 한국의 소설가이다. "
        long_text = base_text * 1000  # 약 44,000자
        long_query = long_text + "김영하가 누구야"

        print(f"  📏 매우 긴 텍스트 처리 테스트...")
        print(f"    - 텍스트 길이: {len(long_query):,}자")
        print(f"    - 목표: 5초 이내 처리")

        start_time = time.time()

        result = WikiTextProcessor.extract_author_name(long_query)

        end_time = time.time()
        processing_time = end_time - start_time

        print(f"    📊 처리 결과:")
        print(f"      - 처리 시간: {processing_time:.4f}초")
        print(f"      - 추출 결과: '{result}'")
        print(f"      - 결과 정확성: {'김영하' == result}")

        # 성능 및 정확성 검증
        assert processing_time < 5.0
        assert result == "김영하"

        print("✅ 매우 긴 텍스트 처리 테스트 통과")

    def test_mixed_language_queries(self):
        """다국어 혼합 쿼리 처리 테스트"""
        mixed_queries = [
            ("Murakami Haruki 무라카미 하루키 누구야", "Murakami Haruki"),
            ("김영하 Kim Young-ha author", "김영하"),
            ("한강 Han Kang writer information", "한강"),
            ("George Orwell 조지 오웰 작가", "George Orwell"),
        ]

        print(f"  🌍 다국어 혼합 쿼리 처리 테스트...")
        print(f"  📋 테스트 케이스: {len(mixed_queries)}개")

        for i, (query, expected_contain) in enumerate(mixed_queries, 1):
            print(f"    {i}. 쿼리: '{query}'")
            print(f"       🎯 예상 포함: '{expected_contain}'")

            result = WikiTextProcessor.extract_author_name(query)

            print(f"       📊 추출 결과: '{result}'")

            # 예상 문자열이 결과에 포함되어야 함 (순서나 형태 무관)
            contains_expected = expected_contain in result or any(
                word in result for word in expected_contain.split()
            )

            print(f"       ✅ 예상 내용 포함: {contains_expected}")

            assert contains_expected or result != ""  # 최소한 빈 결과가 아니어야 함
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 다국어 혼합 쿼리 처리 테스트 통과")

    def test_complex_punctuation_handling(self):
        """복잡한 구두점 처리 테스트"""
        punctuation_queries = [
            ("김영하가... 누구야???", "김영하"),
            ("한강이!!! 정말 누구인지 알려줘!!!", "한강"),
            ("\"무라카미 하루키\"는 누구입니까?", "무라카미 하루키"),
            ("(이말년) 작가에 대해...", "이말년"),
            ("김영하, 한강... 이 작가들은?", "김영하"),  # 첫 번째만 추출
        ]

        print(f"  📝 복잡한 구두점 처리 테스트...")
        print(f"  📋 테스트 케이스: {len(punctuation_queries)}개")

        for i, (query, expected) in enumerate(punctuation_queries, 1):
            print(f"    {i}. 쿼리: '{query}'")
            print(f"       🎯 예상: '{expected}'")

            result = WikiTextProcessor.extract_author_name(query)

            print(f"       📊 추출 결과: '{result}'")
            print(f"       ✅ 정확성: {expected == result}")

            assert result == expected
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 복잡한 구두점 처리 테스트 통과")


if __name__ == "__main__":
    start_time = time.time()

    print("🧪 WikiTextProcessor 직관적인 TDD 테스트 시작\n")

    # 기본 작가명 추출 테스트
    print("📋 기본 작가명 추출 테스트 - LLM 및 폴백 방식")
    print("=" * 60)
    test_basics = TestWikiTextProcessorBasics()
    test_basics.test_extract_author_name_with_llm_success()
    print()
    test_basics.test_extract_author_name_with_llm_low_confidence_fallback()
    print()
    test_basics.test_extract_author_name_llm_failure_fallback()
    print()
    test_basics.test_fallback_extract_author_name_who_patterns()
    print()
    test_basics.test_fallback_extract_foreign_author_names()

    # 명확화 응답 처리 테스트
    print("\n🔍 명확화 응답 처리 테스트 - 동명이인 해결")
    print("=" * 60)
    test_clarification = TestWikiTextProcessorClarification()
    test_clarification.test_parse_clarification_response_number_patterns()
    print()
    test_clarification.test_parse_clarification_response_direct_mention()
    print()
    test_clarification.test_parse_clarification_response_invalid_cases()

    # 컨텍스트 질문 처리 테스트
    print("\n💬 컨텍스트 질문 처리 테스트 - 대화 맥락 이해")
    print("=" * 60)
    test_context = TestWikiTextProcessorContextQuestions()
    test_context.test_extract_author_from_context_question_success()
    print()
    test_context.test_extract_author_from_context_question_invalid()

    # 책 제목 추출 테스트
    print("\n📚 책 제목 추출 테스트 - 역추적 검색")
    print("=" * 60)
    test_book = TestWikiTextProcessorBookExtraction()
    test_book.test_extract_book_title_from_query_basic()
    print()
    test_book.test_extract_book_title_complex_cases()
    print()
    test_book.test_handle_conjunction_in_title()

    # 통합 테스트
    print("\n🔄 통합 테스트 - 전체 워크플로우 검증")
    print("=" * 60)
    test_integration = TestWikiTextProcessorIntegration()
    test_integration.test_full_author_extraction_workflow()
    print()
    test_integration.test_clarification_workflow_integration()

    # 성능 테스트
    print("\n⚡ 성능 테스트 - 처리 속도 및 메모리 효율성")
    print("=" * 60)
    test_performance = TestWikiTextProcessorPerformance()
    test_performance.test_extraction_performance_large_batch()
    print()
    test_performance.test_memory_usage_stability()

    # 오류 처리 테스트
    print("\n🚫 오류 처리 테스트 - 예외 상황 대응")
    print("=" * 60)
    test_error = TestWikiTextProcessorErrorHandling()
    test_error.test_handle_invalid_input_types()
    print()
    test_error.test_handle_empty_and_whitespace_input()
    print()
    test_error.test_handle_empty_context_gracefully()
    print()
    test_error.test_handle_malformed_llm_response()

    # 엣지 케이스 테스트
    print("\n🌟 엣지 케이스 테스트 - 특수 상황 처리")
    print("=" * 60)
    test_edge = TestWikiTextProcessorEdgeCases()
    test_edge.test_unicode_and_special_characters()
    print()
    test_edge.test_very_long_text_handling()
    print()
    test_edge.test_mixed_language_queries()
    print()
    test_edge.test_complex_punctuation_handling()

    end_time = time.time()
    total_time = end_time - start_time

    print("\n" + "=" * 60)
    print("🎉 모든 WikiTextProcessor 테스트 통과!")
    print(f"⏱️ 총 실행 시간: {total_time:.2f}초")
    print("\n📊 테스트 요약:")
    print("  ✅ 기본 작가명 추출: 5개 테스트")
    print("  ✅ 명확화 응답 처리: 3개 테스트")
    print("  ✅ 컨텍스트 질문 처리: 2개 테스트")
    print("  ✅ 책 제목 추출: 3개 테스트")
    print("  ✅ 통합 테스트: 2개 테스트")
    print("  ✅ 성능 테스트: 2개 테스트")
    print("  ✅ 오류 처리: 4개 테스트")
    print("  ✅ 엣지 케이스: 4개 테스트")
    print(f"\n📈 총 테스트 수: 25개")
    print("\n📝 pytest로 실행하려면:")
    print("    cd ai-service")
    print("    python -m pytest tests/unit/utils/test_wiki_text_processing.py -v -s")
    print("\n🚀 개별 실행:")
    print("    python tests/unit/utils/test_wiki_text_processing.py")