"""
WikiAgentResponse 직관적인 TDD 테스트
각 테스트마다 성공 메시지 출력으로 진행상황을 실시간 확인

실행 방법:
    cd ai-service
    python tests/unit/models/test_wiki_agent_response.py
    또는
    python -m pytest tests/unit/models/test_wiki_agent_response.py -v -s
"""

import pytest
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 테스트 대상 모델 import
from app.models.wiki_agent_response import WikiAgentResponse, ActionType

class TestWikiAgentResponseBasics:
    """WikiAgentResponse 기본 기능 테스트"""

    def test_create_success_response(self):
        """성공 응답 생성 테스트"""
        message = "김소월 작가 정보를 성공적으로 찾았습니다."

        print(f"  📝 성공 메시지: '{message}'")
        print(f"  🎯 응답 타입: 성공 결과 표시")

        response = WikiAgentResponse.create_success(message, context_updated=True)

        print(f"  ✅ 성공 여부: {response.success}")
        print(f"  📄 저장된 메시지: '{response.message}'")
        print(f"  🎬 액션 타입: {response.action.value}")
        print(f"  🔄 대화 계속: {response.should_continue}")
        print(f"  📝 컨텍스트 업데이트: {response.context_updated}")

        assert response.success == True
        assert response.message == message
        assert response.action == ActionType.SHOW_RESULT
        assert response.should_continue == True
        assert response.context_updated == True
        assert response.agent_name == 'wiki_search'
        assert response.error is None
        print("✅ 성공 응답 생성 테스트 통과")


    def test_create_clarification_response(self):
        """명확화 요청 응답 생성 테스트"""
        message = "동일한 이름의 작가가 여러 명 있습니다. 어느 김철수를 찾으시나요?"

        print(f"  📝 명확화 메시지: '{message}'")
        print(f"  🤔 상황: 동명이인으로 인한 모호한 질문")

        response = WikiAgentResponse.create_clarification(message, context_updated=False)

        print(f"  ✅ 성공 여부: {response.success} (명확화도 성공 응답)")
        print(f"  📄 저장된 메시지: '{response.message}'")
        print(f"  🎬 액션 타입: {response.action.value}")
        print(f"  🔄 대화 계속: {response.should_continue}")
        print(f"  📝 컨텍스트 업데이트: {response.context_updated}")

        assert response.success == True
        assert response.message == message
        assert response.action == ActionType.ASK_CLARIFICATION
        assert response.should_continue == True
        assert response.context_updated == False
        print("✅ 명확화 요청 응답 생성 테스트 통과")

    def test_create_error_response(self):
        """에러 응답 생성 테스트"""
        message = "위키피디아 검색 중 오류가 발생했습니다."
        error_details = "네트워크 연결 시간 초과"

        print(f"  📝 에러 메시지: '{message}'")
        print(f"  🚨 에러 세부사항: '{error_details}'")
        print(f"  💥 상황: 외부 API 호출 실패")

        response = WikiAgentResponse.create_error(message, error_details)

        print(f"  ❌ 성공 여부: {response.success}")
        print(f"  📄 저장된 메시지: '{response.message}'")
        print(f"  🎬 액션 타입: {response.action.value}")
        print(f"  🔄 대화 계속: {response.should_continue}")
        print(f"  📝 컨텍스트 업데이트: {response.context_updated}")
        print(f"  🚨 에러 정보: '{response.error}'")

        assert response.success == False
        assert response.message == message
        assert response.action == ActionType.ERROR
        assert response.should_continue == False
        assert response.context_updated == False
        assert response.error == error_details
        print("✅ 에러 응답 생성 테스트 통과")

    def test_direct_constructor(self):
        """직접 생성자 사용 테스트"""
        print(f"  🔧 직접 생성자로 커스텀 응답 생성")
        print(f"  🎯 시나리오: 부분적 성공 (일부 정보만 찾음)")

        response = WikiAgentResponse(
            success=True,
            message="작가 정보 일부만 찾았습니다.",
            action=ActionType.SUCCESS,
            should_continue=True,
            context_updated=True,
            agent_name='custom_wiki',
            error=None
        )

        print(f"  ✅ 성공 여부: {response.success}")
        print(f"  📄 메시지: '{response.message}'")
        print(f"  🎬 액션: {response.action.value}")
        print(f"  🤖 에이전트명: '{response.agent_name}'")

        assert response.success == True
        assert response.action == ActionType.SUCCESS
        assert response.agent_name == 'custom_wiki'
        print("✅ 직접 생성자 사용 테스트 통과")


