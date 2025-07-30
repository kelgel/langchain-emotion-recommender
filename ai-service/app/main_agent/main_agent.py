"""
main_agent.py
main_agent 메인 에이전트-쿼리 라우팅
"""
from chromadb.app import app
from dotenv import load_dotenv

# import app.main_agent.intent_router.route_intent
# from chains import query_analysis_chain, intent_classify_chain
# from chains.clarification_chain import get_clarification_chain
# from utils.clarification_checker import needs_clarification
# from prompts.clarification_prompt import get_clarification_prompt
# from config.llm import clarification_llm
# from dotenv import load_dotenv


load_dotenv()

async def run_pipeline(user_input):
    while True:

        # 1. 질의 분석
        query = app.chains.query_analysis_chain.invoke({"user_input": user_input})
        print(f"📌 분석 결과: {query}")

        # 2. 화행 분류
        intent = app.chains.intent_classify_chain.invoke({"user_input": user_input})
        print(f"📌 분류된 의도: {intent}")

        # 3. 필수 정보 누락 시 clarification loop
        while app.utils.needs_clarification(intent, query):
            # [1] 프롬프트 준비
            prompt = app.prompts.get_clarification_prompt(intent)
            prompt_string = prompt.format(**query)

            # [2] LLM 실행 → 자연어 메시지
            llm_response = app.config.llm.clarification_llm.invoke(prompt_string)
            print(f"❓ 추가 질문: {llm_response.content}")  # 여긴 자연어 출력

            user_input = input("↩️ 사용자 응답: ")
            query = app.chains.query_analysis_chain.invoke({"user_input": user_input})
            print(f"📌 재분석 결과: {query}")

        # 4. 최종 intent 처리
        response = app.main_agent.intent_router.route_intent(intent, query)
        print(f"\n🤖 챗봇 응답:\n{response}")
        break

if __name__ == "__main__":
    run_pipeline()