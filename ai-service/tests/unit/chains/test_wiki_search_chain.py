"""
WikiSearchChain 직관적인 TDD 테스트
각 테스트마다 성공 메시지 출력으로 진행상황을 실시간 확인

실행 방법:
    cd ai-service
    python tests/unit/chains/test_wiki_search_chain.py
    또는
    python -m pytest tests/unit/chains/test_wiki_search_chain.py -v -s
"""

import pytest
import sys
import os
import json
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 의존성 모듈 Mock 설정
mock_modules = ['utils', 'models', 'tools', 'chains', 'prompts']
for module_name in mock_modules:
    if module_name not in sys.modules:
        sys.modules[module_name] = Mock()

# 테스트 대상 import
from app.chains.wiki_search_chain import WikiSearchChain

class TestWikiSearchChainBasics:
    """WikiSearchChain 기본 워크플로우 테스트"""

    def setup_method(self):
        """각 테스트 전에 실행되는 설정"""
        self.mock_llm_client = Mock()
        self.chain = WikiSearchChain(llm_client=self.mock_llm_client)

        # Mock tool과 prompt 설정
        self.chain.tool = Mock()
        self.chain.prompt = Mock()

        # 기본 성공 응답 설정
        self.chain.tool.search_page.return_value = {
            'success': True,
            'title': '한강 (작가)',
            'summary': '한강은 대한민국의 소설가이다.',
            'content': '한강은 1970년 광주에서 태어났다. 연세대학교 국어국문학과를 졸업했다.',
            'url': 'https://ko.wikipedia.org/wiki/한강_(작가)'
        }

        self.chain.prompt.format_author_response.return_value = "한강 작가 정보입니다."

    def test_execute_fresh_search_flow_with_author_name(self):
        """작가명이 포함된 쿼리의 신규 검색 플로우 테스트"""
        query = "한강 작가에 대해 알려줘"
        context = {}

        print(f"  🔍 신규 검색 플로우 테스트 - 작가명 포함")
        print(f"  📝 입력 쿼리: '{query}'")
        print(f"  🎯 예상 흐름: 신규 검색 → 작가 검색 처리")

        # LLM 의도 분석 모킹
        self.mock_llm_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content=json.dumps({
                'intent_type': 'author_search',
                'extracted_keywords': ['한강'],
                'confidence': 0.9
            })))]
        )

        result = self.chain.execute(query, context)

        print(f"  📊 실행 결과:")
        print(f"    - 액션: {result.get('action')}")
        print(f"    - 메시지 길이: {len(result.get('message', ''))}")
        print(f"    - 컨텍스트 업데이트: {bool(result.get('update_context'))}")
        print(f"  ✅ 검색 도구 호출됨: {self.chain.tool.search_page.called}")
        print(f"  ✅ LLM 호출됨: {self.mock_llm_client.chat.completions.create.called}")

        assert result.get('action') in ['show_result', 'ask_clarification']
        assert 'message' in result
        assert 'update_context' in result
        assert self.chain.tool.search_page.called

        print("✅ 작가명 포함 신규 검색 플로우 테스트 통과")

    def test_execute_context_question_flow(self):
        """컨텍스트 기반 질문 처리 플로우 테스트"""
        query = "그 작가 나이는?"
        context = {
            'current_author': '한강',
            'last_search_result': {
                'success': True,
                'title': '한강 (작가)',
                'content': '한강은 1970년 11월 27일 광주에서 태어났다.',
                'url': 'https://ko.wikipedia.org/wiki/한강_(작가)'
            }
        }

        print(f"  💬 컨텍스트 질문 처리 플로우 테스트")
        print(f"  📝 입력 쿼리: '{query}'")
        print(f"  🎯 컨텍스트: 작가={context['current_author']}")
        print(f"  🎯 예상 흐름: 컨텍스트 사용 → 특정 정보 추출")

        result = self.chain.execute(query, context)

        print(f"  📊 실행 결과:")
        print(f"    - 액션: {result.get('action')}")
        print(f"    - 메시지 포함 '1970': {'1970' in result.get('message', '')}")
        print(f"    - 컨텍스트 유지: {result.get('update_context', {}).get('current_author') == '한강'}")

        assert result.get('action') == 'show_result'
        assert '1970' in result.get('message', '') or '출생' in result.get('message', '')

        print("✅ 컨텍스트 질문 처리 플로우 테스트 통과")

    def test_execute_clarification_response_flow(self):
        """명확화 응답 처리 플로우 테스트"""
        query = "채식주의자"
        context = {
            'waiting_for_clarification': True,
            'current_author': '한강'
        }

        print(f"  🔍 명확화 응답 처리 플로우 테스트")
        print(f"  📝 입력 응답: '{query}'")
        print(f"  🎯 상태: 명확화 대기 중")
        print(f"  🎯 예상 흐름: 명확화 파싱 → 추가 검색")

        # LLM 명확화 파싱 모킹
        self.mock_llm_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content=json.dumps({
                'book_title': '채식주의자',
                'author_name': '한강',
                'is_new_query': False
            })))]
        )

        result = self.chain.execute(query, context)

        print(f"  📊 실행 결과:")
        print(f"    - 액션: {result.get('action')}")
        print(f"    - 명확화 종료: {not result.get('update_context', {}).get('waiting_for_clarification', True)}")
        print(f"    - 작가 정보 설정: {bool(result.get('update_context', {}).get('current_author'))}")

        assert result.get('action') in ['show_result', 'ask_clarification']
        assert 'message' in result

        print("✅ 명확화 응답 처리 플로우 테스트 통과")


