"""
main_agent.py
main_agent 메인 에이전트-쿼리 라우팅
"""

from langchain.chains import LLMChain
from chains import query_analysis_chain, intent_classify_chain

user_input = "채식주의자 책을 쓴 사람에 대해서 알고싶어" #"우울하니까 위로가 되는 에세이를 추천해줘"

#query_analysis_response = query_analysis_chain.run(user_input=user_input)
# 최신 방식: .invoke() 사용, dict로 전달
query_analysis_response = query_analysis_chain.invoke({"user_input": user_input})
print(query_analysis_response)

#intent_classify_response = intent_classify_chain.run(user_input=user_input)
intent_classify_response = intent_classify_chain.invoke({"user_input": user_input})
print(intent_classify_response)
