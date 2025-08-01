#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
알라딘 API 대량 데이터 수집 스크립트
5개 API 키를 활용해서 768개 카테고리별로 32권씩 수집
"""

import requests
import json
import time
import random
import mysql.connector
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

class AladinBulkCollector:
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
        self.key_lock = threading.Lock()
        
        # MySQL 연결 설정 (Windows MySQL 사용)
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
            'errors': 0
        }
        self.stats_lock = threading.Lock()
    
    def get_next_api_key(self):
        """다음 API 키 가져오기 (순환)"""
        with self.key_lock:
            key = self.api_keys[self.current_key_index]
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            return key
    
    def get_db_connection(self):
        """데이터베이스 연결"""
        return mysql.connector.connect(**self.db_config)
    
    def get_categories_with_cid(self):
        """CID가 있는 카테고리 목록 조회"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT low_category, low_category_name, aladin_cid 
        FROM low_category 
        WHERE aladin_cid IS NOT NULL AND aladin_cid != 0
        ORDER BY low_category
        """
        
        cursor.execute(query)
        categories = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [{'low_category': cat[0], 'name': cat[1], 'cid': cat[2]} for cat in categories]
    
    def get_books_by_category(self, cid, max_results=32):
        """카테고리별 도서 목록 조회"""
        api_key = self.get_next_api_key()
        books = []
        page = 1
        
        while len(books) < max_results:
            url = f"{self.base_url}/ItemList.aspx"
            # 다양한 QueryType 시도
            query_types = ['Bestseller', 'ItemNewAll', 'ItemNewSpecial'] if page == 1 else ['Bestseller']
            
            for query_type in query_types:
                if len(books) >= max_results:
                    break
                    
                params = {
                    'ttbkey': api_key,
                    'QueryType': query_type,
                    'CategoryId': cid,
                    'MaxResults': min(50, max_results - len(books)),
                    'start': page,
                    'SearchTarget': 'Book',
                    'output': 'js',
                    'Version': '20131101'
                }
            
            try:
                response = requests.get(url, params=params, timeout=30)  # 타임아웃 증가
                response.raise_for_status()
                
                with self.stats_lock:
                    self.stats['api_calls'] += 1
                
                data = response.json()
                
                if not data or 'item' not in data or not data['item']:
                    break
                
                for item in data['item']:
                    if len(books) >= max_results:
                        break
                    books.append(item)
                
                page += 1
                time.sleep(0.5)  # API 호출 간격 증가
                
            except Exception as e:
                print(f"API 호출 오류 (CID: {cid}, Page: {page}): {e}")
                print(f"  재시도 중...")
                time.sleep(2)  # 오류 시 대기
                with self.stats_lock:
                    self.stats['errors'] += 1
                # 재시도 대신 다음 페이지로 넘어가기
                if page > 1:
                    break
                else:
                    continue
        
        return books
    
    def convert_to_product_format(self, book_data, low_category_id):
        """알라딘 데이터를 product 테이블 형식으로 변환"""
        try:
            # ISBN 추출
            isbn = book_data.get('isbn13', book_data.get('isbn', ''))
            if not isbn:
                return None
            
            # 가격 처리
            price = book_data.get('priceStandard', 0)
            if isinstance(price, str):
                price = int(price.replace(',', '')) if price.replace(',', '').isdigit() else 0
            
            # 평점 처리 (알라딘 0-10점을 0-10.0점으로)
            customer_review = book_data.get('customerReviewRank', 0)
            rate = round(float(customer_review), 1) if customer_review else 5.0
            
            # 이미지 URL
            img_url = book_data.get('cover', '')
            if img_url:
                img_url = img_url.replace('_sum', '_big')
            
            # 설명 처리
            description = book_data.get('description', '')
            if not description:
                description = f"{book_data.get('title', '')} - {book_data.get('author', '')} 저"
            
            brief_desc = description[:300] + "..." if len(description) > 300 else description
            
            # 판매 상태
            stock_status = book_data.get('stockStatus', '')
            if 'out of print' in stock_status.lower():
                sales_status = 'OUT_OF_PRINT'
            elif 'temporarily' in stock_status.lower():
                sales_status = 'TEMPORARILY_OUT_OF_STOCK'
            else:
                sales_status = 'ON_SALE'
            
            # 책 크기 (랜덤값으로 대체)
            width = random.randint(148, 188)
            height = random.randint(210, 257)
            page = random.randint(200, 500)
            
            # 페이지 수 추출 시도
            if 'subInfo' in book_data and isinstance(book_data['subInfo'], dict):
                page_info = book_data['subInfo'].get('page', '')
                if page_info:
                    try:
                        page = int(''.join(filter(str.isdigit, str(page_info))))
                    except:
                        pass
            
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
                'width': width,
                'height': height,
                'page': page,
                'sales_status': sales_status,
                'search_count': random.randint(1, 100)
            }
            
        except Exception as e:
            print(f"데이터 변환 오류: {e}")
            return None
    
    def save_products_to_db(self, products):
        """상품 데이터를 DB에 저장"""
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
                print(f"DB 저장 오류 (ISBN: {product.get('isbn', 'N/A')}): {e}")
                with self.stats_lock:
                    self.stats['errors'] += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return saved_count
    
    def process_category(self, category):
        """카테고리별 데이터 처리"""
        print(f"처리 중: {category['name']} (CID: {category['cid']})")
        
        # 도서 목록 조회
        books = self.get_books_by_category(category['cid'], max_results=32)
        
        if not books:
            print(f"  ❌ 도서 없음: {category['name']}")
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
        with self.stats_lock:
            self.stats['processed_categories'] += 1
            self.stats['total_books'] += saved_count
        
        print(f"  ✅ 완료: {category['name']} - {saved_count}권 저장")
    
    def run(self):
        """메인 실행"""
        print("🚀 알라딘 대량 데이터 수집 시작!")
        print("=" * 60)
        
        # 카테고리 목록 조회
        categories = self.get_categories_with_cid()
        self.stats['total_categories'] = len(categories)
        
        print(f"📊 수집 대상: {len(categories)}개 카테고리")
        print(f"🔑 API 키: {len(self.api_keys)}개")
        print(f"📚 목표: 카테고리별 32권씩 (총 {len(categories) * 32}권)")
        print()
        
        start_time = time.time()
        
        # 멀티스레드로 처리 (API 키 개수만큼)
        with ThreadPoolExecutor(max_workers=len(self.api_keys)) as executor:
            executor.map(self.process_category, categories)
        
        end_time = time.time()
        
        # 최종 통계
        print("\n" + "=" * 60)
        print("📈 수집 완료!")
        print(f"⏱️  소요 시간: {int(end_time - start_time)}초")
        print(f"📂 처리 카테고리: {self.stats['processed_categories']}/{self.stats['total_categories']}")
        print(f"📚 수집 도서: {self.stats['total_books']}권")
        print(f"🔗 API 호출: {self.stats['api_calls']}회")
        print(f"❌ 오류: {self.stats['errors']}회")
        print(f"⚡ 평균 속도: {self.stats['total_books']/(end_time - start_time):.1f}권/초")

def main():
    collector = AladinBulkCollector()
    collector.run()

if __name__ == "__main__":
    main()