package bookstore_ai_project.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.repository.query.Param;
import java.util.List;
import bookstore_ai_project.entity.Product;
import java.time.LocalDateTime;
import org.springframework.data.jpa.domain.Specification;

public interface ProductRepository extends JpaRepository<Product, String> {
    /*
      대분류별 책 개수 집계
      비즈니스 로직: 카테고리별 상품 통계
    */
    @Query("SELECT t.topCategory, t.topCategoryName, COUNT(p) FROM Product p " +
           "JOIN LowCategory l ON p.lowCategory = l.lowCategory " +
           "JOIN MiddleCategory m ON l.midCategory = m.midCategory " +
           "JOIN TopCategory t ON m.topCategory = t.topCategory " +
           "GROUP BY t.topCategory, t.topCategoryName")
    List<Object[]> countBooksByTopCategory();

    /*
      중분류별 책 개수 집계
      비즈니스 로직: 카테고리별 상품 통계
    */
    @Query("SELECT m.midCategory, m.midCategoryName, t.topCategory, t.topCategoryName, COUNT(p) FROM Product p " +
           "JOIN LowCategory l ON p.lowCategory = l.lowCategory " +
           "JOIN MiddleCategory m ON l.midCategory = m.midCategory " +
           "JOIN TopCategory t ON m.topCategory = t.topCategory " +
           "GROUP BY m.midCategory, m.midCategoryName, t.topCategory, t.topCategoryName")
    List<Object[]> countBooksByMiddleCategory();

    /*
      소분류별 책 개수 집계
      비즈니스 로직: 카테고리별 상품 통계
    */
    @Query("SELECT l.lowCategory, l.lowCategoryName, m.midCategory, m.midCategoryName, t.topCategory, t.topCategoryName, COUNT(p) FROM Product p " +
           "JOIN LowCategory l ON p.lowCategory = l.lowCategory " +
           "JOIN MiddleCategory m ON l.midCategory = m.midCategory " +
           "JOIN TopCategory t ON m.topCategory = t.topCategory " +
           "GROUP BY l.lowCategory, l.lowCategoryName, m.midCategory, m.midCategoryName, t.topCategory, t.topCategoryName")
    List<Object[]> countBooksByLowCategory();

    // - 인기검색어 Top N 조회
    @Query("SELECT p.isbn, p.productName, p.img, p.author, p.price, p.searchCount FROM Product p ORDER BY p.searchCount DESC, p.productName ASC")
    List<Object[]> findTopPopularProducts(org.springframework.data.domain.Pageable pageable);

    // - 신상품 Top N 조회
    @Query("SELECT p.isbn, p.productName, p.img, p.author, p.price, p.regDate FROM Product p ORDER BY p.regDate DESC, p.productName ASC")
    List<Object[]> findTopNewProducts(org.springframework.data.domain.Pageable pageable);

    /*
      검색수 증가 처리
      비즈니스 로직: 인기상품 집계용
    */
    @Modifying
    @Query("UPDATE Product p SET p.searchCount = COALESCE(p.searchCount, 0) + 1 WHERE p.isbn = :isbn")
    void increaseSearchCount(@Param("isbn") String isbn);

    /*
      기간별 베스트셀러 집계 (주간/월간/연간)
      비즈니스 로직: 판매량 기준 인기상품 분석
    */
    @Query(value = "SELECT od.isbn, SUM(od.order_item_quantity) AS total_quantity " +
            "FROM order_detail od " +
            "JOIN `order` o ON od.order_id = o.order_id " +
            "WHERE o.order_status = 'DELIVERED' " +
            "AND o.order_date BETWEEN :startDate AND :endDate " +
            "GROUP BY od.isbn " +
            "ORDER BY total_quantity DESC ",
            nativeQuery = true)
    java.util.List<Object[]> findBestsellerByPeriod(@Param("startDate") LocalDateTime startDate, @Param("endDate") LocalDateTime endDate, org.springframework.data.domain.Pageable pageable);

    // - ISBN으로 상품 상세 조회
    Product findByIsbn(String isbn);

    // - ISBN 존재 여부 확인
    boolean existsByIsbn(String isbn);

    // - 소분류별 상품 목록 조회 (최신순)
    @Query("SELECT p FROM Product p WHERE p.lowCategory = :lowCategoryId ORDER BY p.regDate DESC")
    List<Product> findByLowCategoryOrderByRegDateDesc(@Param("lowCategoryId") Integer lowCategoryId, org.springframework.data.domain.Pageable pageable);

    // - 소분류별 상품 목록 조회 (평점순)
    @Query("SELECT p FROM Product p WHERE p.lowCategory = :lowCategoryId ORDER BY p.rate DESC NULLS LAST")
    List<Product> findByLowCategoryOrderByRateDesc(@Param("lowCategoryId") Integer lowCategoryId, org.springframework.data.domain.Pageable pageable);

    // - 소분류별 상품 목록 조회 (높은 가격순)
    @Query("SELECT p FROM Product p WHERE p.lowCategory = :lowCategoryId ORDER BY p.price DESC")
    List<Product> findByLowCategoryOrderByPriceDesc(@Param("lowCategoryId") Integer lowCategoryId, org.springframework.data.domain.Pageable pageable);

