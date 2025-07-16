package bookstore_ai_project.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;

@Entity                    // JPA 엔티티임을 표시
@Table(name = "payment")   // DB 테이블명 지정
@Data                      // getter, setter, toString 자동 생성
@NoArgsConstructor         // 기본 생성자
@AllArgsConstructor        // 모든 필드 생성자
public class Payment {

    @EmbeddedId
    private PaymentId id;

    @Column(name = "payment_method_id")
    private String paymentMethodId;

    @Column(name = "payment_date")
    private LocalDateTime paymentDate;

    @Enumerated(EnumType.STRING)                     // Enum을 문자열로 저장
    @Column(name = "payment_status")
    private PaymentStatus paymentStatus;

    @Column(name = "update_date")
    private LocalDateTime updateDate;

    // 연관관계 설정 (Payment와 Order는 다대일 관계)
    @ManyToOne(fetch = FetchType.LAZY)               // 지연 로딩
    @JoinColumns({
        @JoinColumn(name = "order_id", referencedColumnName = "order_id", insertable = false, updatable = false),
        @JoinColumn(name = "id_for_admin", referencedColumnName = "id_for_admin", insertable = false, updatable = false)
    })
    private Order order;

    // 연관관계 설정 (Payment와 PaymentMethod는 다대일 관계)
    @ManyToOne(fetch = FetchType.LAZY)               // 지연 로딩
    @JoinColumn(name = "payment_method_id", insertable = false, updatable = false)
    private PaymentMethod paymentMethod;

    // Enum 정의
    public enum PaymentStatus {
        PAYMENT_ATTEMPT, PAYMENT_FAILED, PAYMENT_COMPLETED
    }
}