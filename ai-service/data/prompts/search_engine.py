# search_engine.py - AI 기반 도서 추천 검색 엔진
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv
import json

# .env 파일에서 환경변수 로드
load_dotenv()

# OpenAI API 키 확인
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("OPENAI_API_KEY 환경변수를 설정해주세요.")

class BookRecommendationEngine:
    def __init__(self, persist_directory=None):
        """검색 엔진 초기화"""
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        self.llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")
        
        # ChromaDB 경로 설정 - 프로젝트 구조에 맞게 수정
        if persist_directory is None:
            # 현재 파일 위치에서 데이터 디렉토리로 상대 경로 설정
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.dirname(current_dir)  # prompts의 부모 = data
            persist_directory = os.path.join(data_dir, "chroma_db")
        
        # 벡터스토어 로드
        self.vectorstore = Chroma(
            collection_name="bookstore_collection",
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )
        
        # 추천 프롬프트 템플릿
        self.recommendation_prompt = PromptTemplate.from_template("""
        너는 AI 기반 도서 추천 전문가야. 사용자의 질문과 검색된 도서 정보를 바탕으로 개인화된 추천을 제공해줘.

        사용자 질문: {query}

        검색된 도서 정보:
        {search_results}

        **추천 가이드라인:**
        1. 사용자의 감정 상태와 니즈를 파악해서 적절한 도서를 추천해라
        2. 각 도서의 감정 키워드와 제품 키워드를 고려해서 매칭해라
        3. 가격, 저자, 카테고리 정보도 함께 제공해라
        4. 추천 이유를 명확하게 설명해라
        5. 최대 5권까지 추천해라

        **응답 형식:**
        ## 📚 당신을 위한 도서 추천

        ### 1. [도서명] - [저자]
        - **가격**: [가격]원
        - **카테고리**: [카테고리]  
        - **추천 이유**: [구체적인 추천 이유]
        - **감정 매칭**: [해당 감정 키워드들]

        ### 2. [도서명] - [저자]
        ...

        ## 💡 추가 조언
        [사용자의 상황에 맞는 독서 조언이나 팁]
        """)
        
        self.recommendation_chain = LLMChain(
            llm=self.llm, 
            prompt=self.recommendation_prompt
        )

    def emotion_search(self, query, k=10):
        """감정 기반 검색"""
        print(f"🔍 감정 기반 검색: '{query}'")
        
        # 벡터 유사도 검색
        results = self.vectorstore.similarity_search(query, k=k)
        
        # 결과 필터링 및 정리
        filtered_results = []
        seen_isbns = set()
        
        for doc in results:
            isbn = doc.metadata.get('isbn')
            if isbn and isbn not in seen_isbns:
                seen_isbns.add(isbn)
                filtered_results.append(doc)
        
        return filtered_results[:5]  # 최대 5개 도서

    def keyword_search(self, query, k=10):
        """키워드 기반 검색"""
        print(f"🔍 키워드 기반 검색: '{query}'")
        
        # 메타데이터 필터링과 함께 검색
        results = self.vectorstore.similarity_search(query, k=k)
        
        # 제품 키워드 매칭도 고려
        scored_results = []
        for doc in results:
            score = 0
            content = doc.page_content.lower()
            query_lower = query.lower()
            
            # 내용 매칭 점수
            if query_lower in content:
                score += 2
            
            # 제품 키워드 매칭 점수
            product_keywords = doc.metadata.get('product_keywords', [])
            for keyword in product_keywords:
                if keyword.lower() in query_lower or query_lower in keyword.lower():
                    score += 3
            
            scored_results.append((score, doc))
        
        # 점수순 정렬 후 상위 결과 반환
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_results[:5]]

    def hybrid_search(self, query, k=15):
        """하이브리드 검색 (감정 + 키워드)"""
        print(f"🔍 하이브리드 검색: '{query}'")
        
        # 벡터 검색으로 후보 확보
        vector_results = self.vectorstore.similarity_search(query, k=k)
        
        # 중복 제거 및 스코어링 (ISBN + Review ID로 고유 식별)
        doc_scores = {}
        query_lower = query.lower()
        
        for doc in vector_results:
            isbn = doc.metadata.get('isbn')
            review_id = doc.metadata.get('review_id')
            doc_type = doc.metadata.get('type')
            
            if not isbn:
                continue
            
            # 문서 고유 키 생성 (ISBN + Review ID)
            doc_key = f"{isbn}_{review_id if review_id else 'no_review'}"
            
            if doc_key not in doc_scores:
                doc_scores[doc_key] = {'doc': doc, 'score': 0}
            
            # 기본 유사도 점수
            doc_scores[doc_key]['score'] += 1
            
            # 상품 감정 키워드 매칭
            product_emotion_keywords = doc.metadata.get('product_emotion_keywords', [])
            for emotion in product_emotion_keywords:
                if emotion in query_lower:
                    doc_scores[doc_key]['score'] += 2
            
            # 리뷰 감정 키워드 매칭 (더 높은 가중치)
            review_emotion_keywords = doc.metadata.get('review_emotion_keywords', [])
            for emotion in review_emotion_keywords:
                if emotion in query_lower:
                    doc_scores[doc_key]['score'] += 4
            
            # 제품 키워드 매칭  
            product_keywords = doc.metadata.get('product_keywords', [])
            for keyword in product_keywords:
                if keyword.lower() in query_lower or query_lower in keyword.lower():
                    doc_scores[doc_key]['score'] += 3
            
            # 제목/내용 직접 매칭
            content = doc.page_content.lower()
            product_name = doc.metadata.get('product_name', '').lower()
            if query_lower in content or query_lower in product_name:
                doc_scores[doc_key]['score'] += 4
        
        # 점수순 정렬하여 상위 5개 반환
        sorted_docs = sorted(doc_scores.values(), key=lambda x: x['score'], reverse=True)
        return [item['doc'] for item in sorted_docs[:5]]

    def search_and_recommend(self, user_query):
        """검색 및 추천 통합 함수"""
        print(f"\n🤖 AI 도서 추천 시작: '{user_query}'")
        
        # 하이브리드 검색 수행
        search_results = self.hybrid_search(user_query)
        
        if not search_results:
            return "죄송합니다. 검색 결과를 찾을 수 없습니다. 다른 키워드로 검색해보세요."
        
        # 검색 결과를 텍스트로 포맷팅
        formatted_results = ""
        for i, doc in enumerate(search_results, 1):
            metadata = doc.metadata
            doc_type = metadata.get('type', 'unknown')
            
            formatted_results += f"\n{i}. 도서명: {metadata.get('product_name', 'N/A')}\n"
            formatted_results += f"   저자: {metadata.get('author', 'N/A')}\n"
            formatted_results += f"   출판사: {metadata.get('publisher', 'N/A')}\n"
            formatted_results += f"   가격: {metadata.get('price', 0)}원\n"
            formatted_results += f"   카테고리: {metadata.get('category', 'N/A')}\n"
            formatted_results += f"   ISBN: {metadata.get('isbn', 'N/A')}\n"
            formatted_results += f"   타입: {doc_type}\n"
            
            # 상품 감정 키워드 (JSON 파싱)
            if metadata.get('product_emotion_keywords'):
                try:
                    emotion_kw = json.loads(metadata['product_emotion_keywords'])
                    formatted_results += f"   상품 감정: {', '.join(emotion_kw)}\n"
                except:
                    formatted_results += f"   상품 감정: {metadata['product_emotion_keywords']}\n"
            
            # 제품 키워드 (JSON 파싱)
            if metadata.get('product_keywords'):
                try:
                    product_kw = json.loads(metadata['product_keywords'])
                    formatted_results += f"   제품 키워드: {', '.join(product_kw)}\n"
                except:
                    formatted_results += f"   제품 키워드: {metadata['product_keywords']}\n"
            
            # 리뷰 감정 키워드 (JSON 파싱)
            if doc_type == "product_with_review" and metadata.get('review_emotion_keywords'):
                try:
                    review_kw = json.loads(metadata['review_emotion_keywords'])
                    formatted_results += f"   리뷰 감정: {', '.join(review_kw)}\n"
                except:
                    formatted_results += f"   리뷰 감정: {metadata['review_emotion_keywords']}\n"
                if metadata.get('review_title'):
                    formatted_results += f"   리뷰 제목: {metadata['review_title']}\n"
            
            formatted_results += f"   내용: {doc.page_content[:200]}...\n"
        
        # LLM을 사용한 개인화 추천 생성
        try:
            recommendation = self.recommendation_chain.run({
                "query": user_query,
                "search_results": formatted_results
            })
            return recommendation
        except Exception as e:
            print(f"추천 생성 오류: {e}")
            # 폴백: 검색 결과만 반환
            return f"검색 결과:\n{formatted_results}"

    def get_book_by_emotion(self, emotion, k=5):
        """특정 감정으로 도서 검색"""
        return self.emotion_search(f"감정: {emotion}", k)

    def get_book_by_keyword(self, keyword, k=5):
        """특정 키워드로 도서 검색"""
        return self.keyword_search(keyword, k)

def main():
    """메인 실행 함수"""
    engine = BookRecommendationEngine()
    
    print("🚀 AI 도서 추천 엔진이 시작되었습니다!")
    print("예시 검색:")
    print("- '스트레스를 받아서 힐링이 필요해'")
    print("- '프로그래밍을 배우고 싶어'")
    print("- '자기계발 도서 추천해줘'")
    print("- '우울할 때 읽을 책'")
    print("\n종료하려면 'quit' 입력\n")
    
    while True:
        user_input = input("검색어를 입력하세요: ").strip()
        
        if user_input.lower() in ['quit', 'exit', '종료']:
            print("추천 엔진을 종료합니다.")
            break
        
        if not user_input:
            continue
        
        try:
            recommendation = engine.search_and_recommend(user_input)
            print("\n" + "="*50)
            print(recommendation)
            print("="*50 + "\n")
        except Exception as e:
            print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()