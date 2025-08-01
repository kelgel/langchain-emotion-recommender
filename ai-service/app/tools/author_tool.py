#작가 기반 추천 Tool

from langchain.tools import StructuredTool
from config.llm import  recommendation_llm, vectorstore
from prompts.recommend_prompt import recommend_prompt
from utils.formatters import format_recommendation_result_with_isbn, format_links_only, combine_response_with_links
from utils.fallback_data import fallback_books

def run_author_tool(author: str, user_input: str="")-> str:
    if not author:
        return "❗ 작가 정보를 입력해주세요. (예: 천선란, 김초엽 등)"

    # Retriever 구성
    # retriever = vectorstore.as_retriever(
    #     search_type="similarity_score_threshold",
    #     search_kwargs={
    #         "score_threshold": 0.75,
    #         "k": 3,
    #         "filter": {"author": author}
    #     }
    # )
    # mmr type
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 3,
            "fetch_k": 10,
            "filter": {"author": author},
            "lambda_mult": 0.7
        }
    )

    search_query = f"{author} 작가의 책"
    docs = retriever.invoke(search_query)

    if not docs:
        fallback = fallback_books.get("author", {}).get(author)
        if fallback:
            return f"❗검색 결과가 없어 작가 '{author}'의 기본 추천 도서를 드립니다:\n" + "\n".join(fallback)
        return "❌ 관련 도서를 찾지 못했어요. 다른 키워드로 시도해보세요."

    retrieved_docs = format_recommendation_result_with_isbn(docs)


    prompt = recommend_prompt.format(
        emotion="",
        genre="",
        author=author,
        keywords="",
        retrieved_docs=retrieved_docs
    )

    llm_result = recommendation_llm.invoke(prompt).content
    return combine_response_with_links(llm_result, docs)

author_tool = StructuredTool.from_function(
    name="AuthorRecommendationTool",
    func=run_author_tool,
    description="작가를 기반으로 추천하는 Tool 입니다."
)