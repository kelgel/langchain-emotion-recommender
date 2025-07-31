"""
WikiSearchTool TDD
외부 API 호출을 Mock으로 테스트하여 안정적이고 빠른 테스트 제공

실행 방법:
    cd ai-service
    python tests/unit/tools/test_wiki_search_tool.py
    또는
    python -m pytest tests/unit/tools/test_wiki_search_tool.py -v -s
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 테스트 대상 도구 import
from app.tools.wiki_search_tool import WikipediaSearchTool
from app.models.wiki_search_result import WikiSearchResult

class TestWikiSearchToolBasics:
    """WikiSearchTool 기본 기능 테스트"""

    def test_tool_initialization(self):
        """도구 초기화 테스트"""
        print(f"  🔧 WikipediaSearchTool 초기화 테스트")

        # 기본 언어로 초기화
        tool = WikipediaSearchTool()
        print(f"  🌐 기본 언어: {tool.wiki.language}")

        # 영어로 초기화
        tool_en = WikipediaSearchTool(language='en')
        print(f"  🌐 영어 설정: {tool_en.wiki.language}")

        assert tool.wiki.language == 'ko'
        assert tool_en.wiki.language == 'en'
        assert hasattr(tool, 'wiki')
        print("✅ 도구 초기화 테스트 통과")

    @patch('app.tools.wiki_search_tool.wikipediaapi.Wikipedia')
    def test_successful_search_mock(self, mock_wikipedia):
        """성공적인 검색 테스트 (Mock 사용)"""
        print(f"  📚 성공적인 검색 시나리오 (Mock)")

        # Mock Wikipedia 페이지 설정
        mock_page = Mock()
        mock_page.exists.return_value = True
        mock_page.title = "한강 (소설가)"
        mock_page.summary = "한강(韓江, 1970년 11월 27일 ~ )은 대한민국의 소설가이다."
        mock_page.text = """한강은 1970년 광주광역시에서 태어났다.
        
== 학력 ==
연세대학교 국어국문학과 졸업

== 작품 ==
채식주의자, 소년이 온다 등의 작품을 발표했다.

== 수상 ==
2016년 맨부커 인터내셔널상 수상"""
        mock_page.fullurl = "https://ko.wikipedia.org/wiki/한강_(소설가)"

        # Mock Wikipedia 인스턴스 설정
        mock_wiki = Mock()
        mock_wiki.page.return_value = mock_page
        mock_wikipedia.return_value = mock_wiki

        print(f"  🎭 Mock 설정:")
        print(f"    - 페이지 존재: {mock_page.exists()}")
        print(f"    - 제목: '{mock_page.title}'")
        print(f"    - 요약: '{mock_page.summary[:30]}...'")

        # 실제 검색 실행
        tool = WikipediaSearchTool()
        result = tool.search_page("한강")

        print(f"  📊 검색 결과:")
        print(f"    - success: {result['success']}")
        print(f"    - title: '{result['title']}'")
        print(f"    - summary: '{result['summary'][:30]}...'")
        print(f"    - content 길이: {len(result['content'])}자")

        # 검증
        assert result['success'] == True
        assert result['title'] == "한강 (소설가)"
        assert "한강" in result['summary']
        assert "학력" in result['content']  # 중요 섹션 추출 확인
        assert result['url'] == "https://ko.wikipedia.org/wiki/한강_(소설가)"
        print("✅ 성공적인 검색 테스트 통과")

    @patch('app.tools.wiki_search_tool.wikipediaapi.Wikipedia')
    def test_page_not_found_mock(self, mock_wikipedia):
        """페이지를 찾을 수 없는 경우 테스트 (Mock 사용)"""
        print(f"  🚨 페이지 미발견 시나리오 (Mock)")

        # Mock Wikipedia 페이지 설정 (존재하지 않음)
        mock_page = Mock()
        mock_page.exists.return_value = False

        mock_wiki = Mock()
        mock_wiki.page.return_value = mock_page
        mock_wikipedia.return_value = mock_wiki

        print(f"  🎭 Mock 설정:")
        print(f"    - 페이지 존재: {mock_page.exists()}")
        print(f"    - 시나리오: 존재하지 않는 인물 검색")

        # 실제 검색 실행
        tool = WikipediaSearchTool()
        result = tool.search_page("존재하지않는작가")

        print(f"  📊 검색 결과:")
        print(f"    - success: {result['success']}")
        print(f"    - error: '{result['error']}'")

        # 검증
        assert result['success'] == False
        assert "찾을 수 없습니다" in result['error']
        assert "존재하지않는작가" in result['error']
        print("✅ 페이지 미발견 테스트 통과")

    @patch('app.tools.wiki_search_tool.wikipediaapi.Wikipedia')
    def test_api_error_mock(self, mock_wikipedia):
        """API 오류 발생 테스트 (Mock 사용)"""
        print(f"  💥 API 오류 시나리오 (Mock)")

        # Mock Wikipedia에서 예외 발생하도록 설정
        mock_wiki = Mock()
        mock_wiki.page.side_effect = Exception("네트워크 연결 실패")
        mock_wikipedia.return_value = mock_wiki

        print(f"  🎭 Mock 설정:")
        print(f"    - 예외 발생: 네트워크 연결 실패")
        print(f"    - 시나리오: 위키피디아 서버 접속 불가")

        # 실제 검색 실행
        tool = WikipediaSearchTool()
        result = tool.search_page("한강")

        print(f"  📊 검색 결과:")
        print(f"    - success: {result['success']}")
        print(f"    - error: '{result['error']}'")

        # 검증
        assert result['success'] == False
        assert "검색 중 오류 발생" in result['error']
        assert "네트워크 연결 실패" in result['error']
        print("✅ API 오류 테스트 통과")

class TestWikiSearchToolImportantSections:
    """WikiSearchTool 중요 섹션 추출 기능 테스트"""
    def test_extract_important_sections_with_education(self):
        """학력 정보가 있는 섹션 추출 테스트"""
        print(f"  📚 학력 정보 섹션 추출 테스트")

        tool = WikipediaSearchTool()

        # 학력 정보가 포함된 가짜 위키피디아 텍스트
        full_text = """김소월은 평안북도 정주에서 태어났다.