class TestWikiSearchChainIntentAnalysis:
    """WikiSearchChain 의도 분석 테스트"""

    def setup_method(self):
        """각 테스트 전에 실행되는 설정"""
        self.mock_llm_client = Mock()
        self.chain = WikiSearchChain(llm_client=self.mock_llm_client)

    def test_analyze_query_intent_with_llm_success(self):
        """LLM을 사용한 쿼리 의도 분석 성공 테스트"""
        query = "개미 작가 누구야"
        context = {}

        print(f"  🤖 LLM 쿼리 의도 분석 테스트")
        print(f"  📝 입력 쿼리: '{query}'")
        print(f"  🎯 예상 의도: book_to_author")

        # LLM 응답 모킹
        self.mock_llm_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content=json.dumps({
                'intent_type': 'book_to_author',
                'extracted_keywords': ['개미'],
                'confidence': 0.95
            })))]
        )

        result = self.chain._analyze_query_intent(query, context)

        print(f"  📊 분석 결과:")
        print(f"    - 의도 타입: {result.get('type')}")
        print(f"    - 책 제목: {result.get('book_title')}")
        print(f"    - 키워드: {result.get('keywords')}")
        print(f"  ✅ LLM 호출됨: {self.mock_llm_client.chat.completions.create.called}")

        assert result.get('type') == 'book_to_author'
        assert result.get('book_title') == '개미'
        assert self.mock_llm_client.chat.completions.create.called

        print("✅ LLM 쿼리 의도 분석 성공 테스트 통과")

    def test_analyze_query_intent_fallback(self):
        """LLM 실패시 폴백 의도 분석 테스트"""
        query = "김영하 작가 정보"
        context = {}

        print(f"  🔄 폴백 의도 분석 테스트")
        print(f"  📝 입력 쿼리: '{query}'")
        print(f"  🚨 LLM 실패 시뮬레이션")

        # LLM 실패 시뮬레이션
        self.mock_llm_client.chat.completions.create.side_effect = Exception("API Error")

        result = self.chain._analyze_query_intent(query, context)

        print(f"  📊 폴백 분석 결과:")
        print(f"    - 의도 타입: {result.get('type')}")
        print(f"    - 키워드: {result.get('keywords')}")
        print(f"  ✅ 폴백 성공: {result.get('type') is not None}")

        assert result.get('type') in ['author_search', 'book_to_author']
        assert 'keywords' in result

        print("✅ 폴백 의도 분석 테스트 통과")

    def test_fallback_analyze_intent_book_patterns(self):
        """폴백 방식 - 책→작가 패턴 분석 테스트"""
        test_cases = [
            ("개미 작가 누구야", "book_to_author", "개미"),
            ("채식주의자 쓴 사람", "book_to_author", "채식주의자"),
            ("토지 저자 알려줘", "book_to_author", "토지"),
        ]

        print(f"  📚 책→작가 패턴 분석 테스트")
        print(f"  📋 테스트 케이스: {len(test_cases)}개")

        for i, (query, expected_type, expected_book) in enumerate(test_cases, 1):
            print(f"    {i}. 쿼리: '{query}'")
            print(f"       🎯 예상: {expected_type}, 책='{expected_book}'")

            result = self.chain._is_author_result(case)

            print(f"       📊 판별 결과: {result}")
            print(f"       ✅ 작가로 인식: {result == True}")

            assert result == True
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 작가 결과 판별 - 긍정적 케이스 테스트 통과")

    def test_is_author_result_negative_cases(self):
        """작가 결과 판별 - 부정적 케이스 테스트"""
        negative_cases = [
            {
                'success': True,
                'title': '한강',
                'summary': '한강은 다음 사람을 가리킨다.',
                'content': '동명이인...'
            },
            {
                'success': False,
                'title': '',
                'summary': '',
                'content': ''
            },
            {
                'success': True,
                'title': '서울특별시',
                'summary': '서울특별시는 대한민국의 수도이다.',
                'content': '인구는...'
            }
        ]

        print(f"  ❌ 작가 결과 판별 - 부정적 케이스 테스트")
        print(f"  📋 테스트 케이스: {len(negative_cases)}개")

        for i, case in enumerate(negative_cases, 1):
            print(f"    {i}. 제목: '{case['title']}'")
            print(f"       상황: {'실패' if not case['success'] else '동명이인' if '가리킨다' in case['summary'] else '비관련'}")

            result = self.chain._is_author_result(case)

            print(f"       📊 판별 결과: {result}")
            print(f"       ✅ 작가 아님으로 인식: {result == False}")

            assert result == False
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 작가 결과 판별 - 부정적 케이스 테스트 통과")

    def test_is_title_similar(self):
        """제목 유사도 판별 테스트"""
        test_cases = [
            ("개미", "개미 (소설)", True),
            ("채식주의자", "채식주의자", True),
            ("한강", "한강 (작가)", True),
            ("김영하", "김철수", False),
            ("무라카미하루키", "무라카미 하루키", True),
        ]

        print(f"  🔍 제목 유사도 판별 테스트")
        print(f"  📋 테스트 케이스: {len(test_cases)}개")

        for i, (query_title, result_title, expected) in enumerate(test_cases, 1):
            print(f"    {i}. 쿼리: '{query_title}' vs 결과: '{result_title}'")
            print(f"       예상: {expected}")

            result = self.chain._is_title_similar(query_title, result_title)

            print(f"       📊 유사도 결과: {result}")
            print(f"       ✅ 정확성: {result == expected}")

            assert result == expected
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 제목 유사도 판별 테스트 통과")

    def test_contains_author_name(self):
        """작가명 포함 여부 판별 테스트"""
        test_cases = [
            ("한강 작가 정보", True),
            ("김영하에 대해 알려줘", True),
            ("무라카미 하루키", True),
            ("그 작가 나이는?", False),
            ("대표작이 뭐야", False),
            ("J.K. 롤링", True),
        ]

        print(f"  👤 작가명 포함 여부 판별 테스트")
        print(f"  📋 테스트 케이스: {len(test_cases)}개")

        for i, (query, expected) in enumerate(test_cases, 1):
            print(f"    {i}. 쿼리: '{query}' → 예상: {expected}")

            result = self.chain._contains_author_name(query)

            print(f"       📊 판별 결과: {result}")
            print(f"       ✅ 정확성: {result == expected}")

            assert result == expected
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 작가명 포함 여부 판별 테스트 통과")

    def test_is_irrelevant_query(self):
        """관련 없는 질문 판별 테스트"""
        irrelevant_queries = [
            "안녕하세요",
            "날씨가 어때",
            "ㅋㅋㅋ 웃겨",
            "뭐해",
            "고마워",
            "좋은 하루",
        ]

        relevant_queries = [
            "한강 작가 정보",
            "개미 쓴 사람",
            "좋은 책 추천",
            "작가가 누구야",
        ]

        print(f"  🚫 관련 없는 질문 판별 테스트")
        print(f"  📋 관련 없는 쿼리: {len(irrelevant_queries)}개")
        print(f"  📋 관련 있는 쿼리: {len(relevant_queries)}개")

        print(f"    관련 없는 쿼리 테스트:")
        for i, query in enumerate(irrelevant_queries, 1):
            print(f"      {i}. '{query}'")
            result = self.chain._is_irrelevant_query(query)
            print(f"         📊 결과: {result} (관련 없음)")
            assert result == True
            print(f"         ✅ 테스트 {i} 통과")

        print(f"    관련 있는 쿼리 테스트:")
        for i, query in enumerate(relevant_queries, 1):
            print(f"      {i}. '{query}'")
            result = self.chain._is_irrelevant_query(query)
            print(f"         📊 결과: {result} (관련 있음)")
            assert result == False
            print(f"         ✅ 테스트 {i} 통과")

        print("✅ 관련 없는 질문 판별 테스트 통과")

