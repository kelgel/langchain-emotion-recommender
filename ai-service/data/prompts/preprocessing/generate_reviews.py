import pymysql
import random
from review_templates import CATEGORY_TEMPLATES

# MySQL 연결 설정
def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='seonghoon',
        password='6529',
        database='bookstore',
        charset='utf8mb4',
        autocommit=True
    )

def get_review_data():
    """리뷰가 필요한 데이터 조회 (product_review_id, isbn, rate, top_category_name)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # product 테이블의 rate 컬럼 사용 - 각 리뷰 row별로 개별 처리
    query = """
    SELECT 
        pr.product_review_id,
        pr.isbn,
        p.rate,
        tc.top_category_name
    FROM product_review pr
    JOIN product p ON pr.isbn = p.isbn
    JOIN low_category lc ON p.low_category = lc.low_category
    JOIN middle_category mc ON lc.mid_category = mc.mid_category
    JOIN top_category tc ON mc.top_category = tc.top_category
    WHERE (pr.review_title IS NULL OR pr.review_title = '')
       OR (pr.review_content IS NULL OR pr.review_content = '')
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return results

def get_review_ratio(rate):
    """평점에 따른 긍부정 비율 반환"""
    if rate <= 7.0:
        return 0.5  # 긍정 50%
    elif 7.1 <= rate <= 8.5:
        return 0.7  # 긍정 70%
    else:  # 8.6 이상
        return 0.85  # 긍정 85%

def select_random_review(category_name, is_positive):
    """카테고리와 긍부정에 따라 랜덤 리뷰 선택"""
    if category_name not in CATEGORY_TEMPLATES:
        # 카테고리가 없으면 기본값으로 '소설/시/희곡' 사용
        category_name = '소설/시/희곡'
    
    review_type = 'positive' if is_positive else 'negative'
    reviews = CATEGORY_TEMPLATES[category_name][review_type]
    
    return random.choice(reviews)

def update_review(product_review_id, title, content):
    """리뷰 제목과 내용 업데이트 - 개별 리뷰 ID로 업데이트"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    UPDATE product_review 
    SET review_title = %s, review_content = %s 
    WHERE product_review_id = %s
    """
    
    cursor.execute(query, (title, content, product_review_id))
    conn.commit()
    
    cursor.close()
    conn.close()

def generate_reviews():
    """메인 함수: 리뷰 데이터 생성"""
    print("리뷰 데이터 조회 중...")
    review_data = get_review_data()
    
    if not review_data:
        print("업데이트할 리뷰가 없습니다.")
        return
    
    print(f"총 {len(review_data)}개의 리뷰를 생성합니다.")
    
    updated_count = 0
    
    for product_review_id, isbn, rate, top_category_name in review_data:
        try:
            # 평점에 따른 긍정 비율 계산
            positive_ratio = get_review_ratio(rate)
            
            # 랜덤하게 긍정/부정 결정
            is_positive = random.random() < positive_ratio
            
            # 랜덤 리뷰 선택
            review = select_random_review(top_category_name, is_positive)
            
            # 리뷰 업데이트
            update_review(product_review_id, review['title'], review['content'])
            
            updated_count += 1
            
            if updated_count % 1000 == 0:
                print(f"{updated_count}개 리뷰 업데이트 완료...")
                
        except Exception as e:
            print(f"product_review_id {product_review_id} 처리 중 오류: {e}")
            continue
    
    print(f"리뷰 생성 완료! 총 {updated_count}개 업데이트됨")

def main():
    """실행 함수"""
    try:
        print("=== 리뷰 자동 생성 시작 ===")
        generate_reviews()
        print("=== 리뷰 자동 생성 완료 ===")
        
    except Exception as e:
        print(f"프로그램 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()