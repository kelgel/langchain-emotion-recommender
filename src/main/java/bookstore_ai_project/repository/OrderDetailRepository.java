package bookstore_ai_project.repository;

import bookstore_ai_project.entity.OrderDetail;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface OrderDetailRepository extends JpaRepository<OrderDetail, String> {
    
    @Query("SELECT od FROM OrderDetail od WHERE od.orderId = :orderId AND od.idForAdmin = :idForAdmin")
    List<OrderDetail> findByOrderIdAndIdForAdmin(@Param("orderId") String orderId, @Param("idForAdmin") String idForAdmin);
}
