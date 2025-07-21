# vector_embedding_enhanced.py - 샘플 데이터 기반 향상된 벡터 임베딩
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
import mysql.connector
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# OpenAI API 키 환경변수에서 가져오기
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("OPENAI_API_KEY 환경변수를 설정해주세요.")

def load_db_config_from_properties():
    """application.properties에서 DB 설정 읽기"""
    # 현재 파일에서 프로젝트 루트 찾기
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)  # 1단계 위로
    properties_path = os.path.join(project_root, 'src', 'main', 'resources', 'application.properties')
    
    print(f"프로젝트 루트: {project_root}")
    print(f"Properties 파일 경로: {properties_path}")
    print(f"Properties 파일 존재: {os.path.exists(properties_path)}")
    
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '',
        'database': 'bookstore',
        'charset': 'utf8mb4',
        'autocommit': False,
        'use_unicode': True
    }
    
    try:
        with open(properties_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('spring.datasource.url='):
                    # jdbc:mysql://host:port/database?params 파싱
                    url = line.split('=', 1)[1]
                    if '://' in url and '/' in url:
                        # host:port 추출
                        host_part = url.split('://')[1].split('/')[0]
                        if ':' in host_part:
                            db_config['host'] = host_part.split(':')[0]
                            db_config['port'] = int(host_part.split(':')[1])
                        else:
                            db_config['host'] = host_part
                            db_config['port'] = 3306
                        
                        # database 추출
                        if '/' in url:
                            # jdbc:mysql://host:port/database?params
                            url_parts = url.split('/')
                            if len(url_parts) >= 4:
                                db_part = url_parts[3]  # database 부분
                                if '?' in db_part:
                                    db_name = db_part.split('?')[0]
                                else:
                                    db_name = db_part
                                db_config['database'] = db_name
                            
                elif line.startswith('spring.datasource.username='):
                    db_config['user'] = line.split('=', 1)[1]
                elif line.startswith('spring.datasource.password='):
                    db_config['password'] = line.split('=', 1)[1]
        
        print(f"DB 설정 로드 완료: {db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
        return db_config
        
    except Exception as e:
        print(f"application.properties 읽기 실패: {e}")
        print(f"Properties 파일 경로: {properties_path}")
        print(f"Properties 파일 존재: {os.path.exists(properties_path)}")
        print("기본 설정 사용 - AWS RDS 설정")
        # AWS RDS 기본값으로 설정
        db_config.update({
            'host': 'tp4team5.cny6cmeagio6.ap-northeast-2.rds.amazonaws.com',
            'user': 'admin',
            'password': 'corzmdls1!'
        })
        return db_config

# 데이터베이스 연결 설정 (application.properties에서 자동 로드)
DB_CONFIG = load_db_config_from_properties()

# OpenAI 임베딩 모델 초기화
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

# Chroma 벡터스토어 설정
PERSIST_DIRECTORY = "./chroma_db"
vectorstore = Chroma(
    collection_name="bookstore_collection",
    embedding_function=embeddings,
    persist_directory=PERSIST_DIRECTORY
)

def create_enhanced_product_review_documents():
    """향상된 Product + Review 통합 문서 생성 (샘플 데이터 기반)"""
    print("=== 향상된 Product + Review 통합 문서 생성 중 ===")

    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    try:
        # 1. 리뷰가 있는 상품들: Product + Review 조합 문서 (실제 테스트된 쿼리)
        cursor.execute("""
            SELECT p.isbn, tc.top_category_name, mc.mid_category_name, lc.low_category_name,
                   p.product_name, p.author, p.publisher, p.price, p.rate,
                   p.brief_description, p.detail_description,
                   p.emotion_keyword as product_emotion, p.product_keyword,
                   pr.review_title, pr.review_content, pr.emotion_keyword as review_emotion,
                   p.page, p.sales_status, p.reg_date
            FROM product p
                     JOIN product_review pr ON p.isbn = pr.isbn
                     LEFT JOIN low_category lc ON p.low_category = lc.low_category
                     LEFT JOIN middle_category mc ON lc.mid_category = mc.mid_category
                     LEFT JOIN top_category tc ON mc.top_category = tc.top_category
            WHERE p.emotion_keyword IS NOT NULL AND p.product_keyword IS NOT NULL
              AND pr.emotion_keyword IS NOT NULL
        """)

        product_review_pairs = cursor.fetchall()
        documents = []

        print(f"Product + Review 조합 문서 생성: {len(product_review_pairs)}개")

        for row in product_review_pairs:
            (isbn, top_category_name, mid_category_name, low_category_name,
             name, author, publisher, price, rate,
             brief, detail,
             product_emotion_kw, product_kw,
             review_title, review_content, review_emotion_kw,
             page, sales_status, reg_date) = row

            # 상품 키워드 파싱
            product_emotion_keywords = json.loads(product_emotion_kw) if product_emotion_kw else []
            product_keywords = json.loads(product_kw) if product_kw else []
            review_emotion_keywords = json.loads(review_emotion_kw) if review_emotion_kw else []

            # 완전 동기화: page_content와 metadata 일치
            content = f"""
                상위 카테고리: {top_category_name or ''}
                중간 카테고리: {mid_category_name or ''}
                하위 카테고리: {low_category_name or ''}
                제품명: {name}
                저자: {author or ''}
                출판사: {publisher or ''}
                가격: {price or 0}원
                평점: {rate or 0}점
                간단 설명: {brief or ''}
                상세 설명: {detail or ''}
                상품 감정: {', '.join(product_emotion_keywords)}
                상품 키워드: {', '.join(product_keywords)}
                리뷰 제목: {review_title or ''}
                리뷰 내용: {review_content or ''}
                리뷰 감정: {', '.join(review_emotion_keywords)}
                페이지: {page or 0}페이지
                판매상태: {sales_status or ''}
                등록일: {reg_date.strftime('%Y-%m-%d') if reg_date else ''}"""

            # 완전 동기화: metadata가 page_content와 정확히 일치
            metadata = {
                "isbn": isbn,
                "type": "product_with_review",
                "top_category_name": top_category_name or "",
                "mid_category_name": mid_category_name or "",
                "low_category_name": low_category_name or "",
                "product_name": name,
                "author": author or "",
                "publisher": publisher or "",
                "price": int(price) if price else 0,
                "rate": float(rate) if rate else 0.0,
                "brief_description": brief or "",
                "detail_description": detail or "",
                "product_emotion_keywords": product_emotion_kw or "",
                "product_keywords": product_kw or "",
                "review_title": review_title or "",
                "review_content": review_content or "",
                "review_emotion_keywords": review_emotion_kw or "",
                "page": int(page) if page else 0,
                "sales_status": sales_status or "",
                "reg_date": str(reg_date.strftime('%Y-%m-%d')) if reg_date else "",
            }

            doc = Document(page_content=content, metadata=metadata)
            documents.append(doc)

        # 2. 리뷰가 없는 상품들: Product만으로 문서 생성 (카테고리 조인 포함)
        cursor.execute("""
            SELECT p.isbn, tc.top_category_name, mc.mid_category_name, lc.low_category_name,
                   p.product_name, p.author, p.publisher, p.price, p.rate,
                   p.brief_description, p.detail_description,
                   p.emotion_keyword as product_emotion, p.product_keyword,
                   p.page, p.sales_status, p.reg_date
            FROM product p
            LEFT JOIN product_review pr ON p.isbn = pr.isbn
            LEFT JOIN low_category lc ON p.low_category = lc.low_category
            LEFT JOIN middle_category mc ON lc.mid_category = mc.mid_category
            LEFT JOIN top_category tc ON mc.top_category = tc.top_category
            WHERE p.emotion_keyword IS NOT NULL AND p.product_keyword IS NOT NULL
              AND pr.isbn IS NULL
        """)

        products_without_reviews = cursor.fetchall()

        print(f"리뷰 없는 상품 문서 생성: {len(products_without_reviews)}개")

        for row in products_without_reviews:
            (isbn, top_category_name, mid_category_name, low_category_name,
             name, author, publisher, price, rate,
             brief, detail,
             product_emotion_kw, product_kw,
             page, sales_status, reg_date) = row

            # 키워드 파싱
            emotion_keywords = json.loads(product_emotion_kw) if product_emotion_kw else []
            product_keywords = json.loads(product_kw) if product_kw else []

            # 완전 동기화: page_content와 metadata 일치 (리뷰 없는 상품)
            content = f"""
                상위 카테고리: {top_category_name or ''}
                중간 카테고리: {mid_category_name or ''}
                하위 카테고리: {low_category_name or ''}
                제품명: {name}
                저자: {author or ''}
                출판사: {publisher or ''}
                가격: {price or 0}원
                평점: {rate or 0}점
                간단 설명: {brief or ''}
                상세 설명: {detail or ''}
                상품 감정: {', '.join(emotion_keywords)}
                상품 키워드: {', '.join(product_keywords)}
                페이지: {page or 0}페이지
                판매상태: {sales_status or ''}
                등록일: {reg_date.strftime('%Y-%m-%d') if reg_date else ''}"""

            # 완전 동기화: metadata가 page_content와 정확히 일치
            metadata = {
                "isbn": isbn,
                "type": "product_only",
                "top_category_name": top_category_name or "",
                "mid_category_name": mid_category_name or "",
                "low_category_name": low_category_name or "",
                "product_name": name,
                "author": author or "",
                "publisher": publisher or "",
                "price": int(price) if price else 0,
                "rate": float(rate) if rate else 0.0,
                "brief_description": brief or "",
                "detail_description": detail or "",
                "product_emotion_keywords": product_emotion_kw or "",
                "product_keywords": product_kw or "",
                "page": int(page) if page else 0,
                "sales_status": sales_status or "",
                "reg_date": str(reg_date.strftime('%Y-%m-%d')) if reg_date else "",
            }

            doc = Document(page_content=content, metadata=metadata)
            documents.append(doc)

        total_docs = len(product_review_pairs) + len(products_without_reviews)
        print(f"총 향상된 문서 생성 완료: {total_docs}개")
        print(f"  - Product+Review 조합: {len(product_review_pairs)}개")
        print(f"  - Product만: {len(products_without_reviews)}개")

        return documents

    except Exception as e:
        print(f"향상된 문서 생성 오류: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def create_enhanced_vector_database():
    """향상된 벡터 데이터베이스 생성"""
    print("🚀 향상된 벡터 데이터베이스 구성 시작")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 향상된 Product + Review 통합 문서 생성
        all_documents = create_enhanced_product_review_documents()

        if not all_documents:
            print("❌ 임베딩할 문서가 없습니다.")
            return

        # 배치 단위로 벡터스토어에 추가
        batch_size = 100
        total_batches = (len(all_documents) + batch_size - 1) // batch_size

        print(f"\n배치 크기: {batch_size}, 총 배치 수: {total_batches}")

        for i in range(0, len(all_documents), batch_size):
            batch = all_documents[i:i+batch_size]
            batch_num = (i // batch_size) + 1

            print(f"배치 {batch_num}/{total_batches} 처리 중... ({len(batch)}개 문서)")

            # 벡터스토어에 문서 추가
            vectorstore.add_documents(batch)

            print(f"배치 {batch_num} 완료")

        # 벡터스토어는 자동 저장됨 (persist 메서드 불필요)
        print("\n향상된 벡터 데이터베이스 자동 저장 완료")

        print(f"\n✅ 향상된 벡터 데이터베이스 구성 완료!")
        print(f"저장 위치: {PERSIST_DIRECTORY}")
        print(f"총 임베딩된 문서 수: {len(all_documents)}개")

    except Exception as e:
        print(f"❌ 향상된 벡터 데이터베이스 구성 실패: {e}")

    print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    create_enhanced_vector_database()