class TestWikiAgentResponseMethods:
    """WikiAgentResponse 메서드 테스트"""

    def test_is_success_method(self):
        """성공 여부 확인 메서드 테스트"""
        success_response = WikiAgentResponse.create_success("성공!")
        error_response = WikiAgentResponse.create_error("실패!")

        print(f"  ✅ 성공 응답 확인: {success_response.is_success()}")
        print(f"  ❌ 에러 응답 확인: {error_response.is_success()}")

        assert success_response.is_success() == True
        assert error_response.is_success() == False
        print("✅ 성공 여부 확인 메서드 테스트 통과")

    def test_needs_clarification_method(self):
        """명확화 필요 여부 확인 메서드 테스트"""
        clarification_response = WikiAgentResponse.create_clarification("명확화 필요")
        success_response = WikiAgentResponse.create_success("성공!")

        print(f"  🤔 명확화 응답 확인: {clarification_response.needs_clarification()}")
        print(f"  ✅ 성공 응답 확인: {success_response.needs_clarification()}")

        assert clarification_response.needs_clarification() == True
        assert success_response.needs_clarification() == False
        print("✅ 명확화 필요 여부 확인 메서드 테스트 통과")

    def test_has_error_method(self):
        """에러 여부 확인 메서드 테스트"""
        error_response = WikiAgentResponse.create_error("에러 발생")
        success_response = WikiAgentResponse.create_success("성공!")

        print(f"  🚨 에러 응답 확인: {error_response.has_error()}")
        print(f"  ✅ 성공 응답 확인: {success_response.has_error()}")

        assert error_response.has_error() == True
        assert success_response.has_error() == False
        print("✅ 에러 여부 확인 메서드 테스트 통과")

    def test_should_continue_conversation_method(self):
        """대화 계속 여부 확인 메서드 테스트"""
        success_response = WikiAgentResponse.create_success("성공!")
        error_response = WikiAgentResponse.create_error("실패!")

        print(f"  ✅ 성공 응답 - 대화 계속: {success_response.should_continue_conversation()}")
        print(f"  ❌ 에러 응답 - 대화 계속: {error_response.should_continue_conversation()}")

        assert success_response.should_continue_conversation() == True
        assert error_response.should_continue_conversation() == False
        print("✅ 대화 계속 여부 확인 메서드 테스트 통과")


class TestWikiAgentResponseSerialization:
    """WikiAgentResponse 직렬화/역직렬화 테스트"""

    def test_success_response_to_dict(self):
        """성공 응답 딕셔너리 변환 테스트"""
        message = "작가 정보를 찾았습니다."

        print(f"  📝 입력 메시지: '{message}'")
        print(f"  🔄 딕셔너리 변환 과정 시작")

        response = WikiAgentResponse.create_success(message, context_updated=True)
        result = response.to_dict()

        print(f"  📊 변환 결과:")
        print(f"    - success: {result['success']}")
        print(f"    - message: '{result['message']}'")
        print(f"    - action: '{result['action']}'")
        print(f"    - should_continue: {result['should_continue']}")
        print(f"    - context_updated: {result['context_updated']}")
        print(f"    - agent_name: '{result['agent_name']}'")

        assert result['success'] == True
        assert result['message'] == message
        assert result['action'] == 'show_result'
        assert result['should_continue'] == True
        assert result['context_updated'] == True
        assert result['agent_name'] == 'wiki_search'
        assert 'error' not in result  # 에러가 없으면 포함되지 않음
        print("✅ 성공 응답 딕셔너리 변환 테스트 통과")

    def test_error_response_to_dict(self):
        """에러 응답 딕셔너리 변환 테스트"""
        message = "검색 실패"
        error_details = "API 호출 실패"

        response = WikiAgentResponse.create_error(message, error_details)
        result = response.to_dict()

        print(f"  📊 에러 응답 변환 결과:")
        print(f"    - success: {result['success']}")
        print(f"    - action: '{result['action']}'")
        print(f"    - error: '{result['error']}'")

        assert result['success'] == False
        assert result['action'] == 'error'
        assert result['error'] == error_details
        print("✅ 에러 응답 딕셔너리 변환 테스트 통과")

    def test_success_response_from_dict(self):
        """성공 응답 딕셔너리 복원 테스트"""
        data = {
            'success': True,
            'message': '복원된 성공 메시지',
            'action': 'show_result',
            'should_continue': True,
            'context_updated': False,
            'agent_name': 'test_agent'
        }

        print(f"  📥 입력 딕셔너리: {data}")

        response = WikiAgentResponse.from_dict(data)

        print(f"  📤 복원된 객체:")
        print(f"    - success: {response.success}")
        print(f"    - message: '{response.message}'")
        print(f"    - action: {response.action.value}")
        print(f"    - agent_name: '{response.agent_name}'")

        assert response.success == True
        assert response.message == '복원된 성공 메시지'
        assert response.action == ActionType.SHOW_RESULT
        assert response.agent_name == 'test_agent'
        print("✅ 성공 응답 딕셔너리 복원 테스트 통과")

    def test_clarification_response_from_dict(self):
        """명확화 응답 딕셔너리 복원 테스트"""
        data = {
            'success': True,
            'message': '명확화가 필요합니다',
            'action': 'ask_clarification',
            'should_continue': True,
            'context_updated': False
        }

        response = WikiAgentResponse.from_dict(data)

        assert response.action == ActionType.ASK_CLARIFICATION
        assert response.needs_clarification() == True
        print("✅ 명확화 응답 딕셔너리 복원 테스트 통과")

    def test_error_response_from_dict(self):
        """에러 응답 딕셔너리 복원 테스트"""
        data = {
            'success': False,
            'message': '에러 발생',
            'action': 'error',
            'should_continue': False,
            'context_updated': False,
            'error': '상세 에러 정보'
        }

        response = WikiAgentResponse.from_dict(data)

        assert response.success == False
        assert response.action == ActionType.ERROR
        assert response.error == '상세 에러 정보'
        assert response.has_error() == True
        print("✅ 에러 응답 딕셔너리 복원 테스트 통과")

