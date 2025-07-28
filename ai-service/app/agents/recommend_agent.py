from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
import os
from config.llm import embedding_model, recommendation_llm

# 환경 변수 불러오기
load_dotenv()
# embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")
# recommendation_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# 벡터 DB 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # app/
CHROMA_DIR = os.path.join(BASE_DIR, '..', 'data', 'chroma_db')
vectorstore = Chroma(
    collection_name="bookstore_collection",
    embedding_function=embedding_model,
    persist_directory=os.path.abspath(CHROMA_DIR)
)

# 추천 프롬프트
recommend_prompt = PromptTemplate(
    input_variables=["emotion", "genre", "keywords", "retrieved_docs"],
    template="""
    당신은 감정 기반 도서 추천 챗봇입니다.

    사용자 요청 정보:
    - 감정(emotion): {emotion}
    - 장르(genre): {genre}
    - 키워드: {keywords}

    아래는 유사한 도서 설명들입니다:
    {retrieved_docs}

    {emotion}이 주어지지 않았다면, 장르에 어울리는 책을 추천해주세요. 감정이 없더라도 장르 기반으로 추천이 가능해야 합니다.
    주어진 정보를 바탕으로 최대 3권의 도서를 추천해주세요.
    각 책에 대해 제목과 간단한 추천 이유를 짧게 포함하세요.
    같은 책 제목은 한 번만 추천해주세요.
    """
)

# 추천 실행 함수
def run_recommend_agent(query_data: dict) -> str:
    emotion = query_data.get("emotion", "")
    genre = query_data.get("genre", "")
    keywords = query_data.get("keywords", [])
    keyword_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)

    # 검색 문장 구성
    search_query = f"{emotion} {genre} {keyword_str}".strip()
    #docs: list[Document] = vectorstore.similarity_search(search_query, k=3)

    # MMR 기반 리트리버 사용
    retirever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 3, "fetch_k":10, "lambda_mult": 0.7}
    )
    docs= retirever.invoke(search_query)

    if not docs:
        return "❌ 관련 도서를 찾지 못했어요. 다른 키워드로 시도해보세요."

    # 벡터 DB에서 검색된 내용 문자열로 변환
    retrieved_docs = "\n\n".join([f"{i+1}. {doc.page_content}" for i, doc in enumerate(docs)])

    # LLM 프롬프트 생성
    filled_prompt = recommend_prompt.format(
        emotion=emotion,
        genre=genre,
        keywords=keyword_str,
        retrieved_docs=retrieved_docs
    )

    # LLM 호출
    response = recommendation_llm.invoke(filled_prompt)

    return response.content


# 테스트용 실행 코드
if __name__ == "__main__":
    sample_query = {
        "emotion": "우울",
        "genre": "에세이",
        "keywords": ["위로", "삶", "희망"]
    }
    result = run_recommend_agent(sample_query)
    print("📚 추천 결과:\n", result)
