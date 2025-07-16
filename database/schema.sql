-- YESorNO.24 온라인 서점 데이터베이스 스키마
-- MySQL 8.0 기준으로 작성됨

-- 데이터베이스 생성 (필요시)
CREATE DATABASE IF NOT EXISTS bookstore CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bookstore;

-- 기존 테이블 삭제 (순서 중요: 외래키 의존성 고려)
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS product_review;
DROP TABLE IF EXISTS order_detail;
DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS `order`;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS product_history;
DROP TABLE IF EXISTS stock;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS low_category;
DROP TABLE IF EXISTS middle_category;
DROP TABLE IF EXISTS top_category;
DROP TABLE IF EXISTS payment_method;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS user_grade;
DROP TABLE IF EXISTS admin;

SET FOREIGN_KEY_CHECKS = 1;

-- 1. 관리자 테이블
CREATE TABLE admin (
    admin_id VARCHAR(50) PRIMARY KEY,
    admin_pwd VARCHAR(255) NOT NULL,
    admin_name VARCHAR(50) NOT NULL,
    admin_status ENUM('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. 사용자 등급 테이블
CREATE TABLE user_grade (
    user_grade_id VARCHAR(20) PRIMARY KEY,
    user_grade_name VARCHAR(50) NOT NULL,
    grade_criteria_start_price INT NOT NULL DEFAULT 0,
    grade_criteria_end_price INT NOT NULL DEFAULT 999999999,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 사용자 테이블
CREATE TABLE user (
    id_for_admin VARCHAR(50) PRIMARY KEY,
    user_pwd VARCHAR(255) NOT NULL,
    user_name VARCHAR(50) NOT NULL,
    user_email VARCHAR(100) NOT NULL UNIQUE,
    user_phone VARCHAR(20),
    user_address VARCHAR(200),
    user_detail_address VARCHAR(200),
    user_zipcode VARCHAR(10),
    user_birth DATE,
    user_gender ENUM('M', 'F'),
    user_grade_id VARCHAR(20) NOT NULL DEFAULT 'BRONZE',
    user_status ENUM('ACTIVE', 'DORMANT', 'WITHDRAWN') NOT NULL DEFAULT 'ACTIVE',
    reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    withdraw_date TIMESTAMP NULL,
    FOREIGN KEY (user_grade_id) REFERENCES user_grade(user_grade_id)
);

-- 4. 결제 방법 테이블
CREATE TABLE payment_method (
    payment_method_id VARCHAR(30) PRIMARY KEY,
    payment_method_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 대분류 카테고리 테이블
CREATE TABLE top_category (
    top_category INT AUTO_INCREMENT PRIMARY KEY,
    top_category_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 중분류 카테고리 테이블
CREATE TABLE middle_category (
    mid_category INT AUTO_INCREMENT PRIMARY KEY,
    top_category INT NOT NULL,
    mid_category_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (top_category) REFERENCES top_category(top_category) ON DELETE CASCADE
);

-- 7. 소분류 카테고리 테이블
CREATE TABLE low_category (
    low_category INT AUTO_INCREMENT PRIMARY KEY,
    mid_category INT NOT NULL,
    low_category_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mid_category) REFERENCES middle_category(mid_category) ON DELETE CASCADE
);

-- 8. 상품 테이블
CREATE TABLE product (
    isbn VARCHAR(13) PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    publisher VARCHAR(100) NOT NULL,
    publish_date DATE,
    price INT NOT NULL,
    product_description TEXT,
    img VARCHAR(500),
    low_category INT NOT NULL,
    product_status ENUM('AVAILABLE', 'OUT_OF_STOCK', 'DISCONTINUED', 'COMING_SOON') NOT NULL DEFAULT 'AVAILABLE',
    search_count INT NOT NULL DEFAULT 0,
    reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (low_category) REFERENCES low_category(low_category),
    INDEX idx_product_status (product_status),
    INDEX idx_search_count (search_count),
    INDEX idx_reg_date (reg_date),
    INDEX idx_low_category (low_category)
);

-- 9. 재고 테이블
CREATE TABLE stock (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(13) NOT NULL,
    stock_type ENUM('IN', 'OUT') NOT NULL,
    quantity INT NOT NULL,
    before_quantity INT NOT NULL DEFAULT 0,
    after_quantity INT NOT NULL DEFAULT 0,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note VARCHAR(200),
    FOREIGN KEY (isbn) REFERENCES product(isbn) ON DELETE CASCADE,
    INDEX idx_isbn_update_date (isbn, update_date DESC)
);

-- 10. 상품 이력 테이블
CREATE TABLE product_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(13) NOT NULL,
    change_type ENUM('PRICE', 'STATUS', 'STOCK', 'INFO') NOT NULL,
    before_value VARCHAR(200),
    after_value VARCHAR(200),
    changed_by VARCHAR(50),
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (isbn) REFERENCES product(isbn) ON DELETE CASCADE,
    INDEX idx_isbn_change_date (isbn, change_date DESC)
);

-- 11. 장바구니 테이블 (복합키)
CREATE TABLE cart (
    id_for_admin VARCHAR(50) NOT NULL,
    isbn VARCHAR(13) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_for_admin, isbn),
    FOREIGN KEY (id_for_admin) REFERENCES user(id_for_admin) ON DELETE CASCADE,
    FOREIGN KEY (isbn) REFERENCES product(isbn) ON DELETE CASCADE
);

-- 12. 주문 테이블 (복합키)
CREATE TABLE `order` (
    order_id VARCHAR(50) NOT NULL,
    id_for_admin VARCHAR(50) NOT NULL,
    order_status ENUM('PENDING', 'CONFIRMED', 'PREPARING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED') NOT NULL DEFAULT 'PENDING',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount INT NOT NULL,
    delivery_address VARCHAR(200),
    delivery_detail_address VARCHAR(200),
    delivery_zipcode VARCHAR(10),
    delivery_phone VARCHAR(20),
    delivery_request TEXT,
    PRIMARY KEY (order_id, id_for_admin),
    FOREIGN KEY (id_for_admin) REFERENCES user(id_for_admin),
    INDEX idx_order_date (order_date DESC),
    INDEX idx_order_status (order_status)
);

-- 13. 결제 테이블
CREATE TABLE payment (
    payment_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    id_for_admin VARCHAR(50) NOT NULL,
    payment_method_id VARCHAR(30) NOT NULL,
    payment_amount INT NOT NULL,
    payment_status ENUM('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED', 'REFUNDED') NOT NULL DEFAULT 'PENDING',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pg_transaction_id VARCHAR(100),
    FOREIGN KEY (order_id, id_for_admin) REFERENCES `order`(order_id, id_for_admin),
    FOREIGN KEY (payment_method_id) REFERENCES payment_method(payment_method_id),
    INDEX idx_payment_status (payment_status),
    INDEX idx_payment_date (payment_date DESC)
);

-- 14. 주문 상세 테이블 (복합키)
CREATE TABLE order_detail (
    order_id VARCHAR(50) NOT NULL,
    id_for_admin VARCHAR(50) NOT NULL,
    isbn VARCHAR(13) NOT NULL,
    quantity INT NOT NULL,
    unit_price INT NOT NULL,
    total_price INT NOT NULL,
    PRIMARY KEY (order_id, id_for_admin, isbn),
    FOREIGN KEY (order_id, id_for_admin) REFERENCES `order`(order_id, id_for_admin) ON DELETE CASCADE,
    FOREIGN KEY (isbn) REFERENCES product(isbn)
);

-- 15. 상품 리뷰 테이블
CREATE TABLE product_review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(13) NOT NULL,
    id_for_admin VARCHAR(50) NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_content TEXT,
    reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (isbn) REFERENCES product(isbn) ON DELETE CASCADE,
    FOREIGN KEY (id_for_admin) REFERENCES user(id_for_admin) ON DELETE CASCADE,
    INDEX idx_isbn_reg_date (isbn, reg_date DESC),
    INDEX idx_is_deleted (is_deleted)
);

-- 인덱스 추가 생성
CREATE INDEX idx_user_email ON user(user_email);
CREATE INDEX idx_user_status ON user(user_status);
CREATE INDEX idx_user_grade ON user(user_grade_id);
CREATE INDEX idx_product_price ON product(price);
CREATE INDEX idx_product_author ON product(author);
CREATE INDEX idx_product_publisher ON product(publisher);

-- 전문 검색 인덱스 (MySQL 5.7+)
-- ALTER TABLE product ADD FULLTEXT(product_name, author, publisher);

-- 트리거 생성: 재고 변경 시 상품 상태 자동 업데이트 (권한 문제로 주석 처리)
-- DELIMITER //

-- CREATE TRIGGER update_product_status_after_stock_change
--     AFTER INSERT ON stock
--     FOR EACH ROW
-- BEGIN
--     DECLARE current_stock INT DEFAULT 0;
--     
--     -- 최신 재고량 조회
--     SELECT after_quantity INTO current_stock
--     FROM stock 
--     WHERE isbn = NEW.isbn 
--     ORDER BY update_date DESC 
--     LIMIT 1;
--     
--     -- 재고에 따른 상품 상태 업데이트
--     IF current_stock <= 0 THEN
--         UPDATE product 
--         SET product_status = 'OUT_OF_STOCK' 
--         WHERE isbn = NEW.isbn;
--     ELSEIF current_stock > 0 AND (SELECT product_status FROM product WHERE isbn = NEW.isbn) = 'OUT_OF_STOCK' THEN
--         UPDATE product 
--         SET product_status = 'AVAILABLE' 
--         WHERE isbn = NEW.isbn;
--     END IF;
-- END//

-- DELIMITER ;

-- 뷰 생성: 상품과 최신 재고 정보 조합
CREATE VIEW product_with_stock AS
SELECT 
    p.*,
    COALESCE(s.after_quantity, 0) as current_stock,
    s.update_date as stock_update_date
FROM product p
LEFT JOIN (
    SELECT 
        isbn,
        after_quantity,
        update_date,
        ROW_NUMBER() OVER (PARTITION BY isbn ORDER BY update_date DESC) as rn
    FROM stock
) s ON p.isbn = s.isbn AND s.rn = 1;

-- 뷰 생성: 카테고리 계층 구조
CREATE VIEW category_hierarchy AS
SELECT 
    tc.top_category,
    tc.top_category_name,
    mc.mid_category,
    mc.mid_category_name,
    lc.low_category,
    lc.low_category_name
FROM top_category tc
LEFT JOIN middle_category mc ON tc.top_category = mc.top_category
LEFT JOIN low_category lc ON mc.mid_category = lc.mid_category
ORDER BY tc.top_category, mc.mid_category, lc.low_category;

-- 뷰 생성: 주문 요약 정보
CREATE VIEW order_summary AS
SELECT 
    o.order_id,
    o.id_for_admin,
    o.order_status,
    o.order_date,
    o.total_amount,
    p.payment_status,
    p.payment_date,
    p.payment_method_id,
    COUNT(od.isbn) as item_count
FROM `order` o
LEFT JOIN payment p ON o.order_id = p.order_id AND o.id_for_admin = p.id_for_admin
LEFT JOIN order_detail od ON o.order_id = od.order_id AND o.id_for_admin = od.id_for_admin
GROUP BY o.order_id, o.id_for_admin, o.order_status, o.order_date, o.total_amount, 
         p.payment_status, p.payment_date, p.payment_method_id;

-- 저장 프로시저: 상품 재고 업데이트
DELIMITER //

CREATE PROCEDURE UpdateProductStock(
    IN p_isbn VARCHAR(13),
    IN p_quantity INT,
    IN p_stock_type ENUM('IN', 'OUT'),
    IN p_note VARCHAR(200)
)
BEGIN
    DECLARE current_stock INT DEFAULT 0;
    DECLARE new_stock INT DEFAULT 0;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    -- 현재 재고량 조회
    SELECT COALESCE(after_quantity, 0) INTO current_stock
    FROM stock 
    WHERE isbn = p_isbn 
    ORDER BY update_date DESC 
    LIMIT 1;
    
    -- 새로운 재고량 계산
    IF p_stock_type = 'IN' THEN
        SET new_stock = current_stock + p_quantity;
    ELSE
        SET new_stock = current_stock - p_quantity;
        IF new_stock < 0 THEN
            SET new_stock = 0;
        END IF;
    END IF;
    
    -- 재고 이력 추가
    INSERT INTO stock (isbn, stock_type, quantity, before_quantity, after_quantity, note)
    VALUES (p_isbn, p_stock_type, p_quantity, current_stock, new_stock, p_note);
    
    COMMIT;
END//

DELIMITER ;

-- 권한 설정 (필요시)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON bookstore_db.* TO 'bookstore_user'@'localhost';
-- FLUSH PRIVILEGES;

-- 스키마 생성 완료 메시지
SELECT 'YESorNO.24 데이터베이스 스키마 생성이 완료되었습니다.' AS message;