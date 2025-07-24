#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
위키피디아 검색 에이전트 - Agent 계층
세션 관리와 다른 에이전트와의 협업을 담당
"""

from typing import Dict, Any
import sys
import os
import json

# OpenAI 모듈 안전하게 import
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

# .env 파일 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 명시적 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
chains_dir = os.path.join(os.path.dirname(current_dir), 'chains')

sys.path.insert(0, chains_dir)

from wiki_search_chain import WikiSearchChain


class WikiSearchAgent:
    """위키피디아 검색 에이전트 클래스."""

    def __init__(self):
        """에이전트를 초기화하고 체인과 세션 상태를 설정."""
        self.chain = WikiSearchChain()
        self.conversation_state = {
            'current_author': None,
            'waiting_for_clarification': False,
            'last_search_result': None,
            'conversation_history': []
        }
        
        # OpenAI 클라이언트 초기화
        self.llm_client = None
        if OPENAI_AVAILABLE:
            try:
                self.llm_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            except Exception:
                pass

    def process(self, query: str) -> Dict[str, Any]:
        """사용자 쿼리를 처리하고 세션 상태를 관리."""
        try:
            # 대화 히스토리에 쿼리 추가
            self._add_to_history('user', query)
            
            # 체인에서 처리
            result = self.chain.execute(query, self.conversation_state)
            
            # 컨텍스트 업데이트
            if result.get('update_context'):
                # 리셋 신호가 있으면 완전히 초기화
                if result['update_context'].get('reset_conversation'):
                    self.reset_conversation()
                    # 새로운 작가 정보로 업데이트
                    if 'current_author' in result['update_context']:
                        self.conversation_state['current_author'] = result['update_context']['current_author']
                    if 'waiting_for_clarification' in result['update_context']:
                        self.conversation_state['waiting_for_clarification'] = result['update_context']['waiting_for_clarification']
                else:
                    self._update_conversation_state(result['update_context'])
            
            # 응답 히스토리에 추가
            self._add_to_history('assistant', result.get('message', ''))
            
            # 결과 포맷팅
            return {
                'success': result['action'] != 'error',
                'message': result.get('message', ''),
                'action': result['action'],
                'should_continue': result['action'] in ['ask_clarification', 'show_result'],
                'context_updated': bool(result.get('update_context')),
                'agent_name': 'wiki_search'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': '죄송합니다. 검색 중 오류가 발생했습니다. 다시 시도해주세요.',
                'action': 'error',
                'should_continue': False,
                'context_updated': False,
                'error': str(e),
                'agent_name': 'wiki_search'
            }

    def get_conversation_state(self) -> Dict[str, Any]:
        """현재 대화 상태를 반환."""
        return self.conversation_state.copy()

    def reset_conversation(self):
        """대화 상태를 초기화."""
        self.conversation_state = {
            'current_author': None,
            'waiting_for_clarification': False,
            'last_search_result': None,
            'conversation_history': []
        }

    def is_conversation_active(self) -> bool:
        """현재 대화가 진행 중인지 확인."""
        return self.conversation_state.get('waiting_for_clarification', False)

    def can_handle_query(self, query: str) -> bool:
        """이 에이전트가 주어진 쿼리를 처리할 수 있는지 판단 (LLM 기반)."""
        # 현재 대화가 진행 중이면 우선적으로 처리
        if self.is_conversation_active():
            return True
        
        if self.llm_client:
            return self._llm_can_handle_query(query)
        else:
            return self._fallback_can_handle_query(query)
    
    def _llm_can_handle_query(self, query: str) -> bool:
        """LLM을 사용한 쿼리 처리 가능 여부 판단."""
        try:
            system_prompt = """당신은 쿼리 라우터입니다. 주어진 질문이 위키피디아 검색 에이전트(작가, 인물 정보 검색)가 처리해야 할 질문인지 판단하세요.

위키피디아 검색 에이전트가 처리하는 질문들:
- 작가, 소설가, 시인에 대한 정보
- 인물의 학력, 출생, 작품 정보
- "누구인지 알려줘" 같은 인물 정보 요청

다른 에이전트가 처리하는 질문들:
- 주문 조회, 배송 상태
- 상품 재고, 가격 정보
- 결제, 환불 관련