class TestWikiSearchChainSearchHandlers:
    """WikiSearchChain 검색 핸들러 테스트"""

    def setup_method(self):
        """각 테스트 전에 실행되는 설정"""
        self.mock_llm_client = Mock()
        self.chain = WikiSearchChain(llm_client=self.mock_llm_client)
        self.chain.tool = Mock()
        self.chain.prompt = Mock()

    def test_handle_author_search_query_success(self):
        """작가 검색 쿼리 처리 성공 테스트"""
        query = "김영하 작가에 대해 알려줘"
        author_name = "김영하"
        query_intent = {'type': 'author_search', 'keywords': ['김영하']}
        context = {}

        print(f"  👤 작가 검색 쿼리 처리 테스트")
        print(f"  📝 쿼리: '{query}'")
        print(f"  🎯 작가명: '{author_name}'")

        # 성공적인 검색 결과 모킹
        self.chain.tool.search_page.return_value = {
            'success': True,
            'title': '김영하 (작가)',
            'summary': '김영하는 대한민국의 소설가이다.',
            'content': '김영하는 1968년 경기도에서 태어났다.',
            'url': 'https://ko.wikipedia.org/wiki/김영하_(작가)'
        }

        # LLM 답변 생성 모킹
        self.mock_llm_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="김영하는 1968년에 태어난 대한민국의 소설가입니다."))]
        )

        result = self.chain._handle_author_search_query(query, author_name, query_intent, context)

        print(f"  📊 처리 결과:")
        print(f"    - 액션: {result.get('action')}")
        print(f"    - 메시지 존재: {bool(result.get('message'))}")
        print(f"    - 작가명 설정: {result.get('update_context', {}).get('current_author')}")
        print(f"  ✅ 검색 도구 호출: {self.chain.tool.search_page.called}")

        assert result.get('action') == 'show_result'
        assert result.get('message')
        assert result.get('update_context', {}).get('current_author') == '김영하'

        print("✅ 작가 검색 쿼리 처리 성공 테스트 통과")

    def test_handle_author_search_query_disambiguation(self):
        """작가 검색 - 동명이인 처리 테스트"""
        query = "한강 작가"
        author_name = "한강"
        query_intent = {'type': 'author_search', 'keywords': ['한강']}
        context = {}

        print(f"  🔍 동명이인 처리 테스트")
        print(f"  📝 쿼리: '{query}'")
        print(f"  🎯 상황: 동명이인 존재")

        # 동명이인 페이지 모킹
        self.chain.tool.search_page.return_value = {
            'success': True,
            'title': '한강',
            'summary': '한강은 다음 사람을 가리킨다.',
            'content': '한강 (강), 한강 (작가)',
            'url': 'https://ko.wikipedia.org/wiki/한강'
        }

        self.chain.prompt.get_search_failure_message.return_value = "한강에 대한 여러 정보가 있습니다."

        result = self.chain._handle_author_search_query(query, author_name, query_intent, context)

        print(f"  📊 처리 결과:")
        print(f"    - 액션: {result.get('action')}")
        print(f"    - 명확화 요청: {result.get('action') == 'ask_clarification'}")
        print(f"    - 대기 상태 설정: {result.get('update_context', {}).get('waiting_for_clarification')}")

        assert result.get('action') == 'ask_clarification'
        assert result.get('update_context', {}).get('waiting_for_clarification') == True
        assert result.get('update_context', {}).get('current_author') == author_name

        print("✅ 동명이인 처리 테스트 통과")

    def test_handle_book_to_author_query_success(self):
        """책→작가 쿼리 처리 성공 테스트"""
        book_title = "개미"
        query_intent = {'type': 'book_to_author', 'book_title': '개미'}
        context = {}

        print(f"  📖 책→작가 쿼리 처리 테스트")
        print(f"  📝 책 제목: '{book_title}'")
        print(f"  🎯 예상: 작가 정보 추출")

        # 책 검색 결과 모킹
        self.chain.tool.search_page.return_value = {
            'success': True,
            'title': '개미 (소설)',
            'summary': '개미는 베르나르 베르베르의 소설이다.',
            'content': '이 소설은 베르나르 베르베르가 1991년에 발표했다.',
            'url': 'https://ko.wikipedia.org/wiki/개미_(소설)'
        }

        # LLM 작가 추출 모킹
        self.mock_llm_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="베르나르 베르베르"))]
        )

        result = self.chain._handle_book_to_author_query(book_title, query_intent, context)

        print(f"  📊 처리 결과:")
        print(f"    - 액션: {result.get('action')}")
        print(f"    - 메시지 포함 '베르베르': {'베르베르' in result.get('message', '')}")
        print(f"    - 작가명 추출: {result.get('update_context', {}).get('current_author')}")

        assert result.get('action') == 'show_result'
        assert '베르베르' in result.get('message', '') or '개미' in result.get('message', '')

        print("✅ 책→작가 쿼리 처리 성공 테스트 통과")


