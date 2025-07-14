package bookstore_ai_project.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Entity                       // JPA 엔티티임을 표시
@Table(name = "order_detail") // DB 테이블명 지정
@Data                         // getter, setter, toString 자동 생성
@NoArgsConstructor            // 기본 생성자
@AllArgsConstructor           // 모든 필드 생성자
@IdClass(OrderDetailId.class) // 복합키 클래스 지정
public class OrderDetail {

    @Id                                // 복합키 일부
    @Column(name = "order_id")         // DB 컬럼명과 길이 지정
    private String orderId;

    @Id                                // 복합키 일부
    @Column(name = "id_for_admin")
    private String idForAdmin;

    @Id                                // 복합키 일부
    @Column(name = "isbn")
    private String isbn;

    @Column(name = "order_item_quantity")
    private Integer orderItemQuantity;

    @Column(name = "each_product_price")
    private Integer eachProductPrice;

    @Column(name = "total_product_price")
    private Integer totalProductPrice;

    // 연관관계 설정 (OrderDetail과 Order는 다대일 관계)
    @ManyToOne(fetch = FetchType.LAZY)               // 지연 로딩
    @JoinColumns({
        @JoinColumn(name = "order_id", referencedColumnName = "order_id", insertable = false, updatable = false),
        @JoinColumn(name = "id_for_admin", referencedColumnName = "id_for_admin", insertable = false, updatable = false)
    })
    private Order order;

    // 연관관계 설정 (OrderDetail과 Product는 다대일 관계)
    @ManyToOne(fetch = FetchType.LAZY)               // 지연 로딩
    @JoinColumn(name = "isbn", insertable = false, updatable = false)
    private Product product;
}