#감정,장르,작가,키워드를 조합해서 추천하는 Tool

from langchain.tools import StructuredTool
from config.llm import recommendation_llm, vectorstore
from prompts.recommend_prompt import recommend_prompt
from utils.formatters import format_recommendation_result_with_isbn, format_links_only, combine_response_with_links
from utils.fallback_data import fallback_books

def run_hybrid_tool(info: dict) -> str:
    emotion = str(info.get("emotion") or "")
    genre = str(info.get("genre") or "")
    author = str(info.get("author") or "")
    keywords = info.get("keywords") or []

    query_parts = []
    if emotion:
        query_parts.append(f"감정: {emotion}")
    if genre:
        query_parts.append(f"장르: {genre}")
    if author:
        query_parts.append(f"작가: {author}")
    if keywords:
        keyword_str = " ".join([str(k) for k in keywords if k])
        query_parts.append(f"키워드: {keyword_str}")

    query_summary = ", ".join(query_parts)

# vectorstore로 복합 쿼리 검색
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 3,
            "fetch_k": 10,
            "lambda_mult": 0.7
        }
    )
    docs = retriever.invoke(query_summary)

    if not docs:
        fallback = fallback_books.get("hybrid")
        if fallback:
            return f"❗조건({query_summary})에 맞는 책이 없어 기본 도서를 추천합니다:\n" + "\n".join(fallback)
        return f"❌ 관련 도서를 찾지 못했어요. (조건: {query_summary})"

    #검색 결과 구성
    retrieved_docs = format_recommendation_result_with_isbn(docs)

    prompt = recommend_prompt.format(
        emotion=emotion,
        genre=genre,
        author=author,
        keywords=query_summary,
        retrieved_docs=retrieved_docs
    )

    llm_result = recommendation_llm.invoke(prompt).content
    return combine_response_with_links(llm_result, docs)

hybrid_tool = StructuredTool.from_function(
    name="HybridRecommendationTool",
    func=run_hybrid_tool,
    description="감정이나 장르, 작가, 키워드 등을 조합해서 추천하는 Tool 입니다."
)