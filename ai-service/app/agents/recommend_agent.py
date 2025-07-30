from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from dotenv import load_dotenv
import os
from config.llm import recommendation_llm, vectorstore
from prompts.recommend_prompt import recommend_prompt
from tools.emotion_tool import run_emotion_tool
from tools.genre_tool import run_genre_tool
# 환경 변수 불러오기
load_dotenv()

# 추천 실행 함수
def run_recommend_agent(query_data: dict) -> str:
    emotion = query_data.get("emotion", "")
    genre = query_data.get("genre", "")
    keywords = query_data.get("keywords", [])
    keyword_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)
    user_input = query_data.get("user_input", "")

    # ✅ 감정만 있는 경우
    if emotion:
        return run_emotion_tool(emotion=emotion, user_input=user_input)

    if genre:
        return run_genre_tool(genre=genre, user_input=user_input)

    # ❌ 조건 부족
    return "❗추천을 위해 감정, 장르, 키워드 중 하나 이상이 필요합니다."

if __name__ == "__main__":
    # sample_query = {
    #     "emotion": "우울",
    #     "genre": None,
    #     "keywords": [],
    #     "user_input": "우울할 때 위로가 되는 책 추천해줘"
    # }
    sample_query = {
        "emotion": "",
        "genre": "에세이",
        "keywords": [],
        "user_input": "에세이 추천"
    }
    print(run_recommend_agent(sample_query))


#     # 검색 문장 구성
#     search_query = f"{emotion} {genre} {keyword_str}".strip()
#     #docs: list[Document] = vectorstore.similarity_search(search_query, k=3)
#
#     # MMR 기반 리트리버 사용
#     retirever = vectorstore.as_retriever(
#         search_type="mmr",
#         search_kwargs={"k": 3, "fetch_k":10, "lambda_mult": 0.7}
#     )
#     docs= retirever.invoke(search_query)
#
#     if not docs:
#         return "❌ 관련 도서를 찾지 못했어요. 다른 키워드로 시도해보세요."
#
#     # 벡터 DB에서 검색된 내용 문자열로 변환
#     retrieved_docs = "\n\n".join([f"{i+1}. {doc.page_content}" for i, doc in enumerate(docs)])
#
#     # LLM 프롬프트 생성
#     filled_prompt = recommend_prompt.format(
#         emotion=emotion,
#         genre=genre,
#         keywords=keyword_str,
#         retrieved_docs=retrieved_docs
#     )
#
#     # LLM 호출
#     response = recommendation_llm.invoke(filled_prompt)
#
#     return response.content
#
#
# # 테스트용 실행 코드
# if __name__ == "__main__":
#     sample_query = {
#         "emotion": "우울",
#         "genre": "에세이",
#         "keywords": ["위로", "삶", "희망"]
#     }
#     result = run_recommend_agent(sample_query)
#     print("📚 추천 결과:\n", result)
