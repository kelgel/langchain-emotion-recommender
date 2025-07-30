# from langchain_core.prompts import PromptTemplate
#
# emotion_prompt = PromptTemplate(
#     input_variables=["emotion", "retrieved_docs", "user_input"],
#     template="""
#     사용자의 감정은 '{emotion}'이고, 요청 내용은 다음과 같습니다:
#     "{user_input}"
#
#     아래는 관련 도서 설명입니다:
#     {retrieved_docs}
#
#     위 정보를 바탕으로 추천할 책을 3권 제시해주세요.
#     각 책마다 제목과 간단한 추천 이유를 포함하세요.
#     """
# )
