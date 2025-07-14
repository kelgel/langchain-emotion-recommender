package bookstore_ai_project.repository;

import bookstore_ai_project.entity.ProductHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ProductHistoryRepository extends JpaRepository<ProductHistory, Integer> {
    
    // 특정 상품의 이력 조회 (최신순)
    @Query("SELECT ph FROM ProductHistory ph WHERE ph.isbn = :isbn ORDER BY ph.updateDate DESC")
    List<ProductHistory> findByIsbnOrderByUpdateDateDesc(@Param("isbn") String isbn);
    
    // 특정 상품의 최신 이력 조회
    @Query("SELECT ph FROM ProductHistory ph WHERE ph.isbn = :isbn ORDER BY ph.updateDate DESC")
    Optional<ProductHistory> findLatestByIsbn(@Param("isbn") String isbn);
}
