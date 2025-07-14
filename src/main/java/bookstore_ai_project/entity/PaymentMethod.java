package bookstore_ai_project.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.util.List;

@Entity                         // JPA 엔티티임을 표시
@Table(name = "payment_method") // DB 테이블명 지정
@Data                           // getter, setter, toString 자동 생성
@NoArgsConstructor              // 기본 생성자
@AllArgsConstructor             // 모든 필드 생성자
public class PaymentMethod {

    @Id                                 // 기본키 지정
    @Column(name = "payment_method_id") // DB 컬럼명과 길이 지정
    private String paymentMethodId;

    @Column(name = "payment_method_name")
    private String paymentMethodName;

    @Column(name = "is_active")
    private Boolean isActive;           // tinyint(1) -> Boolean 매핑

    // 연관관계 설정 (PaymentMethod와 Payment는 일대다 관계)
    @OneToMany(mappedBy = "paymentMethod", fetch = FetchType.LAZY)  // 지연 로딩
    private List<Payment> payments;
}