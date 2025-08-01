# extract_product_keywords_fast.py - 병렬 처리 최적화 버전
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import mysql.connector
import json
import re
from datetime import datetime
from dotenv import load_dotenv
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

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
    project_root = os.path.dirname(os.path.dirname(current_dir))  # 2단계 위로
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

# 프롬프트 템플릿 설정
product_prompt = PromptTemplate.from_template(
    """
너는 도서 추천 시스템의 전문 제품 키워드 추출 AI야.
주어진 텍스트를 정확히 분석해서 사용자가 자연어로 검색할 수 있는 제품/서비스/개념 키워드 5개를 추출해줘.

텍스트:
{text}

**🚨 절대 원칙 🚨**
1. **가장 중요한 제품명**의 내용을 최우선으로 반영하라. 제품명이 가장 중요하다.
2. 상세 설명은 제품명이 모호할 때 보완 정보로 활용하라.
3. 사용자가 실제로 검색할 만한 키워드만 추출하라.
4. 기술명, 프로그래밍 언어, 도구명, 개념명, 주제명을 우선적으로 추출하라.
5. 너무 일반적인 단어(책, 학습, 공부 등)는 피하고 구체적인 키워드를 선택하라.
6. 영어와 한국어 모두 포함 가능하다.
7. **감정 키워드 절대 금지**: 감정, 행복, 슬픔, 기쁨, 우울, 불안, 희망, 사랑, 분노 등 감정 관련 단어는 절대 포함하지 말아라.
8. **중복 정보 절대 금지**: 저자명, 출판사명, 대학명, 교수명은 이미 별도 컬럼에 있으므로 절대 포함하지 말아라.
9. **당연한 정보 금지**: 북, 책, 저, 출판, 도서 등 서점에서 당연한 단어는 절대 포함하지 말아라.

**금지 키워드 목록:**
- **저자/출판사**: 최인철, 서울대학교, 도우출판, 한빛미디어, 길벗, 인피니티북스 등
- **당연한 정보**: 북, 책, 저, 출판, 도서, 서적, 간행물, 교재, 문서 등
- **감정 키워드**: 행복, 슬픔, 기쁨, 우울, 불안, 희망, 사랑, 분노, 감정 등

**중복 제거 필수**: 같은 의미의 키워드는 하나만 선택하라.

텍스트 내용에 따라 적절한 제품/서비스/개념 키워드를 정확히 분석해서 JSON 배열로 출력해라:
["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"]
"""
)

# 전역 변수
processed_count = 0
total_count = 0
start_time = None
lock = threading.Lock()

def create_llm_chain():
    """각 스레드마다 별도의 LLM 체인 생성"""
    llm = ChatOpenAI(temperature=0)
    return LLMChain(llm=llm, prompt=product_prompt)

