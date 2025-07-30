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

# 환경 자동 감지 및 ChromaDB 설정
def create_vectorstore():
    collection_name = "bookstore_collection"

    # Docker 환경 감지
    is_docker = (
            os.path.exists('/.dockerenv') or  # Docker 컨테이너 감지
            os.getenv('DOCKER_ENV') == 'true'  # 명시적 환경변수
    )

    if is_docker:
        print("🐳 Docker 환경 감지")
        # Docker에서는 ChromaDB 컨테이너와 공유하는 볼륨 사용
        persist_dir = "/app/data/chroma_db"

        # 디렉토리가 없으면 생성
        os.makedirs(persist_dir, exist_ok=True)

        # ChromaDB 볼륨 내부 구조에 맞게 경로 설정
        chroma_internal_path = os.path.join(persist_dir, "chroma.sqlite3")

        print(f"📁 ChromaDB 경로: {persist_dir}")

        try:
            return Chroma(
                collection_name=collection_name,
                embedding_function=embedding_model,
                persist_directory=persist_dir
            )
        except Exception as e:
            print(f"❌ Docker ChromaDB 연결 실패: {e}")
            # 대안: 임시 인메모리 DB 사용
            print("🔄 임시 인메모리 ChromaDB 사용")
            return Chroma(
                collection_name=collection_name,
                embedding_function=embedding_model
            )
    else:
        print("💻 로컬 환경 감지")
        # 로컬에서는 상대 경로 사용
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        persist_dir = os.path.join(BASE_DIR, '..', 'data', 'chroma_db')

        # 디렉토리 생성 확인
        os.makedirs(persist_dir, exist_ok=True)
        print(f"📁 ChromaDB 경로: {persist_dir}")

        return Chroma(
            collection_name=collection_name,
            embedding_function=embedding_model,
            persist_directory=persist_dir
        )

# 벡터스토어 객체 생성
try:
    vectorstore = create_vectorstore()
    print("✅ ChromaDB 연결 완료")
except Exception as e:
    print(f"❌ ChromaDB 연결 실패: {e}")
    # 임시 방편으로 인메모리 DB 사용
    vectorstore = Chroma(
        collection_name="bookstore_collection",
        embedding_function=embedding_model
    )
    print("⚠️ 임시 인메모리 ChromaDB 사용 중")

# 목적별로 필요한 LLM 객체 정의
query_analysis_llm = ChatOpenAI(api_key=api_key, temperature=0.0)
intent_classify_llm = ChatOpenAI(api_key=api_key, temperature=0.0)
clarification_llm = ChatOpenAI(api_key=api_key, temperature=0.5)
recommendation_llm = ChatOpenAI(api_key=api_key, temperature=0.7)


