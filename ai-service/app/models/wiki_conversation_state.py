#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
위키피디아 검색 에이전트 - 대화 상태 모델
에이전트의 대화 상태를 관리하는 데이터 모델
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class ConversationMessage:
    """대화 히스토리의 개별 메시지"""
    role: str  # 'user' 또는 'assistant'
    message: str
    timestamp: str


@dataclass
class WikiConversationState:
    """위키피디아 검색 에이전트의 대화 상태"""
    current_author: Optional[str] = None
    waiting_for_clarification: bool = False
    last_search_result: Optional[Dict[str, Any]] = None
    conversation_history: List[ConversationMessage] = field(default_factory=list)

    def add_message(self, role: str, message: str):
        """대화 히스토리에 메시지 추가"""
        self.conversation_history.append(ConversationMessage(
            role=role,
            message=message,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        
        # 히스토리 길이 제한 (최근 20개만 유지)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def reset(self):
        """대화 상태 초기화"""
        self.current_author = None
        self.waiting_for_clarification = False
        self.last_search_result = None
        self.conversation_history = []

    def update(self, updates: Dict[str, Any]):
        """상태 업데이트"""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환 (기존 코드 호환성을 위해)"""
        history = []
        for msg in self.conversation_history:
            if isinstance(msg, ConversationMessage):
                # ConversationMessage 객체인 경우
                history.append({
                    'role': msg.role,
                    'message': msg.message,
                    'timestamp': msg.timestamp
                })
            elif isinstance(msg, dict):
                # 이미 딕셔너리인 경우
                history.append(msg)
        
        return {
            'current_author': self.current_author,
            'waiting_for_clarification': self.waiting_for_clarification,
            'last_search_result': self.last_search_result,
            'conversation_history': history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WikiConversationState':
        """딕셔너리에서 객체 생성 (기존 코드 호환성을 위해)"""
        history = []
        for msg_data in data.get('conversation_history', []):
            history.append(ConversationMessage(
                role=msg_data.get('role', ''),
                message=msg_data.get('message', ''),
                timestamp=msg_data.get('timestamp', '')
            ))
        
        return cls(
            current_author=data.get('current_author'),
            waiting_for_clarification=data.get('waiting_for_clarification', False),
            last_search_result=data.get('last_search_result'),
            conversation_history=history
        )