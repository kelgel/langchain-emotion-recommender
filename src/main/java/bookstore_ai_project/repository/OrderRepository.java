package bookstore_ai_project.repository;

import bookstore_ai_project.entity.Order;
import bookstore_ai_project.entity.OrderId;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.time.LocalDateTime;

@Repository
public interface OrderRepository extends JpaRepository<Order, OrderId> {
    
    // - 관리자 ID로 주문 내역 조회 (최신순)
    @Query("SELECT o FROM Order o WHERE o.idForAdmin = :idForAdmin ORDER BY o.orderDate DESC")
    List<Order> findByIdForAdminOrderByOrderDateDesc(@Param("idForAdmin") String idForAdmin);
    
    /*
      관리자용 복합 검색 쿼리 (userAdminIds가 있는 경우)
      비즈니스 로직: 주문 내역 필터링(관리자별)
    */
    @Query("SELECT o FROM Order o WHERE " +
           "(:orderId IS NULL OR :orderId = '' OR o.orderId LIKE %:orderId%) AND " +
           "(o.idForAdmin IN :userAdminIds) AND " +
           "(:minAmount IS NULL OR o.totalPaidPrice >= :minAmount) AND " +
           "(:maxAmount IS NULL OR o.totalPaidPrice <= :maxAmount) AND " +
           "(:startDate IS NULL OR o.orderDate >= :startDate) AND " +
           "(:endDate IS NULL OR o.orderDate <= :endDate) AND " +
           "(:status IS NULL OR o.orderStatus = :status)")
    Page<Order> findOrdersWithUserSearch(
            @Param("orderId") String orderId,
            @Param("userAdminIds") List<String> userAdminIds,
            @Param("minAmount") Integer minAmount,
            @Param("maxAmount") Integer maxAmount,
            @Param("startDate") LocalDateTime startDate,
            @Param("endDate") LocalDateTime endDate,
            @Param("status") Order.OrderStatus status,
            Pageable pageable);
            
    /*
      관리자용 복합 검색 쿼리 (userAdminIds가 없는 경우)
      비즈니스 로직: 주문 내역 필터링(전체)
    */
    @Query("SELECT o FROM Order o WHERE " +
           "(:orderId IS NULL OR :orderId = '' OR o.orderId LIKE %:orderId%) AND " +
           "(:minAmount IS NULL OR o.totalPaidPrice >= :minAmount) AND " +
           "(:maxAmount IS NULL OR o.totalPaidPrice <= :maxAmount) AND " +
           "(:startDate IS NULL OR o.orderDate >= :startDate) AND " +
           "(:endDate IS NULL OR o.orderDate <= :endDate) AND " +
           "(:status IS NULL OR o.orderStatus = :status)")
    Page<Order> findOrdersWithoutUserSearch(
            @Param("orderId") String orderId,
            @Param("minAmount") Integer minAmount,
            @Param("maxAmount") Integer maxAmount,
            @Param("startDate") LocalDateTime startDate,
            @Param("endDate") LocalDateTime endDate,
            @Param("status") Order.OrderStatus status,
            Pageable pageable);
}
