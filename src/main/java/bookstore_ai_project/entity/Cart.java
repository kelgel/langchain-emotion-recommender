package bookstore_ai_project.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;

@Entity                    // JPA 엔티티임을 표시
@Table(name = "cart")      // DB 테이블명 지정
@Data                      // getter, setter, toString 자동 생성
@NoArgsConstructor         // 기본 생성자
@AllArgsConstructor        // 모든 필드 생성자
@IdClass(CartId.class)     // 복합키 클래스 지정
public class Cart {

    @Id                                // 복합키 일부
    @Column(name = "id_for_admin")     // DB 컬럼명과 길이 지정
    private String idForAdmin;

    @Id                                // 복합키 일부
    @Column(name = "isbn")
    private String isbn;

    @Column(name = "product_quantity")
    private Integer productQuantity;

    @Column(name = "cart_reg_date")
    private LocalDateTime cartRegDate;

    // 연관관계 설정 (Cart와 User는 다대일 관계)
    @ManyToOne(fetch = FetchType.LAZY)               // 지연 로딩
    @JoinColumn(name = "id_for_admin", insertable = false, updatable = false)
    private User user;

    // 연관관계 설정 (Cart와 Product는 다대일 관계)
    @ManyToOne(fetch = FetchType.LAZY)               // 지연 로딩
    @JoinColumn(name = "isbn", insertable = false, updatable = false)
    private Product product;
}