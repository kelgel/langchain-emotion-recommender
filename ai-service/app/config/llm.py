"""
llm.py
한 파일에 목적별로 필요한 LLM 객체 모두 정의
"""
import os
from langchain_chroma import Chroma
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set.")

#임베딩 모델 생성
embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")

# 벡터 DB 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # app/
CHROMA_DIR = os.path.join(BASE_DIR, '..', 'data', 'chroma_db')

# 벡터스토어 객체 생성
vectorstore = Chroma(
    collection_name="bookstore_collection",
    embedding_function=embedding_model,
    persist_directory=os.path.abspath(CHROMA_DIR)
)

# 목적별로 필요한 LLM 객체 정의
query_analysis_llm = ChatOpenAI(api_key=api_key, temperature=0.0)
intent_classify_llm = ChatOpenAI(api_key=api_key, temperature=0.0)
clarification_llm = ChatOpenAI(api_key=api_key, temperature=0.5)
recommendation_llm = ChatOpenAI(api_key=api_key, temperature=0.7)


