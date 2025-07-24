# from agents.recommend_agent import run_recommendation_agent
# from agents.order_agent import run_order_agent
# from agents.stock_agent import run_stock_agent
#
# def route_intent(intent: str, query_data: dict) -> str:
#     if intent == "recommendation":
#         return run_recommendation_agent(query_data)
#     elif intent == "order_check":
#         return run_order_agent(query_data)
#     elif intent == "stock_check":
#         return run_stock_agent(query_data)
#     else:
#         return "죄송합니다. 해당 요청은 아직 지원하지 않습니다."

def route_intent(intent: str, query_data: dict):
    if intent == "recommendation":
        print("recommendation agent")
    elif intent == "info":
        print("info agent")
    elif intent == "order_check":
        print("order agent")
    elif intent == "stock_check":
        print("stock agent")
    else:
        print("죄송합니다. 해당 요청은 아직 지원하지 않습니다.")