def extract_product_keywords(text, chain):
    import time
    import random
    import re

    max_retries = 5
    base_delay = 1

    for attempt in range(max_retries):
        try:
            result = chain.run({"text": text})
            product_keywords = json.loads(result.strip())

            # 중복 제거 및 검증
            unique_keywords = []
            for keyword in product_keywords:
                if keyword not in unique_keywords and keyword.strip():
                    unique_keywords.append(keyword.strip())

            # 3~5개 범위로 제한
            if len(unique_keywords) > 5:
                unique_keywords = unique_keywords[:5]
            elif len(unique_keywords) < 3:
                default_keywords = ["도서", "학습", "교육"]
                for default in default_keywords:
                    if default not in unique_keywords:
                        unique_keywords.append(default)
                    if len(unique_keywords) >= 3:
                        break

            return unique_keywords
        except Exception as e:
            error_msg = str(e)
            if "rate limit" in error_msg or "429" in error_msg:
                wait_match = re.search(r"try again in ([\d\.]+)s", error_msg)
                wait_time = float(wait_match.group(1)) if wait_match else 10
                print(f"429 에러: {wait_time}초 대기 후 재시도 (시도 {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"제품 키워드 추출 실패: {e}")
                return []
    print("최대 재시도 횟수 초과, 실패 처리")
    return []

def process_batch(products_batch, thread_id):
    """배치 단위로 제품 키워드 처리"""
    global processed_count, total_count, start_time

    # 각 스레드마다 별도의 LLM 체인 생성
    chain = create_llm_chain()

    # 각 스레드마다 별도의 DB 연결
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    results = []
    error_429 = False

    try:
        for isbn, product_name, brief_desc, detail_desc in products_batch:
            # 텍스트 조합
            combined_text = f"**가장 중요한 제품명**: {product_name}\n\n"
            if detail_desc:
                combined_text += f"**상세 설명**: {detail_desc}\n\n"
            if brief_desc:
                combined_text += f"간단 설명: {brief_desc}"

            # 키워드 추출 (요청 간격 추가)
            time.sleep(1.0)  # 1초 대기
            keywords = extract_product_keywords(combined_text, chain)

            if keywords:
                keyword_json = json.dumps(keywords, ensure_ascii=False)
                results.append((keyword_json, isbn, keywords))

            # 진행률 업데이트
            with lock:
                processed_count += 1
                if processed_count % 10 == 0:  # 10개마다 진행률 출력
                    elapsed_time = time.time() - start_time
                    progress = (processed_count / total_count) * 100
                    estimated_total = elapsed_time / (processed_count / total_count)
                    remaining_time = estimated_total - elapsed_time
                    print(f"[스레드 {thread_id}] 진행률: {processed_count}/{total_count} ({progress:.1f}%) "
                          f"경과: {elapsed_time:.0f}초, 예상 남은 시간: {remaining_time:.0f}초")

        # 배치 단위로 DB 업데이트
        if results:
            for keyword_json, isbn, keywords in results:
                cursor.execute("""
                    UPDATE product
                    SET product_keyword = %s
                    WHERE isbn = %s
                """, (keyword_json, isbn))

            connection.commit()
            print(f"[스레드 {thread_id}] 배치 커밋 완료: {len(results)}개")

    except Exception as e:
        connection.rollback()
        if "429" in str(e):
            error_429 = True
        print(f"[스레드 {thread_id}] 오류 발생: {e}")
    finally:
        cursor.close()
        connection.close()

    return len(results), error_429


def process_product_keywords_serial():
    """직렬 처리로 제품 키워드 추출"""
    global processed_count, total_count, start_time

    print("=== Product 테이블 제품 키워드 추출 시작 (직렬 처리) ===")

    # 데이터 조회
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT isbn, product_name, brief_description, detail_description
            FROM product
            WHERE product_keyword IS NULL OR product_keyword = ''
        """)

        products = cursor.fetchall()
        total_count = len(products)
        print(f"처리할 상품 수: {total_count}")

        if total_count == 0:
            print("처리할 상품이 없습니다.")
            return

        # 직렬 처리 설정
        print(f"직렬 처리 시작 - 총 {total_count}개 상품")

        # 시작 시간 기록
        start_time = time.time()
        processed_count = 0
        
        # LLM 체인 생성
        chain = create_llm_chain()
        
        # 직렬 처리 실행
        total_processed = 0
        for idx, (isbn, product_name, brief_desc, detail_desc) in enumerate(products):
            try:
                # 텍스트 조합
                combined_text = f"**가장 중요한 제품명**: {product_name}\n\n"
                if detail_desc:
                    combined_text += f"**상세 설명**: {detail_desc}\n\n"
                if brief_desc:
                    combined_text += f"간단 설명: {brief_desc}"

                # 키워드 추출 (요청 간격 추가)
                time.sleep(1.5)  # 1.5초 대기
                keywords = extract_product_keywords(combined_text, chain)

                if keywords:
                    keyword_json = json.dumps(keywords, ensure_ascii=False)
                    
                    # DB 업데이트
                    cursor.execute("""
                        UPDATE product
                        SET product_keyword = %s
                        WHERE isbn = %s
                    """, (keyword_json, isbn))
                    connection.commit()
                    total_processed += 1

                # 진행률 출력
                processed_count += 1
                if processed_count % 50 == 0:  # 50개마다 진행률 출력
                    elapsed_time = time.time() - start_time
                    progress = (processed_count / total_count) * 100
                    estimated_total = elapsed_time / (processed_count / total_count)
                    remaining_time = estimated_total - elapsed_time
                    avg_speed = processed_count / elapsed_time
                    print(f"진행률: {processed_count}/{total_count} ({progress:.1f}%) "
                          f"경과: {elapsed_time:.0f}초, 예상 남은 시간: {remaining_time:.0f}초, 속도: {avg_speed:.2f}개/초")
                    
            except Exception as e:
                print(f"상품 {isbn} 처리 실패: {e}")
                continue

        elapsed_time = time.time() - start_time
        print(f"\n=== Product 테이블 처리 완료 ===")
        print(f"총 처리 시간: {elapsed_time:.1f}초")
        print(f"처리된 상품 수: {total_processed}/{total_count}")
        print(f"평균 처리 속도: {total_processed/elapsed_time:.1f}개/초")

    except Exception as e:
        print(f"데이터 조회 오류: {e}")
    finally:
        cursor.close()
        connection.close()

def main():
    """메인 실행 함수"""
    print("🚀 제품 키워드 추출 시작 (고속 병렬 처리)")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        process_product_keywords_serial()
        print("\n✅ 모든 처리가 완료되었습니다!")
        
    except Exception as e:
        print(f"❌ 처리 중 오류 발생: {e}")
    
    print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()