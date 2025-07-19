# check_vector_db.py - 벡터 데이터베이스 확인 도구
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

def check_vector_database():
    """벡터 데이터베이스 상태 확인"""
    persist_directory = "./chroma_db"
    
    print("🔍 벡터 데이터베이스 상태 확인")
    print(f"저장 위치: {os.path.abspath(persist_directory)}")
    
    # 디렉토리 존재 확인
    if not os.path.exists(persist_directory):
        print("❌ 벡터 데이터베이스가 생성되지 않았습니다.")
        return
    
    # 파일 목록 확인
    files = []
    for root, dirs, filenames in os.walk(persist_directory):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            file_size = os.path.getsize(file_path)
            files.append((file_path, file_size))
    
    print(f"\n📁 저장된 파일들:")
    total_size = 0
    for file_path, size in files:
        size_mb = size / (1024 * 1024)
        total_size += size
        print(f"  {file_path}: {size_mb:.2f} MB")
    
    print(f"\n💾 총 크기: {total_size / (1024 * 1024):.2f} MB")
    
    try:
        # 벡터스토어 로드 및 문서 수 확인
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        vectorstore = Chroma(
            collection_name="bookstore_collection",
            embedding_function=embeddings,
            persist_directory=persist_directory
        )
        
        # 샘플 검색으로 문서 수 추정
        test_results = vectorstore.similarity_search("test", k=1)
        
        if test_results:
            print("✅ 벡터 데이터베이스가 정상적으로 로드되었습니다.")
            
            # 컬렉션 정보 확인 (가능한 경우)
            try:
                # Chroma 내부 API 사용 (버전에 따라 다를 수 있음)
                collection = vectorstore._collection
                doc_count = collection.count()
                print(f"📊 총 문서 수: {doc_count}개")
            except:
                print("📊 문서 수는 직접 확인할 수 없습니다.")
        else:
            print("⚠️ 벡터 데이터베이스가 비어있거나 검색에 실패했습니다.")
            
    except Exception as e:
        print(f"❌ 벡터 데이터베이스 로드 실패: {e}")

def sample_search():
    """샘플 검색 테스트"""
    print("\n🔍 샘플 검색 테스트")
    persist_directory = "./chroma_db"
    
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        vectorstore = Chroma(
            collection_name="bookstore_collection",
            embedding_function=embeddings,
            persist_directory=persist_directory
        )
        
        # 다양한 검색어로 테스트
        test_queries = ["프로그래밍", "자바", "행복", "스트레스"]
        
        for query in test_queries:
            results = vectorstore.similarity_search(query, k=3)
            print(f"\n'{query}' 검색 결과: {len(results)}개")
            
            for i, doc in enumerate(results[:2], 1):  # 상위 2개만 표시
                metadata = doc.metadata
                doc_type = metadata.get('type', 'unknown')
                product_name = metadata.get('product_name', 'N/A')
                print(f"  {i}. [{doc_type}] {product_name}")
                
                if metadata.get('product_keywords'):
                    try:
                        import json
                        kw = json.loads(metadata['product_keywords'])
                        print(f"     제품키워드: {', '.join(kw)}")
                    except:
                        print(f"     제품키워드: {metadata['product_keywords'][:50]}...")
                if metadata.get('product_emotion_keywords'):
                    try:
                        import json
                        kw = json.loads(metadata['product_emotion_keywords'])
                        print(f"     상품감정: {', '.join(kw)}")
                    except:
                        print(f"     상품감정: {metadata['product_emotion_keywords'][:50]}...")
                if metadata.get('review_emotion_keywords'):
                    try:
                        import json
                        kw = json.loads(metadata['review_emotion_keywords'])
                        print(f"     리뷰감정: {', '.join(kw)}")
                    except:
                        print(f"     리뷰감정: {metadata['review_emotion_keywords'][:50]}...")
                    
    except Exception as e:
        print(f"❌ 검색 테스트 실패: {e}")

def main():
    """메인 실행 함수"""
    import sys
    
    check_vector_database()
    
    if len(sys.argv) > 1 and sys.argv[1] == "search":
        sample_search()

if __name__ == "__main__":
    main()