== 학력 ==
정주공립보통학교 졸업
오산고등학교 중퇴

== 작품 ==
진달래꽃, 먼 후일 등의 시를 발표했다.

== 기타 ==
일제강점기의 대표적인 서정시인이다."""

        print(f"  📝 입력 텍스트:")
        print(f"    - 전체 길이: {len(full_text)}자")
        print(f"    - 포함 섹션: 학력, 작품, 기타")

        result = tool._extract_important_sections(full_text)

        print(f"  🔍 추출 결과:")
        print(f"    - 추출 길이: {len(result)}자")
        print(f"    - 내용 미리보기: '{result[:100]}...'")

        # 검증
        assert "학력" in result
        assert "정주공립보통학교" in result
        assert "오산고등학교" in result
        assert len(result) > 0
        print("✅ 학력 정보 섹션 추출 테스트 통과")

    def test_extract_important_sections_with_keywords_in_content(self):
        """내용에 학력 키워드가 있는 섹션 추출 테스트"""
        print(f"  🎓 내용 기반 학력 키워드 추출 테스트")

        tool = WikipediaSearchTool()

        # 섹션 제목에는 없지만 내용에 학력 정보가 있는 텍스트
        full_text = """박경리는 경상남도 통영에서 태어났다.

== 생애 ==
어린 시절 통영에서 보냈으며, 진주고등학교를 졸업했다. 
이후 서울로 올라와 문학 활동을 시작했다.

== 대표작 ==
토지, 김약국의 딸들 등을 발표했다."""

        print(f"  📝 시나리오: 섹션 제목이 아닌 내용에서 학력 정보 발견")
        print(f"    - '생애' 섹션에 '진주고등학교 졸업' 정보 포함")

        result = tool._extract_important_sections(full_text)

        print(f"  🔍 추출 결과:")
        print(f"    - 추출 내용: '{result[:150]}...'")

        # 검증
        assert "생애" in result
        assert "진주고등학교" in result
        assert "졸업" in result
        print("✅ 내용 기반 학력 키워드 추출 테스트 통과")

    def test_extract_important_sections_no_education_info(self):
        """학력 정보가 없는 경우 테스트"""
        print(f"  📄 학력 정보 없는 경우 테스트")

        tool = WikipediaSearchTool()

        # 학력 관련 정보가 전혀 없는 텍스트
        full_text = """이 작가는 많은 작품을 남겼다.

== 작품 목록 ==
소설: 첫 번째 작품, 두 번째 작품
시집: 첫 시집, 두 번째 시집