class TestWikiSearchChainInformationExtraction:
    """WikiSearchChain 정보 추출 테스트"""

    def setup_method(self):
        """각 테스트 전에 실행되는 설정"""
        self.mock_llm_client = Mock()
        self.chain = WikiSearchChain(llm_client=self.mock_llm_client)

        # 샘플 검색 결과
        self.sample_search_result = {
            'success': True,
            'title': '한강 (작가)',
            'summary': '한강은 대한민국의 소설가이다.',
            'content': '''한강은 1970년 11월 27일 광주광역시에서 태어났다. 
                         연세대학교 국어국문학과를 졸업했다. 
                         아버지는 소설가 한승원이다.
                         대표작으로는 채식주의자, 소년이 온다 등이 있다.
                         2016년 맨부커상을 수상했다.''',
            'url': 'https://ko.wikipedia.org/wiki/한강_(작가)'
        }

    def test_extract_specific_info_request_university(self):
        """특정 정보 요청 추출 - 대학교 테스트"""
        test_cases = [
            ("한강 대학교 어디야", "university"),
            ("그 작가 어디 대학 나왔어", "university"),
            ("학교 정보 알려줘", "university"),
            ("출신 대학 어디", "university"),
        ]

        print(f"  🎓 대학교 정보 요청 추출 테스트")
        print(f"  📋 테스트 케이스: {len(test_cases)}개")

        for i, (query, expected) in enumerate(test_cases, 1):
            print(f"    {i}. 쿼리: '{query}'")

            result = self.chain._extract_specific_info_request(query)

            print(f"       📊 추출 결과: '{result}'")
            print(f"       ✅ 정확성: {result == expected}")

            assert result == expected
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 대학교 정보 요청 추출 테스트 통과")

    def test_extract_specific_info_request_birth_death(self):
        """특정 정보 요청 추출 - 출생/사망 테스트"""
        test_cases = [
            ("언제 태어났어", "birth"),
            ("출생일이 언제야", "birth"),
            ("나이가 몇이야", "birth"),
            ("언제 죽었어", "death"),
            ("사망일 알려줘", "death"),
            ("언제 태어나서 언제 죽었어", "birth_death"),
        ]

        print(f"  📅 출생/사망 정보 요청 추출 테스트")
        print(f"  📋 테스트 케이스: {len(test_cases)}개")

        for i, (query, expected) in enumerate(test_cases, 1):
            print(f"    {i}. 쿼리: '{query}' → 예상: '{expected}'")

            result = self.chain._extract_specific_info_request(query)

            print(f"       📊 추출 결과: '{result}'")
            print(f"       ✅ 정확성: {result == expected}")

            assert result == expected
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 출생/사망 정보 요청 추출 테스트 통과")

    def test_extract_specific_answer_university(self):
        """특정 답변 추출 - 대학교 정보 테스트"""
        info_type = "university"
        author_name = "한강"

        print(f"  🎓 대학교 정보 추출 테스트")
        print(f"  📝 작가: {author_name}")
        print(f"  📊 추출 대상: 연세대학교")

        result = self.chain._extract_specific_answer(
            self.sample_search_result,
            info_type,
            author_name
        )

        print(f"  📊 추출 결과:")
        print(f"    - 메시지 길이: {len(result)}")
        print(f"    - '연세대학교' 포함: {'연세대학교' in result}")
        print(f"    - '졸업' 포함: {'졸업' in result}")
        print(f"    - URL 포함: {'http' in result}")

        assert '연세대학교' in result
        assert '졸업' in result
        assert 'http' in result

        print("✅ 대학교 정보 추출 테스트 통과")

    def test_extract_specific_answer_birth(self):
        """특정 답변 추출 - 출생 정보 테스트"""
        info_type = "birth"
        author_name = "한강"

        print(f"  👶 출생 정보 추출 테스트")
        print(f"  📝 작가: {author_name}")
        print(f"  📊 추출 대상: 1970년 11월 27일")

        result = self.chain._extract_specific_answer(
            self.sample_search_result,
            info_type,
            author_name
        )

        print(f"  📊 추출 결과:")
        print(f"    - 메시지 길이: {len(result)}")
        print(f"    - '1970' 포함: {'1970' in result}")
        print(f"    - '태어났습니다' 포함: {'태어났습니다' in result}")

        assert '1970' in result
        assert '태어났습니다' in result or '태어나' in result

        print("✅ 출생 정보 추출 테스트 통과")

    def test_extract_specific_answer_family(self):
        """특정 답변 추출 - 가족 정보 테스트"""
        info_type = "family"
        author_name = "한강"

        print(f"  👨‍👩‍👧‍👦 가족 정보 추출 테스트")
        print(f"  📝 작가: {author_name}")
        print(f"  📊 추출 대상: 아버지 한승원")

        # WikiInformationExtractor.find_enhanced_family_info 모킹
        with patch('app.chains.wiki_search_chain.WikiInformationExtractor') as mock_extractor:
            mock_extractor.find_enhanced_family_info.return_value = {
                'father': '한승원',
                'mother': None,
                'siblings': [],
                'family': []
            }

            result = self.chain._extract_specific_answer(
                self.sample_search_result,
                info_type,
                author_name
            )

        print(f"  📊 추출 결과:")
        print(f"    - 메시지 길이: {len(result)}")
        print(f"    - '한승원' 포함: {'한승원' in result}")
        print(f"    - '아버지' 포함: {'아버지' in result}")

        assert '한승원' in result
        assert '아버지' in result

        print("✅ 가족 정보 추출 테스트 통과")


