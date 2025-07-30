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

# 모델 import를 위한 경로 설정
models_dir = os.path.join(os.path.dirname(current_dir), 'models')
sys.path.insert(0, models_dir)

from wiki_agent_response import WikiAgentResponse


class WikiSearchAgent:
    """위키피디아 검색 에이전트 클래스."""

    def __init__(self):
        """에이전트를 초기화하고 체인과 세션 상태를 설정."""
        # OpenAI 클라이언트 초기화 (Agent에서 리소스 관리)
        self.llm_client = None
        if OPENAI_AVAILABLE:
            try:
                self.llm_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            except Exception:
                pass
        
        # Chain에 LLM 클라이언트 전달 (의존성 주입)
        self.chain = WikiSearchChain(llm_client=self.llm_client)
        self.context = {}

    def process_with_context(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 쿼리를 컨텍스트와 함께 처리."""
        try:
            # 체인에서 처리 (컨텍스트 전달)
            result = self.chain.execute(query, context)
            
            # WikiAgentResponse 모델 사용
            if result['action'] == 'error':
                response = WikiAgentResponse.create_error(
                    message=result.get('message', ''),
                    error_details=result.get('error')
                )
            elif result['action'] == 'ask_clarification':
                response = WikiAgentResponse.create_clarification(
                    message=result.get('message', ''),
                    context_updated=True
                )
            else:
                response = WikiAgentResponse.create_success(
                    message=result.get('message', ''),
                    context_updated=True
                )
            
            # 에이전트의 내부 상태 업데이트 및 반환값에 컨텍스트 추가
            response_dict = response.to_dict()
            if 'update_context' in result:
                self.context.update(result['update_context'])
                response_dict['update_context'] = result['update_context']

            return response_dict
            
        except Exception as e:
            response = WikiAgentResponse.create_error(
                message='죄송합니다. 검색 중 오류가 발생했습니다. 다시 시도해주세요.',
                error_details=str(e)
            )
            return response.to_dict()


    def can_handle_query(self, query: str) -> bool:
        """이 에이전트가 주어진 쿼리를 처리할 수 있는지 판단 (키워드 기반)."""
        # 키워드 기반 판단만 사용
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
            'is_active': self.context.get('waiting_for_clarification', False),
            'current_author': self.context.get('current_author'),
            'conversation_turns': len(self.context.get('conversation_history', [])),
            'waiting_for_input': self.context.get('waiting_for_clarification', False)
        }


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

            # 에이전트 처리
            result = agent.process_with_context(user_input, agent.context)

            # 응답 출력
            print(f"\n에이전트: {result['message']}")

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