    // - 소분류별 상품 목록 조회 (낮은 가격순)
    @Query("SELECT p FROM Product p WHERE p.lowCategory = :lowCategoryId ORDER BY p.price ASC")
    List<Product> findByLowCategoryOrderByPriceAsc(@Param("lowCategoryId") Integer lowCategoryId, org.springframework.data.domain.Pageable pageable);

    // - 소분류별 상품 개수 집계
    @Query("SELECT COUNT(p) FROM Product p WHERE p.lowCategory = :lowCategoryId")
    long countByLowCategory(@Param("lowCategoryId") Integer lowCategoryId);

    /*
      소분류별 판매량순 상품 목록 집계
      비즈니스 로직: 베스트셀러 분석
    */
    @Query(value = "SELECT p.isbn, p.product_name, p.author, p.publisher, p.price, p.rate, p.img, p.reg_date, " +
            "COALESCE(SUM(od.order_item_quantity), 0) as sales_count, p.sales_status " +
            "FROM product p " +
            "LEFT JOIN order_detail od ON p.isbn = od.isbn " +
            "LEFT JOIN `order` o ON od.order_id = o.order_id AND o.order_status = 'DELIVERED' " +
            "WHERE p.low_category = :lowCategoryId " +
            "GROUP BY p.isbn, p.product_name, p.author, p.publisher, p.price, p.rate, p.img, p.reg_date, p.sales_status " +
            "ORDER BY sales_count DESC, p.product_name ASC",
            nativeQuery = true)
    List<Object[]> findProductsByLowCategoryOrderBySalesDesc(@Param("lowCategoryId") Integer lowCategoryId, org.springframework.data.domain.Pageable pageable);

    /*
      전체 상품 판매량순 집계
      비즈니스 로직: 전체 베스트셀러 분석
    */
    @Query(value = "SELECT p.isbn, p.product_name, p.author, p.publisher, p.price, p.rate, p.img, p.reg_date, " +
            "COALESCE(SUM(od.order_item_quantity), 0) as sales_count, p.sales_status " +
            "FROM product p " +
            "LEFT JOIN order_detail od ON p.isbn = od.isbn " +
            "LEFT JOIN `order` o ON od.order_id = o.order_id AND o.order_status = 'DELIVERED' " +
            "GROUP BY p.isbn, p.product_name, p.author, p.publisher, p.price, p.rate, p.img, p.reg_date, p.sales_status " +
            "ORDER BY sales_count DESC, p.product_name ASC",
            nativeQuery = true)
    List<Object[]> findAllProductsOrderBySalesDesc(org.springframework.data.domain.Pageable pageable);

    /*
      전체 상품 판매량순 집계 (검색 조건 포함)
      비즈니스 로직: 검색+베스트셀러 분석
    */
    @Query(value = "SELECT p.isbn, p.product_name, p.author, p.publisher, p.price, p.rate, p.img, p.reg_date, " +
            "COALESCE(SUM(od.order_item_quantity), 0) as sales_count, p.sales_status " +
            "FROM product p " +
            "LEFT JOIN order_detail od ON p.isbn = od.isbn " +
            "LEFT JOIN `order` o ON od.order_id = o.order_id AND o.order_status = 'DELIVERED' " +
            "WHERE (:title IS NULL OR p.product_name LIKE CONCAT('%', :title, '%')) " +
            "AND (:author IS NULL OR p.author LIKE CONCAT('%', :author, '%')) " +
            "AND (:publisher IS NULL OR p.publisher LIKE CONCAT('%', :publisher, '%')) " +
            "GROUP BY p.isbn, p.product_name, p.author, p.publisher, p.price, p.rate, p.img, p.reg_date, p.sales_status " +
            "ORDER BY sales_count DESC, p.product_name ASC",
            nativeQuery = true)
    List<Object[]> findAllProductsOrderBySalesDescWithSearch(@Param("title") String title, 
                                                            @Param("author") String author, 
                                                            @Param("publisher") String publisher,
                                                            org.springframework.data.domain.Pageable pageable);

    // - 동적 검색(소분류+제목+저자+출판사) 페이징+정렬
    List<Product> findAll(Specification<Product> spec, org.springframework.data.domain.Pageable pageable);
    // - 동적 검색 조건별 개수 집계
    long count(Specification<Product> spec);
    
    /*
      전체 상품 검색 조건별 개수 집계
      비즈니스 로직: 검색 결과 통계
    */
    @Query(value = "SELECT COUNT(*) FROM product p " +
            "WHERE (:title IS NULL OR p.product_name LIKE CONCAT('%', :title, '%')) " +
            "AND (:author IS NULL OR p.author LIKE CONCAT('%', :author, '%')) " +
            "AND (:publisher IS NULL OR p.publisher LIKE CONCAT('%', :publisher, '%'))",
            nativeQuery = true)
    long countAllProductsWithSearch(@Param("title") String title, 
                                   @Param("author") String author, 
                                   @Param("publisher") String publisher);
}
