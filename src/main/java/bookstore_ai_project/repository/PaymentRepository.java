package bookstore_ai_project.repository;

import org.springframework.stereotype.Repository;
import org.springframework.data.jpa.repository.JpaRepository;
import bookstore_ai_project.entity.Payment;
import java.util.List;
import java.util.Optional;

@Repository
public interface PaymentRepository extends JpaRepository<Payment, String> {
    List<Payment> findByOrderId(String orderId);
    List<Payment> findByPaymentId(String paymentId);
    List<Payment> findByOrderIdAndIdForAdmin(String orderId, String idForAdmin);
    Optional<Payment> findByPaymentIdAndOrderId(String paymentId, String orderId);
}