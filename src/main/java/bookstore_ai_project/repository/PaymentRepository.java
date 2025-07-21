package bookstore_ai_project.repository;

import org.springframework.stereotype.Repository;
import org.springframework.data.jpa.repository.JpaRepository;
import bookstore_ai_project.entity.Payment;
import bookstore_ai_project.entity.PaymentId;
import java.util.List;
import java.util.Optional;

@Repository
public interface PaymentRepository extends JpaRepository<Payment, PaymentId> {
    // - 주문번호와 관리자ID로 결제 내역 전체 조회
    List<Payment> findByIdOrderIdAndIdIdForAdmin(String orderId, String idForAdmin);
    List<Payment> findByIdOrderId(String orderId);
    List<Payment> findByIdPaymentId(String paymentId);
    Optional<Payment> findByIdPaymentIdAndIdOrderId(String paymentId, String orderId);
    Optional<Payment> findByIdPaymentIdAndIdOrderIdAndIdIdForAdmin(String paymentId, String orderId, String idForAdmin);
}