JSON 형식으로 응답하세요:
{
    "can_handle": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "판단 이유"
}"""
            
            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"질문: {query}"}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('can_handle', False)
            
        except Exception as e:
            # LLM 실패시 폴백
            return self._fallback_can_handle_query(query)
    
    def _fallback_can_handle_query(self, query: str) -> bool:
        """기존 키워드 기반 처리 가능 여부 판단 (폴백용)."""
        author_keywords = ['작가', '소설가', '시인', '저자', '작품', '알려줘', '정보', '누구']
        
        # 기본 키워드 체크
        if any(keyword in query.lower() for keyword in author_keywords):
            return True
        
        # 인물명 + 질문 패턴 체크 (예: "제인오스틴은 언제 죽었어")
        person_question_patterns = ['언제', '어디', '태어', '죽었', '사망', '대학', '학교', '출생']
        query_lower = query.lower()
        
        # 인물명이 포함되어 있고 + 질문 패턴이 있으면 처리 가능
        if any(pattern in query_lower for pattern in person_question_patterns):
            # 간단한 휴리스틱: 대문자나 외국 이름 패턴이 있으면 인물명일 가능성
            if (any(char.isupper() for char in query) or 
                any(name in query for name in ['스틴', '러키', '영하', '오웰', '하루키', '카미']) or
                len([char for char in query if char.isupper()]) >= 2):  # 대문자가 2개 이상
                return True
        
        return False

    def get_status_info(self) -> Dict[str, Any]:
        """에이전트 상태 정보를 반환."""
        return {
            'agent_name': 'wiki_search',
            'is_active': self.is_conversation_active(),
            'current_author': self.conversation_state.get('current_author'),
            'conversation_turns': len(self.conversation_state.get('conversation_history', [])),
            'waiting_for_input': self.conversation_state.get('waiting_for_clarification', False)
        }

    def _update_conversation_state(self, updates: Dict[str, Any]):
        """대화 상태를 업데이트."""
        for key, value in updates.items():
            if key in self.conversation_state:
                self.conversation_state[key] = value

    def _add_to_history(self, role: str, message: str):
        """대화 히스토리에 메시지를 추가."""
        if 'conversation_history' not in self.conversation_state:
            self.conversation_state['conversation_history'] = []
        
        self.conversation_state['conversation_history'].append({
            'role': role,
            'message': message,
            'timestamp': self._get_current_timestamp()
        })
        
        # 히스토리 길이 제한 (최근 20개만 유지)
        if len(self.conversation_state['conversation_history']) > 20:
            self.conversation_state['conversation_history'] = \
                self.conversation_state['conversation_history'][-20:]

    def _get_current_timestamp(self) -> str:
        """현재 타임스탬프를 문자열로 반환."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def interactive_chat():
    """대화형 위키서치 에이전트"""
    agent = WikiSearchAgent()

    print("=" * 60)
    print("위키서치 에이전트 대화 시작")
    print("=" * 60)
    print("작가에 대해 물어보세요! (종료하려면 'quit' 또는 'exit' 입력)")
    print("예시: '한강 작가 알려줘', '희랍어 시간 작가 정보'")
    print("-" * 60)

    while True:
        try:
            # 사용자 입력
            user_input = input("\n당신: ").strip()

            # 종료 명령어 체크
            if user_input.lower() in ['quit', 'exit', '종료', '나가기']:
                print("\n대화를 종료합니다. 안녕히 계세요!")
                break

            # 빈 입력 체크
            if not user_input:
                print("메시지를 입력해주세요.")
                continue

            # 리셋 명령어
            if user_input.lower() in ['reset', '리셋', '새대화']:
                agent.reset_conversation()
                print("대화 상태가 초기화되었습니다.")
                continue

            # 에이전트 처리
            result = agent.process(user_input)

            # 응답 출력
            print(f"\n에이전트: {result['message']}")

            # 상태 정보 (디버깅용)
            if agent.is_conversation_active():
                print("(대화 진행 중...)")

        except KeyboardInterrupt:
            print("\n\n대화를 종료합니다. 안녕히 계세요!")
            break
        except Exception as e:
            print(f"\n오류가 발생했습니다: {e}")
            print("다시 시도해주세요.")


if __name__ == "__main__":
    try:
        interactive_chat()
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
        interactive_chat()