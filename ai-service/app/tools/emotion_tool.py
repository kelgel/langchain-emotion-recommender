from langchain.tools import StructuredTool
from config.llm import recommendation_llm, vectorstore
from prompts.recommend_prompt import recommend_prompt
#from prompts.emotion_prompt import emotion_prompt
from utils.formatters import format_recommendation_result_with_isbn, format_links_only, combine_response_with_links
from utils.fallback_data import fallback_books

def run_emotion_tool(emotion: str, user_input: str = "") -> str:
    if not emotion:
        return "❗ 감정 정보를 입력해주세요. (예: 우울, 행복 등)"
    # 감정 기반 retriever 구성
    # mmr type
    # retriever = vectorstore.as_retriever(
    #     search_type="mmr",
    #     search_kwargs={
    #         "k": 3,
    #         "fetch_k": 10,
    #         "lambda_mult": 0.7
    #     }
    # )
    # search_query = f"{emotion} {user_input}"  # 또는 그냥 user_input만 사용
    # docs = retriever.invoke(search_query)

    # similarity score threshold type
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "score_threshold": 0.75,
            "k": 3
        }
    )
    search_query = f"'{user_input}'라는 요청에서 '{emotion}' 감정에 어울리는 책"
    docs = retriever.invoke(search_query)
    # for doc in docs:
    #     print(doc.metadata)

    if not docs:
        fallback = fallback_books.get("emotion", {}).get(emotion)
        if fallback:
            return f"❗'{emotion}' 감정에 어울리는 기본 도서를 추천합니다:\n" + "\n".join(fallback)
        return f"❌ '{emotion}' 감정에 맞는 책을 찾지 못했어요. 다른 감정을 입력해보세요."
    # 검색 결과 문서 구성
    #retrieved_docs = "\n\n".join([f"{i+1}. {doc.page_content}" for i, doc in enumerate(docs)])
    #url 형식에 맞춘 결과 반환 - 우선 감정 툴에만 추가
    retrieved_docs = format_recommendation_result_with_isbn(docs)

    prompt = recommend_prompt.format(
        emotion=emotion,
        genre="",  # 비워도 됨
        author="",
        keywords="",  # 필요시 추출값 사용
        retrieved_docs=retrieved_docs
    )

# prompt = emotion_prompt.format(
    #     emotion=emotion,
    #     user_input=user_input,
    #     retrieved_docs=retrieved_docs
    # )
    # LLM  호출 및 응답 반환
    llm_result = recommendation_llm.invoke(prompt).content
    return combine_response_with_links(llm_result, docs)


# LangChain Tool 객체로 등록
emotion_tool = StructuredTool.from_function(
    name="EmotionRecommendationTool",
    func=run_emotion_tool,
    description="감정을 기반으로 도서를 추천하는 Tool 입니다."
)