class TestWikiAgentResponseRoundtrip:
    """WikiAgentResponse 직렬화-역직렬화 왕복 테스트"""

    def test_success_response_roundtrip(self):
        """성공 응답 직렬화-역직렬화 왕복 테스트"""
        original = WikiAgentResponse.create_success(
            "한강 작가 정보 검색 완료",
            context_updated=True
        )

        print(f"  📤 원본 응답:")
        print(f"    - message: '{original.message}'")
        print(f"    - action: {original.action.value}")
        print(f"    - context_updated: {original.context_updated}")

        # 직렬화
        data = original.to_dict()
        print(f"  🔄 직렬화 완료")

        # 역직렬화
        restored = WikiAgentResponse.from_dict(data)
        print(f"  📥 역직렬화 완료")

        print(f"  🔍 복원된 응답:")
        print(f"    - message: '{restored.message}'")
        print(f"    - action: {restored.action.value}")
        print(f"    - context_updated: {restored.context_updated}")

        # 검증
        assert restored.success == original.success
        assert restored.message == original.message
        assert restored.action == original.action
        assert restored.should_continue == original.should_continue
        assert restored.context_updated == original.context_updated
        assert restored.agent_name == original.agent_name
        assert restored.error == original.error
        print("✅ 성공 응답 직렬화-역직렬화 왕복 테스트 통과")

    def test_clarification_response_roundtrip(self):
        """명확화 응답 직렬화-역직렬화 왕복 테스트"""
        original = WikiAgentResponse.create_clarification("어느 김철수인가요?")

        # 직렬화
        data = original.to_dict()

        # 역직렬화
        restored = WikiAgentResponse.from_dict(data)

        # 검증
        assert restored.success == original.success
        assert restored.message == original.message
        assert restored.action == original.action
        assert restored.needs_clarification() == True
        print("✅ 명확화 응답 직렬화-역직렬화 왕복 테스트 통과")

    def test_error_response_roundtrip(self):
        """에러 응답 직렬화-역직렬화 왕복 테스트"""
        original = WikiAgentResponse.create_error("검색 실패", "타임아웃 발생")

        # 직렬화
        data = original.to_dict()

        # 역직렬화
        restored = WikiAgentResponse.from_dict(data)

        # 검증
        assert restored.success == original.success
        assert restored.message == original.message
        assert restored.action == original.action
        assert restored.error == original.error
        assert restored.has_error() == True
        print("✅ 에러 응답 직렬화-역직렬화 왕복 테스트 통과")

