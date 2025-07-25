#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
위키피디아 검색 에이전트 - 에이전트 응답 모델
에이전트의 응답을 표현하는 데이터 모델
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum


class ActionType(Enum):
    """에이전트 액션 타입"""
    ASK_CLARIFICATION = "ask_clarification"  # 명확화 요청
    SHOW_RESULT = "show_result"  # 결과 표시
    ERROR = "error"  # 에러
    SUCCESS = "success"  # 성공


@dataclass
class WikiAgentResponse:
    """위키피디아 검색 에이전트 응답"""
    success: bool
    message: str
    action: ActionType
    should_continue: bool
    context_updated: bool
    agent_name: str = 'wiki_search'
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환 (기존 코드 호환성을 위해)"""
        result = {
            'success': self.success,
            'message': self.message,
            'action': self.action.value,
            'should_continue': self.should_continue,
            'context_updated': self.context_updated,
            'agent_name': self.agent_name
        }
        
        if self.error:
            result['error'] = self.error
            
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WikiAgentResponse':
        """딕셔너리에서 객체 생성 (기존 코드 호환성을 위해)"""
        # ActionType 매핑
        action_str = data.get('action', 'error')
        action_map = {
            'ask_clarification': ActionType.ASK_CLARIFICATION,
            'show_result': ActionType.SHOW_RESULT,
            'error': ActionType.ERROR,
            'success': ActionType.SUCCESS
        }
        action = action_map.get(action_str, ActionType.ERROR)
        
        return cls(
            success=data.get('success', False),
            message=data.get('message', ''),
            action=action,
            should_continue=data.get('should_continue', False),
            context_updated=data.get('context_updated', False),
            agent_name=data.get('agent_name', 'wiki_search'),
            error=data.get('error')
        )

    @classmethod
    def create_success(cls, message: str, context_updated: bool = False) -> 'WikiAgentResponse':
        """성공 응답 생성"""
        return cls(
            success=True,
            message=message,
            action=ActionType.SHOW_RESULT,
            should_continue=True,
            context_updated=context_updated
        )

    @classmethod
    def create_clarification(cls, message: str, context_updated: bool = False) -> 'WikiAgentResponse':
        """명확화 요청 응답 생성"""
        return cls(
            success=True,
            message=message,
            action=ActionType.ASK_CLARIFICATION,
            should_continue=True,
            context_updated=context_updated
        )

    @classmethod
    def create_error(cls, message: str, error_details: str = None) -> 'WikiAgentResponse':
        """에러 응답 생성"""
        return cls(
            success=False,
            message=message,
            action=ActionType.ERROR,
            should_continue=False,
            context_updated=False,
            error=error_details
        )

    def is_success(self) -> bool:
        """성공 여부 확인"""
        return self.success

    def needs_clarification(self) -> bool:
        """명확화 필요 여부 확인"""
        return self.action == ActionType.ASK_CLARIFICATION

    def has_error(self) -> bool:
        """에러 여부 확인"""
        return self.action == ActionType.ERROR

    def should_continue_conversation(self) -> bool:
        """대화 계속 여부 확인"""
        return self.should_continue