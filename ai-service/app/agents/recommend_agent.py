from langchain_core.prompts import PromptTemplate
from config.llm import recommendation_llm, embedding_model
from langchain_chroma import Chroma

# # 1. 벡터 DB 로드 (Chroma)
# import os
#
# # __file__ 기준으로 절대 경로 생성
# CHROMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma_db"))
#
# db = Chroma(
#     persist_directory=CHROMA_PATH,
#     embedding_function=embedding_model
# )
#
# print(f"📁 Chroma 경로: {CHROMA_PATH}")
# print("📄 포함 파일들:", os.listdir(CHROMA_PATH))


recommend_prompt = PromptTemplate(
    input_variables = ["emotion", "genre", "keywords"],
    template="""
    너는 서점 사이트의 도서 추천 AI야.

    아래 정보가 주어졌을 때, 관련된 도서를 최대 3권 추천해줘:
    - 감정: {emotion}
    - 장르: {genre}
    - 키워드: {keywords}
    
    가능한 정보만 활용해서 도서를 추천해.
    추천할 정보가 부족하면 유사 키워드 기반으로 유추해서 추천해도 돼.
    """
)

def run_recommend_agent(query_data: dict) -> str:
    emotion = query_data.get("emotion")
    genre = query_data.get("genre")
    keywords = query_data.get("keywords", [])  # 또는 "" 로 초기화
    keyword_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)

    prompt = recommend_prompt.format(
        emotion=emotion,
        genre=genre,
        keywords=keyword_str
    )
    response = recommendation_llm.invoke(prompt)

    return response.content


