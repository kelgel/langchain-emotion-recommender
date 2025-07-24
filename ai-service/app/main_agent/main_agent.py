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

load_dotenv()

# def run_pipeline(user_input: str):
#     #1. 질의 분석 - 감정/장르/키워드 추출
#     query_analysis = query_analysis_chain.invoke({"user_input": user_input})
#     print(f"📌 분석 결과: {query_analysis}")
#
#     #2. 화행 분류
#     intent = intent_classify_chain.invoke({"user_input": user_input})
#     print(f"📌 분류된 의도: {intent}")
#
#     #3. 필수 키워드 누락 여부 검사 - True면 clarification_prompt로 재질문 진행
#     if needs_clarification(intent, query_analysis):
#         clarification_chain = get_clarification_chain(intent)
#         clarification_message = clarification_chain.invoke(query_analysis)
#         print(f"❓ {clarification_message}")
#
#
# if __name__ == "__main__":
#     user_input = input("사용자 질문: ")
#     result = run_pipeline(user_input)
#     print("\n🤖 챗봇 응답:\n", result)

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
            # clarification_chain = get_clarification_chain(intent)
            # clarification_message = clarification_chain.invoke(query)
            # print(f"❓ 추가 질문: {clarification_message.content}")
            #print(f"❓ 추가 질문: {clarification_message.get('content')}")

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
        route_intent(intent, query)
        #print(f"\n🤖 챗봇 응답:\n{response}")
        #break

if __name__ == "__main__":
    run_pipeline()