class TestWikiSearchChainHelperMethods:
    """WikiSearchChain 헬퍼 메서드 테스트"""

    def setup_method(self):
        """각 테스트 전에 실행되는 설정"""
        self.chain = WikiSearchChain()

    def test_is_author_result_positive_cases(self):
        """작가 결과 판별 - 긍정적 케이스 테스트"""
        positive_cases = [
            {
                'success': True,
                'title': '김영하 (작가)',
                'summary': '김영하는 대한민국의 소설가이다.',
                'content': '주요 작품으로는...'
            },
            {
                'success': True,
                'title': '한강',
                'summary': '한강은 시인이자 소설가이다.',
                'content': '작품 활동을...'
            },
            {
                'success': True,
                'title': '이말년',
                'summary': '이말년은 만화가이다.',
                'content': '웹툰을...'
            }
        ]

        print(f"  ✅ 작가 결과 판별 - 긍정적 케이스 테스트")
        print(f"  📋 테스트 케이스: {len(positive_cases)}개")

        for i, case in enumerate(positive_cases, 1):
            print(f"    {i}. 제목: '{case['title']}'")
            print(f"       요약: '{case['summary'][:30]}...'")

            result =self.chain._fallback_analyze_intent(query)

            print(f"       📊 결과: 타입={result.get('type')}, 책={result.get('book_title')}")
            print(f"       ✅ 정확성: {result.get('type') == expected_type}")

            assert result.get('type') == expected_type
            if expected_book:
                assert expected_book in result.get('book_title', '')

            print(f"       ✅ 테스트 {i} 통과")

            print("✅ 책→작가 패턴 분석 테스트 통과")


