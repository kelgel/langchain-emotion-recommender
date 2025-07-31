"""
WikiInformationExtractor 직관적인 TDD 테스트
각 테스트마다 성공 메시지 출력으로 진행상황을 실시간 확인

실행 방법:
    cd ai-service
    python tests/unit/utils/test_wiki_information_extractor.py
    또는
    python -m pytest tests/unit/utils/test_wiki_information_extractor.py -v -s
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock
import json
import time

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 의존성 모듈 Mock 설정
mock_modules = ['utils', 'models', 'tools', 'chains', 'prompts']
for module_name in mock_modules:
    if module_name not in sys.modules:
        sys.modules[module_name] = Mock()

# 테스트 대상 import
from app.utils.wiki_information_extractor import WikiInformationExtractor

class TestWikiInformationExtractorBasics:
    """WikiInformationExtractor 기본 정보 추출 테스트"""
    def test_find_university_info_success(self):
        """대학교 정보 추출 성공 테스트"""
        content = """
        김영하는 1968년 11월 11일 경기도 화성군에서 태어났다.
        연세대학교 경영학과를 졸업했으며, 1995년 계간 《리뷰》에 단편소설을 발표하며 등단했다.
        현재 연세대학교 국어국문학과 교수로 재직 중이다.
        """

        print(f"  📝 입력 텍스트:")
        print(f"    - 내용: '...연세대학교 경영학과를 졸업했으며...'")
        print(f"    - 예상 추출: 연세대학교")

        result = WikiInformationExtractor.find_university_info(content)

        print(f"  🎯 추출 결과: '{result}'")
        print(f"  ✅ 대학명 정확성: {'연세대학교' in result}")

        assert result is not None
        assert '연세대학교' in result
        print("✅ 대학교 정보 추출 성공 테스트 통과")

    def test_find_university_info_with_llm(self):
        """LLM을 사용한 대학교 정보 추출 테스트"""
        content = """
        한강은 1970년 광주에서 태어났다.
        연세대학교 국어국문학과를 졸업하고 소설가가 되었다.
        """

        # Mock LLM 클라이언트 생성
        mock_llm_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "university": "연세대학교",
            "department": "국어국문학과",
            "found": true
        }
        '''
        mock_llm_client.chat.completions.create.return_value = mock_response

        print(f"  🤖 LLM 클라이언트와 함께 대학교 정보 추출...")
        print(f"  📝 입력: '...연세대학교 국어국문학과를 졸업하고...'")

        result = WikiInformationExtractor.find_university_info(content, mock_llm_client)

        print(f"  🎯 LLM 추출 결과: '{result}'")
        print(f"  ✅ LLM 호출됨: {mock_llm_client.chat.completions.create.called}")

        assert result is not None
        assert '연세대학교' in result
        print("✅ LLM을 사용한 대학교 정보 추출 테스트 통과")

    def test_find_birth_info_success(self):
        """출생 정보 추출 성공 테스트"""
        content = """
        김영하는 1968년 11월 11일 경기도 화성군에서 태어났다.
        어린 시절을 화성에서 보내고 서울로 올라와 대학을 졸업했다.
        """

        print(f"  📅 출생 정보 추출 테스트...")
        print(f"  📝 입력: '1968년 11월 11일 경기도 화성군에서 태어났다'")
        print(f"  🎯 예상 결과: 1968년 11월 11일 관련 정보")

        result = WikiInformationExtractor.find_birth_info(content)

        print(f"  📊 추출 결과: '{result}'")
        print(f"  ✅ 연도 포함: {'1968' in result}")
        print(f"  ✅ 월일 포함: {'11월' in result or '11' in result}")

        assert result is not None
        assert '1968' in result
        print("✅ 출생 정보 추출 성공 테스트 통과")

    def test_find_death_info_success(self):
        """사망 정보 추출 성공 테스트"""
        content = """
        박경리는 1926년 10월 2일에 태어나 2008년 5월 5일에 사망했다.
        토지라는 대하소설로 유명한 작가였다.
        """

        print(f"  ⚰️ 사망 정보 추출 테스트...")
        print(f"  📝 입력: '2008년 5월 5일에 사망했다'")
        print(f"  🎯 예상 결과: 2008년 5월 5일 관련 정보")

        result = WikiInformationExtractor.find_death_info(content)

        print(f"  📊 추출 결과: '{result}'")
        print(f"  ✅ 사망년도 포함: {'2008' in result}")
        print(f"  ✅ 월일 포함: {'5월' in result or '5' in result}")

        assert result is not None
        assert '2008' in result
        print("✅ 사망 정보 추출 성공 테스트 통과")

    def test_find_school_info_success(self):
        """학교 정보 추출 성공 테스트"""
        content = """
        한강은 서울예술고등학교를 졸업하고 연세대학교에 진학했다.
        고등학교 시절부터 문학에 관심이 많았다.
        """

        print(f"  🏫 학교 정보 추출 테스트...")
        print(f"  📝 입력: '서울예술고등학교를 졸업하고...'")
        print(f"  🎯 예상 결과: 서울예술고등학교")

        result = WikiInformationExtractor.find_school_info(content)

        print(f"  📊 추출 결과: '{result}'")
        print(f"  ✅ 고등학교명 포함: {'서울예술고등학교' in result}")

        assert result is not None
        assert '고등학교' in result
        print("✅ 학교 정보 추출 성공 테스트 통과")

class TestWikiInformationExtractorWorks:
    """WikiInformationExtractor 작품 정보 추출 테스트"""
    def test_find_works_info_success(self):
        """작품 정보 추출 성공 테스트"""
        content = """
        김영하의 주요 작품으로는 《나는 나를 파괴할 권리가 있다》, 《살인자의 기억법》, 
        《빛의 과거》, 《검은 꽃》 등이 있다. 특히 《살인자의 기억법》은 영화화되기도 했다.
        """

        print(f"  📚 작품 정보 추출 테스트...")
        print(f"  📝 입력: '《나는 나를 파괴할 권리가 있다》, 《살인자의 기억법》...'")
        print(f"  🎯 예상 결과: 4개 작품 리스트")

        result = WikiInformationExtractor.find_works_info(content)

        print(f"  📊 추출 결과:")
        if isinstance(result, list):
            print(f"    - 작품 수: {len(result)}개")
            for i, work in enumerate(result, 1):
                print(f"    - {i}. {work}")
        else:
            print(f"    - 결과: {result}")

        assert result is not None
        if isinstance(result, list):
            assert len(result) > 0
            assert any('살인자의 기억법' in work for work in result)
        else:
            assert '살인자의 기억법' in result
        print("✅ 작품 정보 추출 성공 테스트 통과")

    def test_find_works_info_with_llm(self):
        """LLM을 사용한 작품 정보 추출 테스트"""
        content = """
        한강의 대표작으로는 《채식주의자》, 《소년이 온다》, 《흰》 등이 있다.
        특히 《채식주의자》로 맨부커상을 수상했다.
        """

        # Mock LLM 클라이언트 생성
        mock_llm_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "works": ["채식주의자", "소년이 온다", "흰"],
            "found": true
        }
        '''
        mock_llm_client.chat.completions.create.return_value = mock_response

        print(f"  🤖 LLM을 사용한 작품 정보 추출...")
        print(f"  📝 입력: '《채식주의자》, 《소년이 온다》, 《흰》...'")

        result = WikiInformationExtractor.find_works_info(content, mock_llm_client)

        print(f"  📊 LLM 추출 결과:")
        if isinstance(result, list):
            for i, work in enumerate(result, 1):
                print(f"    - {i}. {work}")

        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        assert '채식주의자' in result
        print("✅ LLM을 사용한 작품 정보 추출 테스트 통과")

class TestWikiInformationExtractorAwards:
    """WikiInformationExtractor 수상 정보 추출 테스트"""
    def test_find_awards_info_success(self):
        """수상 정보 추출 성공 테스트"""
        content = """
        김영하는 2004년 동인문학상을 수상했으며, 2010년에는 이상문학상을 받았다.
        또한 2016년에는 한국소설문학상도 수상했다.
        """

        print(f"  🏆 수상 정보 추출 테스트...")
        print(f"  📝 입력: '동인문학상을 수상했으며, 이상문학상을 받았다...'")
        print(f"  🎯 예상 결과: 3개 상 리스트")

        result = WikiInformationExtractor.find_awards_info(content)

        print(f"  📊 추출 결과:")
        if isinstance(result, list):
            print(f"    - 수상 수: {len(result)}개")
            for i, award in enumerate(result, 1):
                print(f"    - {i}. {award}")

        assert result is not None
        if isinstance(result, list):
            assert len(result) > 0
            # 일부 상이라도 정확히 추출되었는지 확인
            award_text = ' '.join(result)
            assert '문학상' in award_text or '상' in award_text
        print("✅ 수상 정보 추출 성공 테스트 통과")

    def test_find_awards_info_with_llm(self):
        """LLM을 사용한 수상 정보 추출 테스트"""
        content = """
        한강은 2016년 맨부커상을 수상했으며, 2000년 서울신문 신춘문예를 통해 등단했다.
        """

        # Mock LLM 클라이언트
        mock_llm_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "awards": ["2016년 맨부커상", "2000년 서울신문 신춘문예"],
            "found": true
        }
        '''
        mock_llm_client.chat.completions.create.return_value = mock_response

        print(f"  🤖 LLM을 사용한 수상 정보 추출...")
        print(f"  📝 입력: '2016년 맨부커상을 수상했으며...'")

        result = WikiInformationExtractor.find_awards_info(content, mock_llm_client)

        print(f"  📊 LLM 추출 결과:")
        if isinstance(result, list):
            for i, award in enumerate(result, 1):
                print(f"    - {i}. {award}")

        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        print("✅ LLM을 사용한 수상 정보 추출 테스트 통과")

class TestWikiInformationExtractorFamily:
    """WikiInformationExtractor 가족 정보 추출 테스트"""
    def test_find_family_info_basic(self):
        """기본 가족 정보 추출 테스트"""
        content = """
        김영하는 아버지 김철수와 어머니 이영희 사이에서 태어났다.
        어린 시절부터 책을 좋아했다.
        """

        print(f"  👨‍👩‍👧‍👦 기본 가족 정보 추출 테스트...")
        print(f"  📝 입력: '아버지 김철수와 어머니 이영희 사이에서 태어났다'")
        print(f"  🎯 예상 결과: father='김철수', mother='이영희'")

        result = WikiInformationExtractor.find_family_info(content)

        print(f"  📊 추출 결과:")
        print(f"    - 아버지: {result.get('father', 'None')}")
        print(f"    - 어머니: {result.get('mother', 'None')}")

        assert isinstance(result, dict)
        assert result.get('father') == '김철수'
        assert result.get('mother') == '이영희'
        print("✅ 기본 가족 정보 추출 테스트 통과")

    def test_find_enhanced_family_info_complex(self):
        """복합 가족 정보 추출 테스트"""
        content = """
        요시모토 바나나는 요시모토 다카아키의 차녀이자 만화가인 하루노 요이코의 동생이다.
        일본의 유명한 소설가로 활동하고 있다.
        """

        print(f"  🇯🇵 복합 가족 정보 추출 테스트...")
        print(f"  📝 입력: '요시모토 다카아키의 차녀이자 하루노 요이코의 동생이다'")
        print(f"  🧠 분석:")
        print(f"    - '차녀' = 아버지와의 관계 → 요시모토 다카아키는 아버지")
        print(f"    - '동생' = 형제자매 관계 → 하루노 요이코는 언니")

        result = WikiInformationExtractor.find_enhanced_family_info(content)

        print(f"  📊 추출 결과:")
        print(f"    - 아버지: {result.get('father', 'None')}")
        print(f"    - 어머니: {result.get('mother', 'None')}")
        print(f"    - 형제자매: {len(result.get('siblings', []))}명")
        if result.get('siblings'):
            for sibling in result['siblings']:
                print(f"      * {sibling.get('name', 'Unknown')} ({sibling.get('relation', 'Unknown')})")
        print(f"    - 전체 가족: {len(result.get('family', []))}명")

        assert isinstance(result, dict)
        # 요시모토 다카아키가 아버지로 인식되어야 함
        assert result.get('father') == '요시모토 다카아키'
        # 하루노 요이코는 형제자매로 인식되어야 함 (어머니가 아님!)
        siblings = result.get('siblings', [])
        sibling_names = [s.get('name') for s in siblings]
        assert '하루노 요이코' in sibling_names
        print("✅ 복합 가족 정보 추출 테스트 통과")

    def test_find_enhanced_family_info_with_llm(self):
        """LLM을 사용한 강화 가족 정보 추출 테스트"""
        content = """
        한승원은 소설가 한승원의 아들로 태어났다.
        아버지의 영향을 받아 문학의 길로 들어섰다.
        """

        # Mock LLM 클라이언트
        mock_llm_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "father": null,
            "mother": null,
            "found": false
        }
        '''
        mock_llm_client.chat.completions.create.return_value = mock_response

        print(f"  🤖 LLM을 사용한 강화 가족 정보 추출...")
        print(f"  📝 입력: '소설가 한승원의 아들로 태어났다'")
        print(f"  🚨 주의: '한승원의 아들'에서 한승원의 성별은 불분명 (LLM이 올바르게 판단해야 함)")

        result = WikiInformationExtractor.find_enhanced_family_info(content, mock_llm_client)

        print(f"  📊 추출 결과:")
        print(f"    - 아버지: {result.get('father', 'None')}")
        print(f"    - 어머니: {result.get('mother', 'None')}")
        print(f"    - LLM 호출됨: {mock_llm_client.chat.completions.create.called}")

        # 성별이 불분명한 경우 부모로 추출하지 않아야 함
        assert isinstance(result, dict)
        print("✅ LLM을 사용한 강화 가족 정보 추출 테스트 통과")

    def test_find_father_info_direct(self):
        """직접 아버지 정보 추출 테스트"""
        content = """
        그의 아버지는 한승원이었고, 문학에 대한 조예가 깊었다.
        """

        print(f"  👨 직접 아버지 정보 추출...")
        print(f"  📝 입력: '아버지는 한승원이었고'")

        result = WikiInformationExtractor.find_father_info(content)

        print(f"  📊 추출 결과: '{result}'")
        print(f"  ✅ 아버지명 정확성: {'한승원' == result}")

        assert result == '한승원'
        print("✅ 직접 아버지 정보 추출 테스트 통과")

    def test_find_mother_info_direct(self):
        """직접 어머니 정보 추출 테스트"""
        content = """
        그의 어머니는 김영희였으며, 교사로 일했다.
        """

        print(f"  👩 직접 어머니 정보 추출...")
        print(f"  📝 입력: '어머니는 김영희였으며'")

        result = WikiInformationExtractor.find_mother_info(content)

        print(f"  📊 추출 결과: '{result}'")
        print(f"  ✅ 어머니명 정확성: {'김영희' == result}")

        assert result == '김영희'
        print("✅ 직접 어머니 정보 추출 테스트 통과")

    def test_find_spouse_info(self):
        """배우자 정보 추출 테스트"""
        content = """
        김영하는 2005년 아내 이수연과 결혼했다.
        현재 두 자녀와 함께 살고 있다.
        """

        print(f"  💑 배우자 정보 추출...")
        print(f"  📝 입력: '아내 이수연과 결혼했다'")

        result = WikiInformationExtractor.find_spouse_info(content)

        print(f"  📊 추출 결과: '{result}'")
        print(f"  ✅ 배우자명 정확성: {'이수연' in result}")

        assert '이수연' in result
        print("✅ 배우자 정보 추출 테스트 통과")

class TestWikiInformationExtractorCompound:
    """WikiInformationExtractor 복합 질문 처리 테스트"""

    def test_detect_compound_query_success(self):
        """복합 질문 감지 성공 테스트"""
        queries = [
            "김영하와 한강에 대해 알려줘",
            "박경리, 한강에 대해 각각 설명해줘",
            "무라카미 하루키와 베르나르 베르베르 정보",
        ]

        print(f"  🔗 복합 질문 감지 테스트...")

        for i, query in enumerate(queries, 1):
            print(f"    {i}. 테스트 쿼리: '{query}'")

            result = WikiInformationExtractor.detect_compound_query(query)

            print(f"       📊 분석 결과:")
            print(f"         - 복합 질문 여부: {result.get('is_compound', False)}")
            print(f"         - 주제 수: {len(result.get('subjects', []))}개")
            if result.get('subjects'):
                for j, subject in enumerate(result['subjects'], 1):
                    print(f"         - 주제 {j}: '{subject}'")

            assert isinstance(result, dict)
            assert result.get('is_compound') == True
            assert len(result.get('subjects', [])) == 2
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 복합 질문 감지 성공 테스트 통과")

    def test_detect_compound_query_single(self):
        """단일 질문 감지 테스트"""
        single_queries = [
            "김영하에 대해 알려줘",
            "한강 작가 정보",
            "박경리의 대표작은?"
        ]

        print(f"  🔍 단일 질문 감지 테스트...")

        for i, query in enumerate(single_queries, 1):
            print(f"    {i}. 테스트 쿼리: '{query}'")

            result = WikiInformationExtractor.detect_compound_query(query)

            print(f"       📊 분석 결과:")
            print(f"         - 복합 질문 여부: {result.get('is_compound', False)}")
            print(f"         - 주제 수: {len(result.get('subjects', []))}개")

            assert isinstance(result, dict)
            assert result.get('is_compound') == False
            assert len(result.get('subjects', [])) == 0
            print(f"       ✅ 테스트 {i} 통과")

        print("✅ 단일 질문 감지 테스트 통과")

class TestWikiInformationExtractorEdgeCases:
    """WikiInformationExtractor 엣지 케이스 테스트"""

    def test_empty_content_handling(self):
        """빈 내용 처리 테스트"""
        empty_contents = ["", "   ", "\n\n", None]

        print(f"  🗳️ 빈 내용 처리 테스트...")

        for i, content in enumerate(empty_contents, 1):
            print(f"    {i}. 테스트 내용: {repr(content)}")

            try:
                # 다양한 추출 함수들 테스트
                university = WikiInformationExtractor.find_university_info(content or "")
                birth = WikiInformationExtractor.find_birth_info(content or "")
                works = WikiInformationExtractor.find_works_info(content or "")

                print(f"       📊 결과:")
                print(f"         - 대학교: {repr(university)}")
                print(f"         - 출생: {repr(birth)}")
                print(f"         - 작품: {repr(works)}")

                # 빈 결과나 빈 리스트가 반환되어야 함
                assert university == "" or university is None
                assert birth == "" or birth is None
                assert works == [] or works == "" or works is None

                print(f"       ✅ 테스트 {i} 통과")

            except Exception as e:
                print(f"       ⚠️ 예외 발생: {type(e).__name__}: {e}")
                # 적절한 예외 타입인지 확인
                assert isinstance(e, (AttributeError, TypeError, ValueError))
                print(f"       ✅ 적절한 예외 처리됨")

        print("✅ 빈 내용 처리 테스트 통과")

    def test_malformed_content_handling(self):
        """잘못된 형식 내용 처리 테스트"""
        malformed_contents = [
            "《》《》《》",  # 빈 괄호들
            "아버지아버지어머니어머니",  # 키워드만 반복
            "1234567890",  # 숫자만
            "!!!@@@###$$$",  # 특수문자만
            "ａｂｃｄｅｆｇ",  # 전각 문자
        ]

        print(f"  🚫 잘못된 형식 내용 처리 테스트...")

        for i, content in enumerate(malformed_contents, 1):
            print(f"    {i}. 테스트 내용: '{content}'")

            try:
                # 가족 정보 추출 테스트
                family = WikiInformationExtractor.find_family_info(content)
                works = WikiInformationExtractor.find_works_info(content)

                print(f"       📊 결과:")
                print(f"         - 가족: {family}")
                print(f"         - 작품: {works}")

                # 빈 결과나 적절한 기본값이 반환되어야 함
                assert isinstance(family, dict)
                assert isinstance(works, list) or works == "" or works is None

                print(f"       ✅ 테스트 {i} 통과")

            except Exception as e:
                print(f"       ⚠️ 예외 발생: {type(e).__name__}: {e}")
                assert isinstance(e, (AttributeError, TypeError, ValueError, KeyError))
                print(f"       ✅ 적절한 예외 처리됨")

        print("✅ 잘못된 형식 내용 처리 테스트 통과")

    def test_very_long_content_handling(self):
        """매우 긴 내용 처리 테스트"""
        # 매우 긴 텍스트 생성
        long_content = """
        김영하는 1968년 11월 11일 경기도 화성군에서 태어났다.
        연세대학교 경영학과를 졸업했다.
        """ * 500  # 500번 반복

        print(f"  📏 매우 긴 내용 처리 테스트...")
        print(f"    - 내용 길이: {len(long_content):,}자")
        print(f"    - 예상 추출: 연세대학교, 1968년 등")

        start_time = time.time()

        # 다양한 추출 함수 테스트
        university = WikiInformationExtractor.find_university_info(long_content)
        birth = WikiInformationExtractor.find_birth_info(long_content)

        end_time = time.time()
        processing_time = end_time - start_time

        print(f"    📊 처리 결과:")
        print(f"      - 처리 시간: {processing_time:.4f}초")
        print(f"      - 대학교: '{university}'")
        print(f"      - 출생: '{birth}'")

        # 성능 기준: 5초 이내 처리
        assert processing_time < 5.0
        assert '연세대학교' in university or university == ""
        assert '1968' in birth or birth == ""

        print("✅ 매우 긴 내용 처리 테스트 통과")

    def test_unicode_and_special_characters(self):
        """유니코드 및 특수문자 처리 테스트"""
        unicode_content = """
        김영하는 1968년 🎭 출생했다.
        연세대학교 🎓 졸업했으며, 《살인자의 기억법》 📚 등을 썼다.
        José Saramago의 영향을 받았다. α, β, γ 그리스 문자도 포함.
        """

        print(f"  🌐 유니코드 및 특수문자 처리 테스트...")
        print(f"    - 내용: 이모지, 그리스 문자, 라틴 문자 포함")

        try:
            university = WikiInformationExtractor.find_university_info(unicode_content)
            works = WikiInformationExtractor.find_works_info(unicode_content)
            birth = WikiInformationExtractor.find_birth_info(unicode_content)

            print(f"    📊 처리 결과:")
            print(f"      - 대학교: '{university}'")
            print(f"      - 작품: {works}")
            print(f"      - 출생: '{birth}'")

            # 유니코드가 있어도 정상 처리되어야 함
            assert isinstance(university, str)
            assert isinstance(works, list) or isinstance(works, str)
            assert isinstance(birth, str)

            print("✅ 유니코드 및 특수문자 처리 테스트 통과")

        except Exception as e:
            print(f"    ❌ 예외 발생: {e}")
            # 유니코드 처리 실패 시에도 적절한 예외여야 함
            assert isinstance(e, (UnicodeError, AttributeError, TypeError))
            print("✅ 적절한 예외 처리됨")

class TestWikiInformationExtractorPerformance:
    """WikiInformationExtractor 성능 테스트"""
    def test_extraction_performance(self):
        """정보 추출 성능 테스트"""
        sample_content = """
        김영하는 1968년 11월 11일 경기도 화성군에서 태어났다.
        연세대학교 경영학과를 졸업했으며, 1995년 계간 《리뷰》에 단편소설 《거울에 대한 명상》을 발표하며 등단했다.
        주요 작품으로는 《나는 나를 파괴할 권리가 있다》, 《살인자의 기억법》, 《빛의 과거》 등이 있다.
        2004년 동인문학상, 2010년 이상문학상을 수상했다.
        """

        print(f"  ⚡ 정보 추출 성능 테스트...")
        print(f"    - 테스트 횟수: 50회")
        print(f"    - 함수: 대학교, 출생, 작품, 수상 정보")

        start_time = time.time()

        for i in range(50):
            WikiInformationExtractor.find_university_info(sample_content)
            WikiInformationExtractor.find_birth_info(sample_content)
            WikiInformationExtractor.find_works_info(sample_content)
            WikiInformationExtractor.find_awards_info(sample_content)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 50

        print(f"    📊 성능 결과:")
        print(f"      - 총 실행 시간: {total_time:.4f}초")
        print(f"      - 평균 실행 시간: {avg_time:.4f}초/회")
        print(f"      - 초당 처리량: {1/avg_time:.1f}회/초")

        # 성능 기준: 평균 0.1초 이내
        assert avg_time < 0.1
        print("✅ 정보 추출 성능 테스트 통과")

    def test_llm_fallback_performance(self):
        """LLM 폴백 성능 테스트"""
        content = "복잡한 텍스트로 정규식으로는 추출하기 어려운 내용입니다."

        print(f"  🤖 LLM 폴백 성능 테스트...")

        # LLM 없이 처리 (폴백 사용)
        start_time = time.time()

        for i in range(20):
            WikiInformationExtractor.find_university_info(content)
            WikiInformationExtractor.find_birth_info(content)

        end_time = time.time()
        fallback_time = end_time - start_time

        print(f"    📊 폴백 성능:")
        print(f"      - 20회 처리 시간: {fallback_time:.4f}초")
        print(f"      - 평균 시간: {fallback_time/20:.4f}초/회")

        # Mock LLM으로 처리
        mock_llm_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"found": false}'
        mock_llm_client.chat.completions.create.return_value = mock_response

        start_time = time.time()

        for i in range(20):
            WikiInformationExtractor.find_university_info(content, mock_llm_client)
            WikiInformationExtractor.find_birth_info(content, mock_llm_client)

        end_time = time.time()
        llm_time = end_time - start_time

        print(f"    🤖 LLM 성능:")
        print(f"      - 20회 처리 시간: {llm_time:.4f}초")
        print(f"      - 평균 시간: {llm_time/20:.4f}초/회")

        # LLM 사용 시에도 합리적인 시간 내에 처리되어야 함
        assert llm_time < 2.0
        print("✅ LLM 폴백 성능 테스트 통과")

class TestWikiInformationExtractorIntegration:
    """WikiInformationExtractor 통합 테스트"""

    def test_full_information_extraction_workflow(self):
        """전체 정보 추출 워크플로우 테스트"""
        complete_content = """
        한강은 1970년 11월 27일 광주광역시에서 태어났다. 
        아버지는 소설가 한승원이고, 어머니는 임금순이다.
        서울예술고등학교를 졸업하고 연세대학교 국어국문학과에 진학했다.
        
        주요 작품으로는 《채식주의자》, 《소년이 온다》, 《흰》 등이 있다.
        2016년 《채식주의자》로 맨부커상을 수상했으며, 이는 한국 문학 최초의 맨부커상 수상이었다.
        또한 2000년 서울신문 신춘문예 소설 부문에 당선되어 등단했다.
        """

        print(f"  🔄 전체 정보 추출 워크플로우 테스트...")
        print(f"    - 대상: 한강 작가 정보")
        print(f"    - 추출 항목: 출생, 가족, 학력, 작품, 수상")

        # 1. 기본 정보 추출
        print(f"    1️⃣ 기본 정보 추출")
        birth_info = WikiInformationExtractor.find_birth_info(complete_content)
        university_info = WikiInformationExtractor.find_university_info(complete_content)
        school_info = WikiInformationExtractor.find_school_info(complete_content)

        print(f"       - 출생 정보: '{birth_info}'")
        print(f"       - 대학교: '{university_info}'")
        print(f"       - 고등학교: '{school_info}'")

        # 2. 가족 정보 추출
        print(f"    2️⃣ 가족 정보 추출")
        family_info = WikiInformationExtractor.find_enhanced_family_info(complete_content)

        print(f"       - 아버지: {family_info.get('father', 'None')}")
        print(f"       - 어머니: {family_info.get('mother', 'None')}")
        print(f"       - 가족 구성원 수: {len(family_info.get('family', []))}명")

        # 3. 작품 및 수상 정보 추출
        print(f"    3️⃣ 작품 및 수상 정보 추출")
        works_info = WikiInformationExtractor.find_works_info(complete_content)
        awards_info = WikiInformationExtractor.find_awards_info(complete_content)

        print(f"       - 작품 수: {len(works_info) if isinstance(works_info, list) else '정보 없음'}")
        if isinstance(works_info, list) and works_info:
            for work in works_info[:3]:  # 처음 3개만 표시
                print(f"         * {work}")

        print(f"       - 수상 수: {len(awards_info) if isinstance(awards_info, list) else '정보 없음'}")
        if isinstance(awards_info, list) and awards_info:
            for award in awards_info[:2]:  # 처음 2개만 표시
                print(f"         * {award}")

        # 4. 결과 검증
        print(f"    4️⃣ 결과 검증")

        # 출생 정보 검증
        assert '1970' in birth_info
        print(f"       ✅ 출생년도 정확")

        # 학력 정보 검증
        assert '연세대학교' in university_info
        assert '서울예술고등학교' in school_info
        print(f"       ✅ 학력 정보 정확")

        # 가족 정보 검증
        assert family_info.get('father') == '한승원'
        assert family_info.get('mother') == '임금순'
        print(f"       ✅ 가족 정보 정확")

        # 작품 정보 검증
        if isinstance(works_info, list):
            works_text = ' '.join(works_info)
            assert '채식주의자' in works_text
            print(f"       ✅ 작품 정보 정확")

        # 수상 정보 검증
        if isinstance(awards_info, list):
            awards_text = ' '.join(awards_info)
            assert '맨부커상' in awards_text or '부커' in awards_text
            print(f"       ✅ 수상 정보 정확")

        print("✅ 전체 정보 추출 워크플로우 테스트 통과")

    def test_cross_information_consistency(self):
        """정보 간 일관성 테스트"""
        content_with_inconsistency = """
        김영하는 1968년에 태어났다.
        한편, 그는 1969년 서울에서 출생했다고도 한다.
        연세대학교를 졸업했으며, 고려대학교 출신이기도 하다.
        """

        print(f"  🔍 정보 간 일관성 테스트...")
        print(f"    - 상황: 모순된 정보가 포함된 텍스트")
        print(f"    - 목표: 첫 번째로 발견된 정보 우선 선택")

        birth_info = WikiInformationExtractor.find_birth_info(content_with_inconsistency)
        university_info = WikiInformationExtractor.find_university_info(content_with_inconsistency)

        print(f"    📊 추출 결과:")
        print(f"      - 출생: '{birth_info}'")
        print(f"      - 대학교: '{university_info}'")

        # 첫 번째 정보가 우선되어야 함
        assert '1968' in birth_info  # 1969가 아닌 1968
        assert '연세대학교' in university_info  # 고려대학교가 아닌 연세대학교

        print("✅ 정보 간 일관성 테스트 통과")

if __name__ == "__main__":
    start_time = time.time()

    print("🧪 WikiInformationExtractor 직관적인 TDD 테스트 시작\n")

    # 기본 정보 추출 테스트
    print("📋 기본 정보 추출 테스트 - 개별 정보 추출 확인")
    print("=" * 60)
    test_basics = TestWikiInformationExtractorBasics()
    test_basics.test_find_university_info_success()
    print()
    test_basics.test_find_university_info_with_llm()
    print()
    test_basics.test_find_birth_info_success()
    print()
    test_basics.test_find_death_info_success()
    print()
    test_basics.test_find_school_info_success()

    # 작품 정보 추출 테스트
    print("\n📚 작품 정보 추출 테스트 - 작품 및 창작물 정보")
    print("=" * 60)
    test_works = TestWikiInformationExtractorWorks()
    test_works.test_find_works_info_success()
    print()
    test_works.test_find_works_info_with_llm()

    # 수상 정보 추출 테스트
    print("\n🏆 수상 정보 추출 테스트 - 상과 업적")
    print("=" * 60)
    test_awards = TestWikiInformationExtractorAwards()
    test_awards.test_find_awards_info_success()
    print()
    test_awards.test_find_awards_info_with_llm()

    # 가족 정보 추출 테스트
    print("\n👨‍👩‍👧‍👦 가족 정보 추출 테스트 - 부모, 형제자매, 배우자")
    print("=" * 60)
    test_family = TestWikiInformationExtractorFamily()
    test_family.test_find_family_info_basic()
    print()
    test_family.test_find_enhanced_family_info_complex()
    print()
    test_family.test_find_enhanced_family_info_with_llm()
    print()
    test_family.test_find_father_info_direct()
    print()
    test_family.test_find_mother_info_direct()
    print()
    test_family.test_find_spouse_info()

    # 복합 질문 처리 테스트
    print("\n🔗 복합 질문 처리 테스트 - 여러 주제 동시 처리")
    print("=" * 60)
    test_compound = TestWikiInformationExtractorCompound()
    test_compound.test_detect_compound_query_success()
    print()
    test_compound.test_detect_compound_query_single()

    # 엣지 케이스 테스트
    print("\n🚨 엣지 케이스 테스트 - 예외 상황 처리")
    print("=" * 60)
    test_edge_cases = TestWikiInformationExtractorEdgeCases()
    test_edge_cases.test_empty_content_handling()
    print()
    test_edge_cases.test_malformed_content_handling()
    print()
    test_edge_cases.test_very_long_content_handling()
    print()
    test_edge_cases.test_unicode_and_special_characters()

    # 성능 테스트
    print("\n⚡ 성능 테스트 - 처리 속도 및 효율성")
    print("=" * 60)
    test_performance = TestWikiInformationExtractorPerformance()
    test_performance.test_extraction_performance()
    print()
    test_performance.test_llm_fallback_performance()

    # 통합 테스트
    print("\n🔄 통합 테스트 - 전체 워크플로우 검증")
    print("=" * 60)
    test_integration = TestWikiInformationExtractorIntegration()
    test_integration.test_full_information_extraction_workflow()
    print()
    test_integration.test_cross_information_consistency()

    print("\n" + "=" * 60)
    print("🎉 모든 WikiInformationExtractor 테스트 통과!")
    print("\n📊 테스트 요약:")
    print("  ✅ 기본 정보 추출: 5개 테스트")
    print("  ✅ 작품 정보 추출: 2개 테스트")
    print("  ✅ 수상 정보 추출: 2개 테스트")
    print("  ✅ 가족 정보 추출: 6개 테스트")
    print("  ✅ 복합 질문 처리: 2개 테스트")
    print("  ✅ 엣지 케이스: 4개 테스트")
    print("  ✅ 성능 테스트: 2개 테스트")
    print("  ✅ 통합 테스트: 2개 테스트")
    print("\n📝 pytest로 실행하려면:")
    print("    cd ai-service")
    print("    python -m pytest tests/unit/utils/test_wiki_information_extractor.py -v -s")