class TestWikiAgentResponseEdgeCases:
    """WikiAgentResponse 엣지 케이스 테스트"""

    def test_missing_fields_in_dict(self):
        """딕셔너리 필드 누락 처리 테스트"""
        minimal_data = {
            'success': True,
            'message': '최소 데이터'
        }

        print(f"  📥 최소 딕셔너리: {minimal_data}")
        response = WikiAgentResponse.from_dict(minimal_data)

        print(f"  📤 복원된 객체 (기본값 적용):")
        print(f"    - success: {response.success}")
        print(f"    - message: '{response.message}'")
        print(f"    - action: {response.action.value} (기본값)")
        print(f"    - should_continue: {response.should_continue} (기본값)")
        print(f"    - agent_name: '{response.agent_name}' (기본값)")

        assert response.success == True
        assert response.message == '최소 데이터'
        assert response.action == ActionType.ERROR  # 기본값
        assert response.should_continue == False  # 기본값
        assert response.agent_name == 'wiki_search'  # 기본값
        print("✅ 딕셔너리 필드 누락 처리 테스트 통과")

    def test_invalid_action_type_handling(self):
        """잘못된 액션 타입 처리 테스트"""
        data = {
            'success': True,
            'message': '잘못된 액션',
            'action': 'invalid_action_type'
        }

        print(f"  📥 잘못된 액션 타입: '{data['action']}'")

        response = WikiAgentResponse.from_dict(data)

        print(f"  📤 처리 결과: action = {response.action.value} (기본값으로 변경)")

        assert response.action == ActionType.ERROR  # 기본값으로 처리
        print("✅ 잘못된 액션 타입 처리 테스트 통과")

    def test_none_error_handling(self):
        """None 에러 처리 테스트"""
        response = WikiAgentResponse.create_success("성공", context_updated=False)

        print(f"  📝 성공 응답의 에러 필드: {response.error}")
        print(f"  🔍 에러 여부 확인: {response.has_error()}")

        assert response.error is None
        assert response.has_error() == False

        # 딕셔너리 변환시 None 에러는 포함되지 않음
        result = response.to_dict()
        assert 'error' not in result
        print("✅ None 에러 처리 테스트 통과")


    def test_empty_message_handling(self):
        """빈 메시지 처리 테스트"""
        response = WikiAgentResponse.create_success("", context_updated=False)

        print(f"  📝 빈 메시지 처리: '{response.message}'")

        assert response.message == ""
        assert response.success == True
        print("✅ 빈 메시지 처리 테스트 통과")

class TestWikiAgentResponseUsageScenarios:
    """WikiAgentResponse 실제 사용 시나리오 테스트"""

    def test_successful_author_search_scenario(self):
        """성공적인 작가 검색 시나리오"""
        print("  📚 시나리오: 사용자가 '한강 작가'를 검색하여 성공적으로 정보를 찾음")

        response = WikiAgentResponse.create_success(
            "한강 작가 정보를 찾았습니다. 1970년 출생, 2016년 맨부커상 수상 등의 정보가 있습니다.",
            context_updated=True
        )

        print(f"  ✅ 검색 성공: {response.is_success()}")
        print(f"  📝 컨텍스트 업데이트: {response.context_updated}")
        print(f"  🔄 대화 계속 가능: {response.should_continue_conversation()}")

        assert response.is_success() == True
        assert response.context_updated == True
        assert response.should_continue_conversation() == True
        print("✅ 성공적인 작가 검색 시나리오 테스트 통과")

    def test_ambiguous_search_scenario(self):
        """모호한 검색 시나리오"""
        print("  🤔 시나리오: 사용자가 '김철수'를 검색했는데 동명이인이 여러 명 존재")

        response = WikiAgentResponse.create_clarification(
            "김철수라는 이름의 작가가 여러 명 있습니다:\n1. 김철수 (시인, 1950년생)\n2. 김철수 (소설가, 1962년생)\n어느 분을 찾으시나요?",
            context_updated=False
        )

        print(f"  🤔 명확화 필요: {response.needs_clarification()}")
        print(f"  📝 컨텍스트 업데이트: {response.context_updated} (아직 확정되지 않아서)")
        print(f"  🔄 대화 계속: {response.should_continue_conversation()}")

        assert response.needs_clarification() == True
        assert response.context_updated == False
        assert response.should_continue_conversation() == True
        print("✅ 모호한 검색 시나리오 테스트 통과")

    def test_search_failure_scenario(self):
        """검색 실패 시나리오"""
        print("  🚨 시나리오: 위키피디아 API 호출 중 네트워크 오류 발생")

        response = WikiAgentResponse.create_error(
            "죄송합니다. 현재 위키피디아에 접근할 수 없습니다. 잠시 후 다시 시도해주세요.",
            "Connection timeout after 30 seconds"
        )

        print(f"  ❌ 에러 발생: {response.has_error()}")
        print(f"  🚨 에러 상세: '{response.error}'")
        print(f"  🔄 대화 계속: {response.should_continue_conversation()} (에러로 인해 중단)")

        assert response.has_error() == True
        assert response.error is not None
        assert response.should_continue_conversation() == False
        print("✅ 검색 실패 시나리오 테스트 통과")

    def test_partial_information_scenario(self):
        """부분 정보 검색 시나리오"""
        print("  📄 시나리오: 작가 정보 일부만 찾았지만 유용한 정보 제공")

        response = WikiAgentResponse(
            success=True,
            message="요청하신 작가의 기본 정보는 찾았지만, 최근 작품 목록은 확인되지 않았습니다.",
            action=ActionType.SHOW_RESULT,
            should_continue=True,
            context_updated=True,
            agent_name='wiki_search'
        )

        print(f"  ✅ 부분 성공: {response.is_success()}")
        print(f"  📝 유용한 정보 제공: '{response.message}'")
        print(f"  🔄 추가 질문 가능: {response.should_continue_conversation()}")

        assert response.is_success() == True
        assert "부분" in response.message or "일부" in response.message
        assert response.should_continue_conversation() == True
        print("✅ 부분 정보 검색 시나리오 테스트 통과")