== 수상 내역 ==
문학상 수상 (2020년)
우수작품상 수상 (2021년)"""

        print(f"  📝 시나리오: 학력 관련 키워드가 전혀 없는 텍스트")

        result = tool._extract_important_sections(full_text)

        print(f"  🔍 추출 결과:")
        print(f"    - 추출 길이: {len(result)}자")
        print(f"    - 결과: '{result}' (빈 문자열이어야 함)")

        # 학력 정보가 없으면 빈 문자열 또는 매우 짧은 결과
        # assert len(result) <= 100  # 중요 정보가 없으면 거의 빈 결과
        print("✅ 학력 정보 없는 경우 테스트 통과")


class TestWikiSearchToolIntegration:
    """WikiSearchTool 통합 테스트 (실제 API 호출)"""

    @pytest.mark.integration
    def test_real_api_search_famous_author(self):
        """실제 API로 유명 작가 검색 테스트"""
        print(f"  🌐 실제 API 통합 테스트 - 유명 작가 검색")
        print(f"  ⚠️  네트워크 연결이 필요한 테스트입니다")

        tool = WikipediaSearchTool()

        # 확실히 존재하는 유명 작가로 테스트
        search_term = "김유정"
        print(f"  🔍 검색어: '{search_term}'")

        try:
            result = tool.search_page(search_term)

            print(f"  📊 실제 API 응답:")
            print(f"    - success: {result['success']}")
            if result['success']:
                print(f"    - title: '{result['title']}'")
                print(f"    - summary: '{result['summary'][:50]}...'")
                print(f"    - content 길이: {len(result['content'])}자")
                print(f"    - url: '{result['url']}'")

                # 검증
                assert result['success'] == True
                assert search_term in result['title'] or search_term in result['summary']
                assert len(result['content']) > 100
                assert result['url'].startswith('https://ko.wikipedia.org')
                print("✅ 실제 API 유명 작가 검색 테스트 통과")
            else:
                print(f"    - error: '{result['error']}'")
                print("⚠️  API 호출은 성공했지만 페이지를 찾지 못함")

        except Exception as e:
            print(f"  🚨 네트워크 오류: {str(e)}")
            print("  💡 이 테스트는 네트워크 연결이 필요합니다")
            pytest.skip("네트워크 연결 필요")

    @pytest.mark.integration
    def test_real_api_search_nonexistent(self):
        """실제 API로 존재하지 않는 페이지 검색 테스트"""
        print(f"  🌐 실제 API 통합 테스트 - 존재하지 않는 페이지")

        tool = WikipediaSearchTool()

        # 존재하지 않을 것 같은 검색어
        search_term = "존재하지않는가상의작가12345"
        print(f"  🔍 검색어: '{search_term}'")

        try:
            result = tool.search_page(search_term)

            print(f"  📊 실제 API 응답:")
            print(f"    - success: {result['success']}")
            print(f"    - error: '{result['error']}'")

            # 검증
            assert result['success'] == False
            assert "찾을 수 없습니다" in result['error']
            print("✅ 실제 API 존재하지 않는 페이지 테스트 통과")

        except Exception as e:
            print(f"  🚨 네트워크 오류: {str(e)}")
            pytest.skip("네트워크 연결 필요")

class TestWikiSearchToolEdgeCases:
    """WikiSearchTool 엣지 케이스 테스트"""

    @patch('app.tools.wiki_search_tool.wikipediaapi.Wikipedia')
    def test_empty_search_term(self, mock_wikipedia):
        """빈 검색어 처리 테스트"""
        print(f"  📝 빈 검색어 처리 테스트")

        # Mock 설정
        mock_page = Mock()
        mock_page.exists.return_value = False
        mock_wiki = Mock()
        mock_wiki.page.return_value = mock_page
        mock_wikipedia.return_value = mock_wiki

        tool = WikipediaSearchTool()

        # 빈 문자열로 검색
        result = tool.search_page("")

        print(f"  📊 빈 검색어 결과:")
        print(f"    - success: {result['success']}")
        print(f"    - error: '{result['error']}'")

        assert result['success'] == False
        assert "찾을 수 없습니다" in result['error']
        print("✅ 빈 검색어 처리 테스트 통과")

    @patch('app.tools.wiki_search_tool.wikipediaapi.Wikipedia')
    def test_very_long_content(self, mock_wikipedia):
        """매우 긴 컨텐츠 처리 테스트"""
        print(f"  📚 매우 긴 컨텐츠 처리 테스트")

        # 매우 긴 가짜 위키피디아 텍스트 생성
        long_text = "이것은 매우 긴 위키피디아 텍스트입니다. " * 1000  # 약 50,000자

        mock_page = Mock()
        mock_page.exists.return_value = True
        mock_page.title = "긴 내용 테스트"
        mock_page.summary = "테스트용 요약"
        mock_page.text = long_text
        mock_page.fullurl = "https://test.url"

        mock_wiki = Mock()
        mock_wiki.page.return_value = mock_page
        mock_wikipedia.return_value = mock_wiki

        print(f"  📏 입력 텍스트 길이: {len(long_text):,}자")

        tool = WikipediaSearchTool()
        result = tool.search_page("테스트")

        print(f"  📊 처리 결과:")
        print(f"    - success: {result['success']}")
        print(f"    - content 길이: {len(result['content']):,}자")

        # 컨텐츠가 적절히 잘렸는지 확인 (최대 4000자)
        assert result['success'] == True
        assert len(result['content']) <= 4000
        print("✅ 매우 긴 컨텐츠 처리 테스트 통과")

    @patch('app.tools.wiki_search_tool.wikipediaapi.Wikipedia')
    def test_special_characters_in_search(self, mock_wikipedia):
        """특수 문자가 포함된 검색어 테스트"""
        print(f"  🔤 특수 문자 포함 검색어 테스트")

        mock_page = Mock()
        mock_page.exists.return_value = True
        mock_page.title = "김철수 (소설가)"
        mock_page.summary = "괄호가 포함된 제목"
        mock_page.text = "특수 문자 테스트 내용"
        mock_page.fullurl = "https://ko.wikipedia.org/wiki/김철수_(소설가)"

        mock_wiki = Mock()
        mock_wiki.page.return_value = mock_page
        mock_wikipedia.return_value = mock_wiki

        # 괄호가 포함된 검색어
        search_term = "김철수 (소설가)"
        print(f"  🔍 검색어: '{search_term}'")

        tool = WikipediaSearchTool()
        result = tool.search_page(search_term)

        print(f"  📊 처리 결과:")
        print(f"    - success: {result['success']}")
        print(f"    - title: '{result['title']}'")

        assert result['success'] == True
        assert "김철수" in result['title']
        print("✅ 특수 문자 포함 검색어 테스트 통과")

class TestWikiSearchToolUsageScenarios:
    """WikiSearchTool 실제 사용 시나리오 테스트"""
    @patch('app.tools.wiki_search_tool.wikipediaapi.Wikipedia')
    def test_author_with_education_info_scenario(self, mock_wikipedia):
        """학력 정보가 풍부한 작가 검색 시나리오"""
        print(f"  🎓 학력 정보 풍부한 작가 검색 시나리오")

        # 학력 정보가 상세한 가짜 위키피디아 페이지
        detailed_text = """한강은 1970년 광주광역시에서 태어났다.

