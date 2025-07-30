# from langchain_core.prompts import PromptTemplate
#
# genre_prompt = PromptTemplate(
#     input_variables=["genre", "retrieved_docs", "user_input"],
#     template="""
#     사용자가 요청한 장르는 '{genre}'이고, 요청 내용은 다음과 같습니다:
#     "{user_input}"
#
#     아래는 관련 도서 설명입니다:
#     {retrieved_docs}
#
#     위 정보를 바탕으로 추천할 책을 3권 제시해주세요.
#     같은 책 제목은 단 한번만 추천하세요.
#     각 책마다 제목과 간단한 추천 이유를 포함하세요.
#     """
# )