if __name__ == "__main__":
    print("🧪 WikiAgentResponse 직관적인 TDD 테스트 시작\n")

    #기본 기능 테스트
    print("📋 기본 기능 테스트 - 응답 생성 과정 확인")
    print("=" * 60)
    test_basics = TestWikiAgentResponseBasics()
    test_basics.test_create_success_response()
    print()
    test_basics.test_create_clarification_response()
    print()
    test_basics.test_create_error_response()
    print()
    test_basics.test_direct_constructor()

    # 메서드 테스트
    print("\n🔧 메서드 기능 테스트")
    print("=" * 60)
    test_methods = TestWikiAgentResponseMethods()
    test_methods.test_is_success_method()
    test_methods.test_needs_clarification_method()
    test_methods.test_has_error_method()
    test_methods.test_should_continue_conversation_method()

    # 직렬화/역직렬화 테스트
    print("\n📄 직렬화/역직렬화 테스트")
    print("=" * 60)
    test_serialization = TestWikiAgentResponseSerialization()
    test_serialization.test_success_response_to_dict()
    test_serialization.test_error_response_to_dict()
    test_serialization.test_success_response_from_dict()
    test_serialization.test_clarification_response_from_dict()
    test_serialization.test_error_response_from_dict()

    # 왕복 테스트
    print("\n🔄 왕복 테스트")
    print("=" * 60)
    test_roundtrip = TestWikiAgentResponseRoundtrip()
    test_roundtrip.test_success_response_roundtrip()
    test_roundtrip.test_clarification_response_roundtrip()

    # 엣지 케이스 테스트
    print("\n🚨 엣지 케이스 테스트")
    print("=" * 60)
    test_edge_cases = TestWikiAgentResponseEdgeCases()
    test_edge_cases.test_missing_fields_in_dict()
    test_edge_cases.test_invalid_action_type_handling()
    test_edge_cases.test_none_error_handling()
    test_edge_cases.test_empty_message_handling()

    # 실제 사용 시나리오 테스트
    print("\n🎭 실제 사용 시나리오 테스트")
    print("=" * 60)
    test_scenarios = TestWikiAgentResponseUsageScenarios()
    test_scenarios.test_successful_author_search_scenario()
    test_scenarios.test_ambiguous_search_scenario()
    test_scenarios.test_search_failure_scenario()
    test_scenarios.test_partial_information_scenario()

    print("\n" + "=" * 60)
    print("🎉 모든 WikiAgentResponse 테스트 통과!")
    print("\n📊 테스트 요약:")
    print("  ✅ 기본 응답 생성: 4개 테스트")
    print("  ✅ 메서드 기능: 4개 테스트")
    print("  ✅ 직렬화/역직렬화: 5개 테스트")
    print("  ✅ 왕복 테스트: 3개 테스트")
    print("  ✅ 엣지 케이스: 4개 테스트")
    print("  ✅ 실제 시나리오: 4개 테스트")
    print("\n📝 pytest로 실행하려면:")
    print("    cd ai-service")
    print("    python -m pytest tests/unit/models/test_wiki_agent_response.py -v -s")