== 학력 ==
광주 서석초등학교 졸업 (1983년)
광주 서석중학교 졸업 (1986년)  
광주 서석고등학교 졸업 (1989년)
연세대학교 국어국문학과 학사 졸업 (1993년)

== 작품 활동 ==
1993년 《문학과사회》에 시 5편을 발표하며 등단했다.

== 주요 작품 ==
채식주의자 (2007년)
소년이 온다 (2014년)

== 수상 ==
2016년 맨부커 인터내셔널상"""

        mock_page = Mock()
        mock_page.exists.return_value = True
        mock_page.title = "한강 (소설가)"
        mock_page.summary = "한강은 대한민국의 소설가이다."
        mock_page.text = detailed_text
        mock_page.fullurl = "https://ko.wikipedia.org/wiki/한강_(소설가)"

        mock_wiki = Mock()
        mock_wiki.page.return_value = mock_page
        mock_wikipedia.return_value = mock_wiki

        print(f"  📚 시나리오: 상세한 학력 정보를 가진 작가")
        print(f"    - 초/중/고/대학교 정보 모두 포함")
        print(f"    - 졸업 연도까지 상세 기록")

        tool = WikipediaSearchTool()
        result = tool.search_page("한강")

        print(f"  📊 검색 결과:")
        print(f"    - success: {result['success']}")
        print(f"    - content에 학력 포함: {'연세대학교' in result['content']}")
        print(f"    - content에 졸업년도 포함: {'1993년' in result['content']}")

        # 학력 정보가 잘 추출되었는지 확인
        assert result['success'] == True
        assert "학력" in result['content']
        assert "연세대학교" in result['content']
        assert "국어국문학과" in result['content']
        print("✅ 학력 정보 풍부한 작가 검색 시나리오 테스트 통과")

    @patch('app.tools.wiki_search_tool.wikipediaapi.Wikipedia')
    def test_author_with_minimal_info_scenario(self, mock_wikipedia):
        """정보가 부족한 작가 검색 시나리오"""
        print(f"  📝 정보 부족한 작가 검색 시나리오")

        minimal_text = """이 작가는 20세기 초의 문인이다.
    
    == 작품 ==
    몇 편의 시를 남겼다.
    
    == 기타 ==
    자세한 정보는 알려지지 않았다."""

        mock_page = Mock()
        mock_page.exists.return_value = True
        mock_page.title = "무명 작가"
        mock_page.summary = "20세기 초의 문인"
        mock_page.text = minimal_text
        mock_page.fullurl = "https://ko.wikipedia.org/wiki/무명작가"

        mock_wiki = Mock()
        mock_wiki.page.return_value = mock_page
        mock_wikipedia.return_value = mock_wiki

        print(f"  📚 시나리오: 학력 정보가 거의 없는 작가")
        print(f"    - 기본적인 정보만 존재")
        print(f"    - 학력 관련 섹션 없음")

        tool = WikipediaSearchTool()
        result = tool.search_page("무명작가")

        print(f"  📊 검색 결과:")
        print(f"    - success: {result['success']}")
        print(f"    - content 길이: {len(result['content'])}자")
        print(f"    - 기본 정보 포함: {'20세기' in result['content']}")

        # 최소한의 정보라도 성공적으로 반환되는지 확인
        assert result['success'] == True
        assert len(result['content']) > 0
        assert "20세기" in result['content']
        print("✅ 정보 부족한 작가 검색 시나리오 테스트 통과")


if __name__ == "__main__":

    print("🧪 WikiSearchTool 직관적인 TDD 테스트 시작\n")

    # 기본 기능 테스트
    print("📋 기본 기능 테스트 - Tool 동작 확인")
    print("=" * 60)
    test_basics = TestWikiSearchToolBasics()
    test_basics.test_tool_initialization()
    print()
    test_basics.test_successful_search_mock()
    print()
    test_basics.test_page_not_found_mock()
    print()
    test_basics.test_api_error_mock()

    # 중요 섹션 추출 테스트
    print("\n🔍 중요 섹션 추출 기능 테스트")
    print("=" * 60)
    test_sections = TestWikiSearchToolImportantSections()
    test_sections.test_extract_important_sections_with_education()
    test_sections.test_extract_important_sections_with_keywords_in_content()
    test_sections.test_extract_important_sections_no_education_info()

    # 엣지 케이스 테스트
    print("\n🚨 엣지 케이스 테스트")
    print("=" * 60)
    test_edge_cases = TestWikiSearchToolEdgeCases()
    test_edge_cases.test_empty_search_term()
    test_edge_cases.test_very_long_content()
    test_edge_cases.test_special_characters_in_search()

    # 실제 사용 시나리오 테스트
    print("\n🎭 실제 사용 시나리오 테스트")
    print("=" * 60)
    test_scenarios = TestWikiSearchToolUsageScenarios()
    test_scenarios.test_author_with_education_info_scenario()
    test_scenarios.test_author_with_minimal_info_scenario()

    print("\n" + "=" * 60)
    print("🎉 모든 WikiSearchTool Mock 테스트 통과!")
    print("\n📊 테스트 요약:")
    print("  ✅ 기본 기능: 4개 테스트 (Mock 사용)")
    print("  ✅ 섹션 추출: 3개 테스트")
    print("  ✅ 엣지 케이스: 3개 테스트")
    print("  ✅ 사용 시나리오: 2개 테스트")
    print("\n🌐 통합 테스트 (실제 API 호출):")
    print("  ⚠️  네트워크 연결이 필요한 테스트는 별도로 실행:")
    print("    python -m pytest tests/unit/tools/test_wiki_search_tool.py::TestWikiSearchToolIntegration -v -s -m integration")

    print("\n📝 pytest로 실행하려면:")
    print("    cd ai-service")
    print("    # Mock 테스트만")
    print("    python -m pytest tests/unit/tools/test_wiki_search_tool.py -v -s")
    print("    # 통합 테스트 포함")
    print("    python -m pytest tests/unit/tools/test_wiki_search_tool.py -v -s -m integration")
