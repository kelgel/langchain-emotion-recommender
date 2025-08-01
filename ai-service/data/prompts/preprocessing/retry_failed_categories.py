#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실패한 카테고리 재처리 스크립트
"""

import mysql.connector
from aladin_bulk_collector import AladinBulkCollector
import time

def get_categories_without_products():
    """상품이 없는 카테고리 조회"""
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'seonghoon',
        'password': '6529',
        'database': 'bookstore',
        'charset': 'utf8mb4'
    }
    
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    # 상품이 없는 카테고리 조회
    query = """
    SELECT lc.low_category, lc.low_category_name, lc.aladin_cid
    FROM low_category lc
    LEFT JOIN product p ON lc.low_category = p.low_category
    WHERE lc.aladin_cid IS NOT NULL 
    AND lc.aladin_cid != 0
    AND p.isbn IS NULL
    ORDER BY lc.low_category
    """
    
    cursor.execute(query)
    categories = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return [{'low_category': cat[0], 'name': cat[1], 'cid': cat[2]} for cat in categories]

def main():
    print("🔄 실패한 카테고리 재처리 시작!")
    print("=" * 50)
    
    # 상품이 없는 카테고리 조회
    failed_categories = get_categories_without_products()
    
    if not failed_categories:
        print("✅ 모든 카테고리 처리 완료!")
        return
    
    print(f"📊 재처리 대상: {len(failed_categories)}개 카테고리")
    
    # 수집기 초기화
    collector = AladinBulkCollector()
    
    # 통계 초기화
    collector.stats = {
        'total_categories': len(failed_categories),
        'processed_categories': 0,
        'total_books': 0,
        'api_calls': 0,
        'errors': 0
    }
    
    start_time = time.time()
    
    # 재처리 (단일 스레드로 안전하게)
    for i, category in enumerate(failed_categories):
        print(f"\n[{i+1}/{len(failed_categories)}] 재처리 중: {category['name']} (CID: {category['cid']})")
        
        try:
            collector.process_category(category)
            time.sleep(1)  # 안전한 간격
        except Exception as e:
            print(f"  ❌ 재처리 실패: {e}")
            collector.stats['errors'] += 1
    
    end_time = time.time()
    
    # 최종 통계
    print("\n" + "=" * 50)
    print("📈 재처리 완료!")
    print(f"⏱️  소요 시간: {int(end_time - start_time)}초")
    print(f"📂 처리 카테고리: {collector.stats['processed_categories']}/{collector.stats['total_categories']}")
    print(f"📚 추가 수집 도서: {collector.stats['total_books']}권")
    print(f"🔗 API 호출: {collector.stats['api_calls']}회")
    print(f"❌ 오류: {collector.stats['errors']}회")
    
    # 전체 통계 확인
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'seonghoon',
        'password': '6529',
        'database': 'bookstore',
        'charset': 'utf8mb4'
    }
    
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM product')
    total_books = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT low_category) FROM product')
    categories_with_books = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    print(f"\n🎉 전체 결과:")
    print(f"📚 총 도서 수: {total_books}권")
    print(f"📂 도서가 있는 카테고리: {categories_with_books}개")

if __name__ == "__main__":
    main()