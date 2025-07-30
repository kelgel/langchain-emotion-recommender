
"""
main_agent.py
main_agent 메인 에이전트-쿼리 라우팅
"""

from main_agent.intent_router import route_intent
from chains import query_analysis_chain, intent_classify_chain
from chains.clarification_chain import get_clarification_chain
from utils.clarification_checker import needs_clarification
from prompts.clarification_prompt import get_clarification_prompt
from config.llm import clarification_llm
from dotenv import load_dotenv
from typing import Dict, Any, List

load_dotenv()

# 세션 관리 헬퍼 함수들
def init_session(session: Dict[str, Any]):
    """세션 초기화"""
    if "conversation_history" not in session:
        session["conversation_history"] = []
    if "current_agent" not in session:
        session["current_agent"] = None

def add_message_to_session(session: Dict[str, Any], role: str, content: str):
    """대화 히스토리에 메시지 추가"""
    session["conversation_history"].append({
        "role": role,
        "content": content
    })

def should_switch_agent(session: Dict[str, Any], current_intent: str) -> bool:
    """에이전트 전환 판단"""
    current_agent = session.get("current_agent")
    
    # 첫 번째 요청이면 무조건 설정 필요
    if not current_agent:
        return True
    
    # intent에 따른 적절한 에이전트 매핑
    intent_to_agent = {
        "info": "wiki",
        "recommendation": "recommend"
    }
    
    target_agent = intent_to_agent.get(current_intent)
    
    # 타겟 에이전트가 현재 에이전트와 다르면 전환
    return target_agent != current_agent

# FastAPI 연결용
def run_main_agent(user_input: str, session: Dict[str, Any], agent_instances: Dict[str, Any]):
    # 세션 초기화
    init_session(session)
    
    # 대화 히스토리에 사용자 메시지 추가
    add_message_to_session(session, "user", user_input)
    
    # 대화 히스토리를 포함한 컨텍스트 구성
    conversation_context = ""
    if session.get("conversation_history"):
        recent_history = session["conversation_history"][-6:]
        for msg in recent_history:
            conversation_context += f"{msg['role']}: {msg['content']}\n"
    
    # 쿼리 및 의도 분석
    query = query_analysis_chain.invoke({
        "user_input": user_input,
        "conversation_history": conversation_context if conversation_context else "이전 대화가 없습니다."
    })
    intent = intent_classify_chain.invoke({
        "user_input": user_input,
        "conversation_history": conversation_context if conversation_context else "이전 대화가 없습니다."
    })

    print("user_input", user_input)
    print("conversation_context:", conversation_context)
    print("query", query)
    print("intent", intent)
    print("session keys:", list(session.keys()))
    print("conversation_history:", session.get("conversation_history", []))
    print("current_agent:", session.get("current_agent"))

    # intent 유효성 검사
    valid_intents = ["info", "recommendation"]
    if intent not in valid_intents:
        clarification_msg = "도서 추천을 원하시나요, 아니면 작가 정보를 원하시나요?"
        add_message_to_session(session, "assistant", clarification_msg)
        return {
            "clarification_needed": True, "message": clarification_msg,
            "query": query, "intent": "unclear",
        }

    # 에이전트 전환 여부 판단
    if should_switch_agent(session, intent):
        print(f"[DEBUG] 에이전트 전환 필요. Clarification 확인.")
        # 새 에이전트이므로 정보가 부족한지 확인
        if needs_clarification(intent, query):
            prompt = get_clarification_prompt(intent).format(**query)
            llm_response = clarification_llm.invoke(prompt)
            add_message_to_session(session, "assistant", llm_response.content)
            return {
                "clarification_needed": True, "message": llm_response.content,
                "query": query, "intent": intent,
            }
        
        # 새 에이전트로 전환
        target_agent = {"info": "wiki", "recommendation": "recommend"}[intent]
        session["current_agent"] = target_agent
        print(f"에이전트 전환: {target_agent}")
    
    # 에이전트에게 라우팅
    current_agent_name = session.get("current_agent")
    query["user_input"] = user_input
    response_result = route_intent(intent, query, current_agent_name, session, agent_instances)
    
    # 컨텍스트 업데이트
    if isinstance(response_result, dict) and "update_context" in response_result:
        session.update(response_result["update_context"])

    # 응답 메시지 추출
    response_message = response_result.get("message", "오류가 발생했습니다.") if isinstance(response_result, dict) else response_result

    # 봇 응답을 세션 히스토리에 추가
    add_message_to_session(session, "assistant", response_message)
    
    return {
        "clarification_needed": isinstance(response_result, dict) and response_result.get("action") == "ask_clarification",
        "response": response_message,
        "query": query,
        "intent": intent,
    }


#콘솔 테스트용
def run_pipeline():
    while True:
        user_input = input("💬 사용자 질문: ")

        # 1. 질의 분석
        query = query_analysis_chain.invoke({"user_input": user_input})
        print(f"📌 분석 결과: {query}")

        # 2. 화행 분류
        intent = intent_classify_chain.invoke({"user_input": user_input})
        print(f"📌 분류된 의도: {intent}")

        # 3. 필수 정보 누락 시 clarification loop
        while needs_clarification(intent, query):
            # [1] 프롬프트 준비
            prompt = get_clarification_prompt(intent)
            prompt_string = prompt.format(**query)

            # [2] LLM 실행 → 자연어 메시지
            llm_response = clarification_llm.invoke(prompt_string)
            print(f"❓ 추가 질문: {llm_response.content}")  # 여긴 자연어 출력

            user_input = input("↩️ 사용자 응답: ")
            query = query_analysis_chain.invoke({"user_input": user_input})
            print(f"📌 재분석 결과: {query}")

        # 4. 최종 intent 처리
        query["user_input"] = user_input
        response = route_intent(intent, query)
        print(f"\n🤖 챗봇 응답:\n{response}")
        break

if __name__ == "__main__":
    run_pipeline()
