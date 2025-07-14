package bookstore_ai_project.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;
import java.util.List;

@Entity                    // JPA 엔티티임을 표시
@Table(name = "`order`")   // order는 SQL 예약어이므로 백틱 사용
@Data                      // getter, setter, toString 자동 생성
@NoArgsConstructor         // 기본 생성자
@AllArgsConstructor        // 모든 필드 생성자
@IdClass(OrderId.class)    // 복합키 클래스 지정
public class Order {

    @Id                                // 복합키 일부
    @Column(name = "order_id")         // DB 컬럼명과 길이 지정
    private String orderId;

    @Id                                // 복합키 일부
    @Column(name = "id_for_admin")
    private String idForAdmin;

    @Column(name = "total_product_category")
    private Integer totalProductCategory;

    @Column(name = "total_product_quantity")
    private Integer totalProductQuantity;

    @Column(name = "total_paid_price")
    private Integer totalPaidPrice;

    @Column(name = "order_date")
    private LocalDateTime orderDate;

    @Enumerated(EnumType.STRING)                     // Enum을 문자열로 저장
    @Column(name = "order_status")
    private OrderStatus orderStatus;

    @Column(name = "update_date")
    private LocalDateTime updateDate;

    // 연관관계 설정 (Order와 User는 다대일 관계)
    @ManyToOne(fetch = FetchType.LAZY)               // 지연 로딩
    @JoinColumn(name = "id_for_admin", insertable = false, updatable = false)
    private User user;

    // 연관관계 설정 (Order와 OrderDetail는 일대다 관계)
    @OneToMany(mappedBy = "order", fetch = FetchType.LAZY)
    private List<OrderDetail> orderDetails;

    // 연관관계 설정 (Order와 Payment는 일대다 관계)
    @OneToMany(mappedBy = "order", fetch = FetchType.LAZY)
    private List<Payment> payments;

    // Enum 정의
    public enum OrderStatus {
        ORDER_REQUESTED, ORDER_FAILED, ORDER_COMPLETED,
        PREPARING_PRODUCT, SHIPPING, DELIVERED,
        CANCEL_COMPLETED
    }
}