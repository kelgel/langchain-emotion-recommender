from langchain.tools import StructuredTool
from config.llm import recommendation_llm, vectorstore
# from prompts.genre_prompt import genre_prompt
from prompts.recommend_prompt import recommend_prompt
from utils.formatters import format_recommendation_result_with_isbn, format_links_only, combine_response_with_links
from utils.fallback_data import fallback_books

def run_genre_tool(genre: str, user_input: str = "") -> str:
    if not genre:
        return "❗ 장르 정보를 입력해주세요. (예: 소설, 에세이 등)"

    # Retriever 구성 - similarity score threshold type
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "score_threshold": 0.75,
            "k": 3
        }
    )
    # retriever = vectorstore.as_retriever(
    #     search_type="mmr",
    #     search_kwargs={
    #         "k": 3,
    #         "fetch_k": 10,
    #         "lambda_mult": 0.7
    #     }
    # )

    search_query = f"{user_input} 요청에 따른 {genre} 장르의 책"
    docs = retriever.invoke(search_query)

    if not docs:
        fallback = fallback_books.get("genre", {}).get(genre)
        if fallback:
            return f"❗'{genre}' 장르에 대한 기본 추천 도서를 드립니다:\n" + "\n".join(fallback)
        return "❌ 관련 도서를 찾지 못했어요. 다른 키워드로 시도해보세요."

    # 검색 결과 구성
    #retrieved_docs = "\n\n".join([f"{i+1}. {doc.page_content}" for i, doc in enumerate(docs)])
    retrieved_docs = format_recommendation_result_with_isbn(docs)


    # 프롬프트 구성
    # prompt = genre_prompt.format(
    #     genre=genre,
    #     user_input=user_input,
    #     retrieved_docs=retrieved_docs
    # )
    prompt = recommend_prompt.format(
        emotion="",
        genre=genre,
        author="",
        keywords="",
        retrieved_docs=retrieved_docs
    )

    # LLM 호출 및 응답 반환
    llm_result = recommendation_llm.invoke(prompt).content
    return combine_response_with_links(llm_result, docs)

# LangChain Tool 객체로 등록
genre_tool = StructuredTool.from_function(
    name="GenreRecommendationTool",
    func=run_genre_tool,
    description="장르를 기반으로 도서를 추천하는 Tool 입니다."
)
