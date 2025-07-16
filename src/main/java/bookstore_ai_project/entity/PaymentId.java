package bookstore_ai_project.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.io.Serializable;
import java.util.Objects;

@Embeddable
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PaymentId implements Serializable {
    
    @Column(name = "payment_id")
    private String paymentId;
    
    @Column(name = "order_id")
    private String orderId;
    
    @Column(name = "id_for_admin")
    private String idForAdmin;
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        PaymentId that = (PaymentId) o;
        return Objects.equals(paymentId, that.paymentId) &&
               Objects.equals(orderId, that.orderId) &&
               Objects.equals(idForAdmin, that.idForAdmin);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(paymentId, orderId, idForAdmin);
    }
}