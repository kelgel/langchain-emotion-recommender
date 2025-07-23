# -*- coding: utf-8 -*-
"""
위키서치 에이전트 대화형 테스트
터미널에서 직접 대화할 수 있는 인터페이스
"""

import sys
import os

# 프로젝트 루트 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.agents.wiki_search_agent import WikiSearchAgent

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