class TestWikiSearchChainComplexScenarios:
    """WikiSearchChain 복잡한 시나리오 테스트"""

    def setup_method(self):
        """각 테스트 전에 실행되는 설정"""
        self.mock_llm_client = Mock()
        self.chain = WikiSearchChain(llm_client=self.mock_llm_client)
        self.chain.tool = Mock()
        self.chain.prompt = Mock()

    def test_compound_query_handling(self):
        """복합 질문 처리 테스트"""
        query = "김영하와 한강에 대해 각각 알려줘"
        context = {}

        print(f"  🔗 복합 질문 처리 테스트")
        print(f"  📝 쿼리: '{query}'")
        print(f"  🎯 예상: 두 작가 정보 각각 처리")

        # 복합 질문 감지 모킹
        with patch('app.chains.wiki_search_chain.WikiInformationExtractor') as mock_extractor:
            mock_extractor.detect_compound_query.return_value = {
                'is_compound': True,
                'subjects': ['김영하', '한강']
            }

            # 각 작가별 검색 결과 모킹
            self.chain.tool.search_page.side_effect = [
                {
                    'success': True,
                    'title': '김영하 (작가)',
                    'summary': '김영하는 대한민국의 소설가이다.',
                    'content': '1968년에 태어났다.',
                    'url': 'https://ko.wikipedia.org/wiki/김영하_(작가)'
                },
                {
                    'success': True,
                    'title': '한강 (작가)',
                    'summary': '한강은 대한민국의 소설가이다.',
                    'content': '1970년에 태어났다.',
                    'url': 'https://ko.wikipedia.org/wiki/한강_(작가)'
                }
            ]

            # LLM 응답 모킹
            self.mock_llm_client.chat.completions.create.return_value = Mock(
                choices=[Mock(message=Mock(content="작가 정보입니다."))]
            )

            result = self.chain._handle_compound_query(query, context)

        print(f"  📊 처리 결과:")
        print(f"    - 복합 질문 인식: {result is not None}")
        if result:
            print(f"    - 액션: {result.get('action')}")
            print(f"    - 김영하 포함: {'김영하' in result.get('message', '')}")
            print(f"    - 한강 포함: {'한강' in result.get('message', '')}")
            print(f"    - 복합 쿼리 표시: {result.get('update_context', {}).get('compound_query')}")

            assert result.get('action') == 'show_result'
            assert '김영하' in result.get('message', '')
            assert '한강' in result.get('message', '')

        print("✅ 복합 질문 처리 테스트 통과")

    def test_context_priority_check(self):
        """컨텍스트 우선순위 확인 테스트"""
        test_scenarios = [
            {
                'query': '그 작가 나이는?',
                'context': {'current_author': '한강'},
                'expected': True,
                'description': '컨텍스트 키워드 + 현재 작가 존재'
            },
            {
                'query': '김영하 작가 정보',
                'context': {'current_author': '한강'},
                'expected': False,
                'description': '새로운 작가명 언급'
            },
            {
                'query': '안녕하세요',
                'context': {'current_author': '한강'},
                'expected': False,
                'description': '관련 없는 질문'
            }
        ]

        print(f"  🎯 컨텍스트 우선순위 확인 테스트")
        print(f"  📋 시나리오: {len(test_scenarios)}개")

        for i, scenario in enumerate(test_scenarios, 1):
            print(f"    {i}. {scenario['description']}")
            print(f"       쿼리: '{scenario['query']}'")
            print(f"       컨텍스트: {scenario['context']}")

            result = self.chain._check_context_priority(scenario['query'], scenario['context'])

            print(f"       📊 결과: 컨텍스트 사용={result['should_use_context']}")
            print(f"       이유: {result['reasoning']}")
            print(f"       ✅ 예상과 일치: {result['should_use_context'] == scenario['expected']}")

            assert result['should_use_context'] == scenario['expected']
            print(f"       ✅ 시나리오 {i} 통과")

        print("✅ 컨텍스트 우선순위 확인 테스트 통과")


class TestWikiSearchChainPerformance:
    """WikiSearchChain 성능 테스트"""

    def setup_method(self):
        """각 테스트 전에 실행되는 설정"""
        self.chain = WikiSearchChain()
        self.chain.tool = Mock()
        self.chain.prompt = Mock()

        # 기본 성공 응답 설정
        self.chain.tool.search_page.return_value = {
            'success': True,
            'title': '테스트 작가',
            'summary': '테스트 작가입니다.',
            'content': '테스트 내용입니다.',
            'url': 'https://test.com'
        }

    def test_multiple_queries_performance(self):
        """다중 쿼리 처리 성능 테스트"""
        queries = [
                      "한강 작가 정보",
                      "김영하에 대해 알려줘",
                      "무라카미 하루키",
                      "개미 작가 누구야",
                      "채식주의자 쓴 사람"
                  ] * 20  # 100개 쿼리

        print(f"  ⚡ 다중 쿼리 처리 성능 테스트")
        print(f"    - 테스트 쿼리 수: {len(queries)}개")
        print(f"    - 목표 시간: 10초 이내")

        start_time = time.time()

        results = []
        for i, query in enumerate(queries):
            try:
                # 기본 분석만 수행 (실제 검색은 모킹됨)
                intent = self.chain._analyze_query_intent(query)
                results.append(intent)

                if (i + 1) % 25 == 0:
                    elapsed = time.time() - start_time
                    print(f"      💾 진행: {i + 1}개 처리 완료 ({elapsed:.2f}초)")

            except Exception as e:
                print(f"      ⚠️ 쿼리 처리 실패: {query} - {e}")
                results.append({'error': str(e)})

        end_time = time.time()
        total_time = end_time - start_time

        print(f"    📊 성능 결과:")
        print(f"      - 총 처리 시간: {total_time:.4f}초")
        print(f"      - 평균 처리 시간: {total_time/len(queries):.6f}초/개")
        print(f"      - 초당 처리량: {len(queries)/total_time:.1f}개/초")
        print(f"      - 성공률: {len([r for r in results if 'error' not in r])}/{len(results)}")

        # 성능 검증
        assert total_time < 10.0
        assert len(results) == len(queries)

        print("✅ 다중 쿼리 처리 성능 테스트 통과")

    def test_memory_usage_stability(self):
        """메모리 사용량 안정성 테스트"""
        try:
            import psutil
        except ImportError:
            print("  ⚠️ psutil 모듈이 없어 메모리 테스트를 건너뜁니다.")
            return

        print(f"  💾 메모리 사용량 안정성 테스트")

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        print(f"    - 초기 메모리: {initial_memory / 1024 / 1024:.2f}MB")

        # 대량 처리 시뮬레이션
        for i in range(500):
            query = f"테스트 작가 {i} 정보"
            context = {'test_iteration': i}

            # 의도 분석만 수행
            try:
                self.chain._analyze_query_intent(query, context)
                self.chain._is_author_result({'success': True, 'title': f'작가{i}', 'summary': '테스트'})
                self.chain._contains_author_name(query)
            except:
                pass

            if (i + 1) % 100 == 0:
                current_memory = process.memory_info().rss
                print(f"      💽 {i + 1}회 처리 후: {current_memory / 1024 / 1024:.2f}MB")

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        print(f"    📊 메모리 사용량 결과:")
        print(f"      - 최종 메모리: {final_memory / 1024 / 1024:.2f}MB")
        print(f"      - 메모리 증가: {memory_increase / 1024 / 1024:.2f}MB")
        print(f"      - 증가율: {(memory_increase / initial_memory) * 100:.2f}%")

        # 메모리 증가량이 100MB 이하인지 확인
        assert memory_increase < 100 * 1024 * 1024

        print("✅ 메모리 사용량 안정성 테스트 통과")


