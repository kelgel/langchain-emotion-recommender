#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카카오 도서검색 API를 사용해서 프로덕트 테이블의 detail_description 업데이트
"""

import requests
import json
import time
try:
    import pymysql
    USE_PYMYSQL = True
except ImportError:
    import mysql.connector
    USE_PYMYSQL = False
from datetime import datetime
import logging

class KakaoBookDescriptionUpdater:
    def __init__(self):
        # 카카오 API 설정
        self.kakao_api_key = "0ab664098b66f4749d003a1e1edaaa3e"  # 실제 API 키로 변경 필요
        self.kakao_base_url = "https://dapi.kakao.com/v3/search/book"
        
        # MySQL 연결 설정 (WSL에서 Windows MySQL 연결)
        self.db_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'seonghoon',
            'password': '6529',
            'database': 'bookstore',
            'charset': 'utf8mb4'
        }
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('kakao_update.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 통계
        self.stats = {
            'total_products': 0,
            'updated_products': 0,
            'api_calls': 0,
            'errors': 0
        }

    def get_db_connection(self):
        """데이터베이스 연결"""
        try:
            if USE_PYMYSQL:
                connection = pymysql.connect(**self.db_config)
            else:
                connection = mysql.connector.connect(**self.db_config)
            return connection
        except Exception as e:
            self.logger.error(f"데이터베이스 연결 오류: {e}")
            return None

    def get_products_without_description(self):
        """detail_description이 없는 프로덕트 조회"""
        connection = self.get_db_connection()
        if not connection:
            return []
        
        try:
            if USE_PYMYSQL:
                cursor = connection.cursor(pymysql.cursors.DictCursor)
            else:
                cursor = connection.cursor(dictionary=True)
            query = """
            SELECT isbn, product_name as title, author
            FROM product 
            WHERE detail_description IS NULL OR detail_description = ''
            ORDER BY isbn
            """
            cursor.execute(query)
            products = cursor.fetchall()
            self.stats['total_products'] = len(products)
            self.logger.info(f"업데이트 대상 프로덕트: {len(products)}개")
            return products
        except Exception as e:
            self.logger.error(f"프로덕트 조회 오류: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

    def search_book_on_kakao(self, title, author=None, isbn=None):
        """카카오 API로 도서 정보 검색"""
        headers = {
            'Authorization': f'KakaoAK {self.kakao_api_key}'
        }
        
        # 검색 쿼리 구성 (ISBN 우선, 그 다음 제목+저자)
        if isbn and isbn.strip():
            query = isbn.strip()
        else:
            query = title
            if author and author.strip():
                query += f" {author.strip()}"
        
        params = {
            'query': query,
            'size': 1  # 첫 번째 결과만 사용
        }
        
        try:
            self.stats['api_calls'] += 1
            response = requests.get(self.kakao_base_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data['documents']:
                    book = data['documents'][0]
                    # 상세 설명이 있으면 반환
                    if 'contents' in book and book['contents'].strip():
                        return book['contents']
                    
            elif response.status_code == 429:
                # API 한도 초과시 대기
                self.logger.warning("API 한도 초과, 1초 대기")
                time.sleep(1)
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"카카오 API 호출 오류: {e}")
            self.stats['errors'] += 1
        
        return None

    def update_product_description(self, isbn, description):
        """프로덕트의 detail_description 업데이트"""
        connection = self.get_db_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            query = """
            UPDATE product 
            SET detail_description = %s 
            WHERE isbn = %s
            """
            cursor.execute(query, (description, isbn))
            connection.commit()
            
            if cursor.rowcount > 0:
                self.stats['updated_products'] += 1
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"프로덕트 업데이트 오류: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

    def process_all_products(self):
        """모든 프로덕트 처리"""
        products = self.get_products_without_description()
        if not products:
            self.logger.info("업데이트할 프로덕트가 없습니다.")
            return
        
        self.logger.info(f"총 {len(products)}개 프로덕트 처리 시작")
        
        for i, product in enumerate(products, 1):
            try:
                self.logger.info(f"처리 중: {i}/{len(products)} - ISBN: {product['isbn']}, 제목: {product['title']}")
                
                # 카카오 API로 설명 검색
                description = self.search_book_on_kakao(
                    title=product['title'],
                    author=product.get('author'),
                    isbn=product.get('isbn')
                )
                
                if description:
                    # 데이터베이스 업데이트
                    if self.update_product_description(product['isbn'], description):
                        self.logger.info(f"업데이트 완료: ISBN {product['isbn']}")
                    else:
                        self.logger.error(f"업데이트 실패: ISBN {product['isbn']}")
                else:
                    self.logger.warning(f"설명을 찾을 수 없음: ISBN {product['isbn']}")
                
                # API 호출 간격 (카카오 API 제한 고려)
                time.sleep(0.1)
                
                # 진행률 출력
                if i % 10 == 0:
                    self.print_progress()
                    
            except Exception as e:
                self.logger.error(f"프로덕트 {product['isbn']} 처리 중 오류: {e}")
                self.stats['errors'] += 1
        
        self.print_final_stats()

    def print_progress(self):
        """진행률 출력"""
        self.logger.info(f"진행률 - 업데이트: {self.stats['updated_products']}/{self.stats['total_products']}, "
                        f"API 호출: {self.stats['api_calls']}, 오류: {self.stats['errors']}")

    def print_final_stats(self):
        """최종 통계 출력"""
        self.logger.info("=" * 50)
        self.logger.info("업데이트 완료")
        self.logger.info(f"총 프로덕트: {self.stats['total_products']}")
        self.logger.info(f"업데이트된 프로덕트: {self.stats['updated_products']}")
        self.logger.info(f"총 API 호출: {self.stats['api_calls']}")
        self.logger.info(f"오류 발생: {self.stats['errors']}")
        self.logger.info("=" * 50)

def main():
    """메인 함수"""
    updater = KakaoBookDescriptionUpdater()
    
    # API 키 확인
    if updater.kakao_api_key == "YOUR_KAKAO_API_KEY":
        print("❌ 카카오 API 키를 설정해주세요!")
        print("1. https://developers.kakao.com에서 앱 생성")
        print("2. REST API 키를 복사")
        print("3. 스크립트의 kakao_api_key 변수에 입력")
        return
    
    try:
        updater.process_all_products()
    except KeyboardInterrupt:
        print("\n작업이 중단되었습니다.")
        updater.print_final_stats()

if __name__ == "__main__":
    main()