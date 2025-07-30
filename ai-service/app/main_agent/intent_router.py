from agents.recommend_agent import run_recommend_agent
from agents.wiki_search_agent import WikiSearchAgent

# 전역에서 한 번만 생성
wiki_agent = WikiSearchAgent()

def route_intent(intent: str, query_data: dict) -> str:
    if intent == "recommendation":
        return run_recommend_agent(query_data)
    elif intent == "info":  # ✅ intent가 "info"일 때 위키 에이전트 호출
        # 원문 질문 (user_input) 추출 – 없으면 기본 문구
        user_query = (
                query_data.get("original_input")
                or query_data.get("raw_input")
                or query_data.get("user_input")
                or "작가 정보를 입력해주세요."
        )
        result = wiki_agent.process(user_query)
        return result.get("message", "검색 결과를 가져오지 못했습니다.")
    else:
        return "죄송합니다. 해당 요청은 아직 지원하지 않습니다."
