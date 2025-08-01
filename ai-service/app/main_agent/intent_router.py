from agents.recommend_agent import run_recommend_agent
from agents.wiki_search_agent import WikiSearchAgent

def route_intent(intent: str, query_data: dict, current_agent: str = None, session: dict = None, agent_instances: dict = None) -> str:
    """현재 세션의 에이전트 정보를 고려하여 라우팅"""
    
    if agent_instances is None:
        agent_instances = {}
    if intent == "recommendation":
        print(f"라우팅: recommendation 에이전트 호출 (현재 에이전트: {current_agent})")

        # ✅ 세션 상태에 recommend로 설정
        if session is not None:
            session["current_agent"] = "recommend"

        return run_recommend_agent(query_data)

    elif intent == "info":
        print(f"라우팅: wiki 에이전트 호출 (현재 에이전트: {current_agent})")
        
        # 위키 에이전트 인스턴스 가져오기 또는 생성
        if 'wiki' not in agent_instances:
            print("새로운 위키 에이전트 인스턴스 생성")
            agent_instances['wiki'] = WikiSearchAgent()
        wiki_agent = agent_instances['wiki']

        # 세션 컨텍스트 준비
        context = {}
        if session:
            # 중요: 에이전트의 내부 컨텍스트를 직접 수정하지 않도록 복사본을 사용
            context = wiki_agent.context.copy()
            context['conversation_history'] = session.get("conversation_history", [])

        # 원문 질문 (user_input)을 그대로 사용
        search_query = (
                query_data.get("user_input")
                or query_data.get("original_input")
                or "정보를 입력해주세요."
        )
        print(f"[DEBUG] 원본 쿼리 전달: {search_query}")
            
        result = wiki_agent.process_with_context(search_query, context)
        return result
    else:
        return "죄송합니다. 해당 요청은 아직 지원하지 않습니다."
