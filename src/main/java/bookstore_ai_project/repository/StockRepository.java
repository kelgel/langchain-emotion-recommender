package bookstore_ai_project.repository;

import bookstore_ai_project.entity.Stock;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface StockRepository extends JpaRepository<Stock, Integer> {

    // 특정 상품의 입출고 이력 조회 (최신순)
    @Query("SELECT s FROM Stock s WHERE s.isbn = :isbn ORDER BY s.updateDate DESC")
    List<Stock> findByIsbnOrderByUpdateDateDesc(@Param("isbn") String isbn);

    // 특정 상품의 최신 입출고 이력 조회
    @Query("SELECT s FROM Stock s WHERE s.isbn = :isbn ORDER BY s.updateDate DESC")
    Optional<Stock> findLatestByIsbn(@Param("isbn") String isbn);

    // - ISBN으로 최신 재고 조회 (Native Query)
    @Query(value = "SELECT after_quantity FROM stock WHERE isbn = :isbn ORDER BY update_date DESC LIMIT 1", nativeQuery = true)
    Integer findCurrentStockByIsbnNative(@Param("isbn") String isbn);

    // - ISBN으로 최신 재고 조회 (JPA Query)
    @Query("SELECT s.afterQuantity FROM Stock s WHERE s.isbn = :isbn ORDER BY s.updateDate DESC")
    List<Integer> findCurrentStockListByIsbn(@Param("isbn") String isbn, org.springframework.data.domain.Pageable pageable);

    // 디버깅을 위한 특정 ISBN의 모든 Stock 데이터 조회
    @Query("SELECT s FROM Stock s WHERE s.isbn = :isbn ORDER BY s.updateDate DESC")
    List<Stock> findAllByIsbnForDebug(@Param("isbn") String isbn);
}