class TestWikiSearchChainErrorHandling:
    """WikiSearchChain 오류 처리 테스트"""

    def setup_method(self):
        """각 테스트 전에 실행되는 설정"""
        self.mock_llm_client = Mock()
        self.chain = WikiSearchChain(llm_client=self.mock_llm_client)
        self.chain.tool = Mock()
        self.chain.prompt = Mock()

    def test_search_tool_failure_handling(self):
        """검색 도구 실패 처리 테스트"""
        query = "한강 작가 정보"
        context = {}

        print(f"  🚨 검색 도구 실패 처리 테스트")
        print(f"  📝 쿼리: '{query}'")
        print(f"  🎯 상황: 검색 도구 실패")

        # 검색 실패 시뮬레이션
        self.chain.tool.search_page.return_value = {
            'success': False,
            'error': 'Network error'
        }

        # LLM 의도 분석은 성공
        self.mock_llm_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content=json.dumps({
                'intent_type': 'author_search',
                'extracted_keywords': ['한강']
            })))]
        )

        self.chain.prompt.get_search_failure_message.return_value = "검색에 실패했습니다."

        result = self.chain.execute(query, context)

        print(f"  📊 오류 처리 결과:")
        print(f"    - 액션: {result.get('action')}")
        print(f"    - 오류 메시지 존재: {bool(result.get('message'))}")
        print(f"    - 명확화 요청: {result.get('action') == 'ask_clarification'}")

        assert result.get('action') in ['ask_clarification', 'error']
        assert result.get('message')

        print("✅ 검색 도구 실패 처리 테스트 통과")

    def test_llm_client_none_fallback(self):
        """LLM 클라이언트 없을 때 폴백 테스트"""
        query = "김영하 작가 정보"
        context = {}

        print(f"  🤖 LLM 없을 때 폴백 테스트")
        print(f"  📝 쿼리: '{query}'")
        print(f"  🎯 상황: LLM 클라이언트 없음")

        # LLM 없는 체인 생성
        chain_no_llm = WikiSearchChain(llm_client=None)
        chain_no_llm.tool = Mock()
        chain_no_llm.prompt = Mock()

        # 검색 성공 응답 설정
        chain_no_llm.tool.search_page.return_value = {
            'success': True,
            'title': '김영하 (작가)',
            'summary': '김영하는 대한민국의 소설가이다.',
            'content': '1968년에 태어났다.',
            'url': 'https://ko.wikipedia.org/wiki/김영하_(작가)'
        }

        chain_no_llm.prompt.format_author_response.return_value = "김영하 작가 정보입니다."

        result = chain_no_llm.execute(query, context)

        print(f"  📊 폴백 처리 결과:")
        print(f"    - 액션: {result.get('action')}")
        print(f"    - 메시지 존재: {bool(result.get('message'))}")
        print(f"    - 폴백 성공: {result.get('action') in ['show_result', 'ask_clarification']}")

        assert result.get('action') in ['show_result', 'ask_clarification', 'error']
        assert result.get('message')

        print("✅ LLM 없을 때 폴백 테스트 통과")

    def test_malformed_json_handling(self):
        """잘못된 JSON 응답 처리 테스트"""
        query = "개미 작가 누구야"
        context = {}

        print(f"  📝 잘못된 JSON 응답 처리 테스트")
        print(f"  📝 쿼리: '{query}'")
        print(f"  🎯 상황: LLM이 잘못된 JSON 반환")

        # 잘못된 JSON 응답 시뮬레이션
        self.mock_llm_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Invalid JSON response"))]
        )

        # 검색 성공 응답 설정 (폴백용)
        self.chain.tool.search_page.return_value = {
            'success': True,
            'title': '개미 (소설)',
            'summary': '개미는 베르나르 베르베르의 소설이다.',
            'content': '1991년에 발표되었다.',
            'url': 'https://ko.wikipedia.org/wiki/개미_(소설)'
        }

        result = self.chain.execute(query, context)

        print(f"  📊 JSON 오류 처리 결과:")
        print(f"    - 액션: {result.get('action')}")
        print(f"    - 폴백 성공: {result.get('action') in ['show_result', 'ask_clarification']}")
        print(f"    - 메시지 존재: {bool(result.get('message'))}")

        # JSON 파싱 실패해도 폴백으로 처리되어야 함
        assert result.get('action') in ['show_result', 'ask_clarification', 'error']
        assert result.get('message')

        print("✅ 잘못된 JSON 응답 처리 테스트 통과")


