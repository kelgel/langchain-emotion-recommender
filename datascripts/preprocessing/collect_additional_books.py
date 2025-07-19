#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 카테고리에서 추가 도서 수집 스크립트
중복 ISBN 제외하고 30권씩 추가 수집
"""

import mysql.connector
import requests
import json
import time
import random
from datetime import datetime

class AdditionalBookCollector:
    def __init__(self):
        # 5개 API 키 설정
        self.api_keys = [
            'ttbbwnfo07021701001',
            'ttbalice76441701001', 
            'ttbcksghdl941659001',
            'ttbsharon3291700001',
            'ttbseonghoon3151604001'
        ]
        
        self.base_url = "http://www.aladin.co.kr/ttb/api"
        self.current_key_index = 0
        
        # MySQL 연결 설정
        self.db_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'seonghoon',
            'password': '6529',
            'database': 'bookstore',
            'charset': 'utf8mb4'
        }
        
        # 통계
        self.stats = {
            'total_categories': 0,
            'processed_categories': 0,
            'total_books': 0,
            'api_calls': 0,
            'errors': 0,
            'duplicates': 0
        }
    
    def get_next_api_key(self):
        """다음 API 키 가져오기"""
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key
    
    def get_db_connection(self):
        """데이터베이스 연결"""
        return mysql.connector.connect(**self.db_config)
    
    def get_categories_with_books(self):
        """이미 도서가 있는 카테고리 조회"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT lc.low_category, lc.low_category_name, lc.aladin_cid, COUNT(p.isbn) as book_count
        FROM low_category lc
        INNER JOIN product p ON lc.low_category = p.low_category
        WHERE lc.aladin_cid IS NOT NULL AND lc.aladin_cid != 0
        GROUP BY lc.low_category, lc.low_category_name, lc.aladin_cid
        ORDER BY book_count DESC
        """
        
        cursor.execute(query)
        categories = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [{'low_category': cat[0], 'name': cat[1], 'cid': cat[2], 'current_books': cat[3]} for cat in categories]
    
    def get_existing_isbns(self, low_category):
        """해당 카테고리의 기존 ISBN 목록 조회"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT isbn FROM product WHERE low_category = %s"
        cursor.execute(query, (low_category,))
        
        existing_isbns = set([row[0] for row in cursor.fetchall()])
        
        cursor.close()
        conn.close()
        
        return existing_isbns
    
    def get_additional_books(self, cid, existing_isbns, target_count=30):
        """추가 도서 수집 (중복 제외)"""
        api_key = self.get_next_api_key()
        books = []
        page = 1
        
        # 다양한 QueryType 시도
        query_types = ['ItemNewAll', 'ItemNewSpecial', 'ItemEditorChoice', 'Bestseller']
        
        for query_type in query_types:
            if len(books) >= target_count:
                break
                
            page = 1
            while len(books) < target_count:
                url = f"{self.base_url}/ItemList.aspx"
                params = {
                    'ttbkey': api_key,
                    'QueryType': query_type,
                    'CategoryId': cid,
                    'MaxResults': 50,
                    'start': page,
                    'SearchTarget': 'Book',
                    'output': 'js',
                    'Version': '20131101'
                }
                
                try:
                    response = requests.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    
                    self.stats['api_calls'] += 1
                    
                    data = response.json()
                    
                    if not data or 'item' not in data or not data['item']:
                        break
                    
                    for item in data['item']:
                        if len(books) >= target_count:
                            break
                        
                        isbn = item.get('isbn13', item.get('isbn', ''))
                        
                        # 중복 ISBN 체크
                        if isbn and isbn not in existing_isbns:
                            books.append(item)
                            existing_isbns.add(isbn)  # 중복 방지용 추가
                        else:
                            self.stats['duplicates'] += 1
                    
                    page += 1
                    time.sleep(0.5)  # API 호출 간격
                    
                except Exception as e:
                    print(f"    API 호출 오류: {e}")
                    self.stats['errors'] += 1
                    break
            
            # QueryType 간 대기
            time.sleep(1)
        
        return books
    
    def convert_to_product_format(self, book_data, low_category_id):
        """데이터 변환"""
        try:
            isbn = book_data.get('isbn13', book_data.get('isbn', ''))
            if not isbn:
                return None
            
            price = book_data.get('priceStandard', 0)
            if isinstance(price, str):
                price = int(price.replace(',', '')) if price.replace(',', '').isdigit() else 0
            
            customer_review = book_data.get('customerReviewRank', 0)
            rate = round(float(customer_review), 1) if customer_review else 5.0
            
            img_url = book_data.get('cover', '')
            if img_url:
                img_url = img_url.replace('_sum', '_big')
            
            description = book_data.get('description', '')
            if not description:
                description = f"{book_data.get('title', '')} - {book_data.get('author', '')} 저"
            
            brief_desc = description[:300] + "..." if len(description) > 300 else description
            
            stock_status = book_data.get('stockStatus', '')
            if 'out of print' in stock_status.lower():
                sales_status = 'OUT_OF_PRINT'
            elif 'temporarily' in stock_status.lower():
                sales_status = 'TEMPORARILY_OUT_OF_STOCK'
            else:
                sales_status = 'ON_SALE'
            
            return {
                'isbn': isbn[:255],
                'low_category': low_category_id,
                'product_name': book_data.get('title', '').strip()[:255],
                'author': book_data.get('author', '').strip()[:255],
                'publisher': book_data.get('publisher', '').strip()[:255],
                'price': price,
                'rate': rate,
                'brief_description': brief_desc,
                'detail_description': description,
                'img': img_url[:1000],
                'width': random.randint(148, 188),
                'height': random.randint(210, 257),
                'page': random.randint(200, 500),
                'sales_status': sales_status,
                'search_count': random.randint(1, 100)
            }
            
        except Exception as e:
            print(f"    데이터 변환 오류: {e}")
            return None
    
    def save_products_to_db(self, products):
        """DB 저장"""
        if not products:
            return 0
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO product (
            isbn, low_category, product_name, author, publisher, price, rate,
            brief_description, detail_description, img, width, height, page,
            sales_status, search_count, reg_date
        ) VALUES (
            %(isbn)s, %(low_category)s, %(product_name)s, %(author)s, %(publisher)s,
            %(price)s, %(rate)s, %(brief_description)s, %(detail_description)s,
            %(img)s, %(width)s, %(height)s, %(page)s, %(sales_status)s,
            %(search_count)s, CURDATE()
        )
        ON DUPLICATE KEY UPDATE
            product_name = VALUES(product_name),
            author = VALUES(author),
            publisher = VALUES(publisher),
            price = VALUES(price),
            rate = VALUES(rate),
            brief_description = VALUES(brief_description),
            detail_description = VALUES(detail_description),
            img = VALUES(img),
            width = VALUES(width),
            height = VALUES(height),
            page = VALUES(page),
            sales_status = VALUES(sales_status),
            search_count = VALUES(search_count)
        """
        
        saved_count = 0
        for product in products:
            try:
                cursor.execute(insert_query, product)
                saved_count += 1
            except Exception as e:
                print(f"    DB 저장 오류: {e}")
                self.stats['errors'] += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return saved_count
    
    def process_category(self, category):
        """카테고리별 추가 수집"""
        print(f"[{self.stats['processed_categories']+1}/{self.stats['total_categories']}] 추가 수집: {category['name']} (현재 {category['current_books']}권)")
        
        # 기존 ISBN 목록 조회
        existing_isbns = self.get_existing_isbns(category['low_category'])
        
        # 추가 도서 수집
        books = self.get_additional_books(category['cid'], existing_isbns, 30)
        
        if not books:
            print(f"  ❌ 추가 도서 없음")
            self.stats['processed_categories'] += 1
            return
        
        # 데이터 변환
        products = []
        for book in books:
            product = self.convert_to_product_format(book, category['low_category'])
            if product:
                products.append(product)
        
        # DB 저장
        saved_count = self.save_products_to_db(products)
        
        # 통계 업데이트
        self.stats['processed_categories'] += 1
        self.stats['total_books'] += saved_count
        
        print(f"  ✅ 완료: {saved_count}권 추가 (총 {category['current_books'] + saved_count}권)")
    
    def run(self):
        """메인 실행"""
        print("📚 기존 카테고리 추가 도서 수집 시작!")
        print("=" * 60)
        
        # 도서가 있는 카테고리 조회
        categories = self.get_categories_with_books()
        self.stats['total_categories'] = len(categories)
        
        print(f"📊 대상 카테고리: {len(categories)}개")
        print(f"🎯 목표: 카테고리별 30권 추가")
        print(f"🔑 API 키: {len(self.api_keys)}개")
        print()
        
        start_time = time.time()
        
        # 순차 처리 (안정성 우선)
        for category in categories:
            try:
                self.process_category(category)
                time.sleep(2)  # 카테고리 간 대기
            except Exception as e:
                print(f"  ❌ 카테고리 처리 오류: {e}")
                self.stats['errors'] += 1
                self.stats['processed_categories'] += 1
        
        end_time = time.time()
        
        # 최종 통계
        print("\n" + "=" * 60)
        print("📈 추가 수집 완료!")
        print(f"⏱️  소요 시간: {int(end_time - start_time)}초")
        print(f"📂 처리 카테고리: {self.stats['processed_categories']}/{self.stats['total_categories']}")
        print(f"📚 추가 수집 도서: {self.stats['total_books']}권")
        print(f"🔗 API 호출: {self.stats['api_calls']}회")
        print(f"❌ 오류: {self.stats['errors']}회")
        print(f"🔄 중복 제외: {self.stats['duplicates']}권")
        
        # 전체 통계 확인
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM product')
        total_books = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 전체 결과:")
        print(f"📚 총 도서 수: {total_books}권")

def main():
    collector = AdditionalBookCollector()
    collector.run()

if __name__ == "__main__":
    main()