package bookstore_ai_project.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import bookstore_ai_project.entity.ProductReview;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

public interface ProductReviewRepository extends JpaRepository<ProductReview, Integer> {
    // - ISBN으로 리뷰 전체 조회
    java.util.List<ProductReview> findAllByIsbn(String isbn);
    
    // 특정 사용자가 특정 상품에 리뷰를 작성했는지 확인
    @Query("SELECT COUNT(pr) > 0 FROM ProductReview pr WHERE pr.isbn = :isbn AND pr.idForAdmin = :idForAdmin")
    boolean existsByIsbnAndIdForAdmin(@Param("isbn") String isbn, @Param("idForAdmin") String idForAdmin);

    @Query("SELECT COUNT(pr) > 0 FROM ProductReview pr WHERE pr.isbn = :isbn AND pr.idForAdmin = :idForAdmin AND pr.deleteDate IS NULL")
    boolean existsActiveByIsbnAndIdForAdmin(@Param("isbn") String isbn, @Param("idForAdmin") String idForAdmin);

    // 주문별 리뷰 조회 (동일한 책을 여러 번 주문한 경우를 위해)
    @Query("SELECT pr FROM ProductReview pr WHERE pr.orderId = :orderId AND pr.isbn = :isbn AND pr.idForAdmin = :idForAdmin AND pr.deleteDate IS NULL")
    java.util.Optional<ProductReview> findActiveByOrderIdAndIsbnAndIdForAdmin(@Param("orderId") String orderId, @Param("isbn") String isbn, @Param("idForAdmin") String idForAdmin);

    // 특정 주문의 특정 상품에 대해 리뷰가 존재하는지 확인
    @Query("SELECT COUNT(pr) > 0 FROM ProductReview pr WHERE pr.orderId = :orderId AND pr.isbn = :isbn AND pr.idForAdmin = :idForAdmin AND pr.deleteDate IS NULL")
    boolean existsActiveByOrderIdAndIsbnAndIdForAdmin(@Param("orderId") String orderId, @Param("isbn") String isbn, @Param("idForAdmin") String idForAdmin);

    Page<ProductReview> findByIsbnAndDeleteDateIsNull(String isbn, Pageable pageable);
    
    // 상품상세페이지용: ISBN으로 리뷰 조회 시 작성자 정보 JOIN
    @Query("SELECT pr, u.userNickname FROM ProductReview pr " +
           "JOIN OrderDetail od ON pr.orderId = od.orderId AND pr.idForAdmin = od.idForAdmin AND pr.isbn = od.isbn " +
           "JOIN User u ON od.idForAdmin = u.idForAdmin " +
           "WHERE pr.isbn = :isbn AND pr.deleteDate IS NULL " +
           "ORDER BY pr.regDate DESC")
    Page<Object[]> findByIsbnWithUserNicknameAndDeleteDateIsNull(@Param("isbn") String isbn, Pageable pageable);
}