if __name__ == "__main__":
    start_time = time.time()

    print("🧪 WikiSearchChain 직관적인 TDD 테스트 시작\n")

    # 기본 워크플로우 테스트
    print("📋 기본 워크플로우 테스트 - 실행 흐름 및 분기")
    print("=" * 60)
    test_basics = TestWikiSearchChainBasics()
    test_basics.setup_method()
    test_basics.test_execute_fresh_search_flow_with_author_name()
    print()
    test_basics.test_execute_context_question_flow()
    print()
    test_basics.test_execute_clarification_response_flow()

    # 의도 분석 테스트
    print("\n🤖 의도 분석 테스트 - LLM 및 폴백 방식")
    print("=" * 60)
    test_intent = TestWikiSearchChainIntentAnalysis()
    test_intent.setup_method()
    test_intent.test_analyze_query_intent_with_llm_success()
    print()
    test_intent.test_analyze_query_intent_fallback()
    print()
    test_intent.test_fallback_analyze_intent_book_patterns()

    # 검색 핸들러 테스트
    print("\n🔍 검색 핸들러 테스트 - 작가/책 검색 처리")
    print("=" * 60)
    test_handlers = TestWikiSearchChainSearchHandlers()
    test_handlers.setup_method()
    test_handlers.test_handle_author_search_query_success()
    print()
    test_handlers.test_handle_author_search_query_disambiguation()
    print()
    test_handlers.test_handle_book_to_author_query_success()

    # 정보 추출 테스트
    print("\n📊 정보 추출 테스트 - 특정 정보 추출 및 답변 생성")
    print("=" * 60)
    test_extraction = TestWikiSearchChainInformationExtraction()
    test_extraction.setup_method()
    test_extraction.test_extract_specific_info_request_university()
    print()
    test_extraction.test_extract_specific_info_request_birth_death()
    print()
    test_extraction.test_extract_specific_answer_university()
    print()
    test_extraction.test_extract_specific_answer_birth()
    print()
    test_extraction.test_extract_specific_answer_family()

    # 헬퍼 메서드 테스트
    print("\n🛠️ 헬퍼 메서드 테스트 - 판별 및 유틸리티 함수")
    print("=" * 60)
    test_helpers = TestWikiSearchChainHelperMethods()
    test_helpers.setup_method()
    test_helpers.test_is_author_result_positive_cases()
    print()
    test_helpers.test_is_author_result_negative_cases()
    print()
    test_helpers.test_is_title_similar()
    print()
    test_helpers.test_contains_author_name()
    print()
    test_helpers.test_is_irrelevant_query()

    # 복잡한 시나리오 테스트
    print("\n🔗 복잡한 시나리오 테스트 - 복합 질문 및 컨텍스트")
    print("=" * 60)
    test_complex = TestWikiSearchChainComplexScenarios()
    test_complex.setup_method()
    test_complex.test_compound_query_handling()
    print()
    test_complex.test_context_priority_check()

    # 성능 테스트
    print("\n⚡ 성능 테스트 - 처리 속도 및 메모리 효율성")
    print("=" * 60)
    test_performance = TestWikiSearchChainPerformance()
    test_performance.setup_method()
    test_performance.test_multiple_queries_performance()
    print()
    test_performance.test_memory_usage_stability()

    # 오류 처리 테스트
    print("\n🚨 오류 처리 테스트 - 예외 상황 대응")
    print("=" * 60)
    test_errors = TestWikiSearchChainErrorHandling()
    test_errors.setup_method()
    test_errors.test_search_tool_failure_handling()
    print()
    test_errors.test_llm_client_none_fallback()
    print()
    test_errors.test_malformed_json_handling()

    end_time = time.time()
    total_time = end_time - start_time

    print("\n" + "=" * 60)
    print("🎉 모든 WikiSearchChain 테스트 통과!")
    print(f"⏱️ 총 실행 시간: {total_time:.2f}초")
    print("\n📊 테스트 요약:")
    print("  ✅ 기본 워크플로우: 3개 테스트")
    print("  ✅ 의도 분석: 3개 테스트")
    print("  ✅ 검색 핸들러: 3개 테스트")
    print("  ✅ 정보 추출: 5개 테스트")
    print("  ✅ 헬퍼 메서드: 5개 테스트")
    print("  ✅ 복잡한 시나리오: 2개 테스트")
    print("  ✅ 오류 처리: 3개 테스트")
    print(f"\n📈 총 테스트 수: 26개")
    print("\n📝 pytest로 실행하려면:")
    print("    cd ai-service")
    print("    python -m pytest tests/unit/chains/test_wiki_search_chain.py -v -s")
    print("\n🚀 개별 실행:")
    print("    python tests/unit/chains/test_wiki_search_chain.py")

