package bookstore_ai_project.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;

@Entity                         // JPA 엔티티임을 표시
@Table(name = "product_review") // DB 테이블명 지정
@Data                           // getter, setter, toString 자동 생성
@NoArgsConstructor              // 기본 생성자
@AllArgsConstructor             // 모든 필드 생성자
public class ProductReview {

    @Id                                              // 기본키 지정
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "product_review_id")              // DB 컬럼명 지정
    private Integer productReviewId;

    @Column(name = "order_id")
    private String orderId;

    @Column(name = "id_for_admin")
    private String idForAdmin;

    @Column(name = "isbn")
    private String isbn;

    @Column(name = "review_title")
    private String reviewTitle;

    @Column(name = "review_content", columnDefinition = "TEXT")  // TEXT 타입
    private String reviewContent;

    @Column(name = "emotion_keyword", columnDefinition = "TEXT") // TEXT 타입
    private String emotionKeyword;

    @Column(name = "reg_date")
    private LocalDateTime regDate;

    @Column(name = "update_date")
    private LocalDateTime updateDate;

    @Column(name = "delete_date")
    private LocalDateTime deleteDate;

    // 연관관계 설정 (ProductReview와 OrderDetail은 다대일 관계)
    @ManyToOne(fetch = FetchType.LAZY)               // 지연 로딩
    @JoinColumns({
        @JoinColumn(name = "order_id", referencedColumnName = "order_id", insertable = false, updatable = false),
        @JoinColumn(name = "id_for_admin", referencedColumnName = "id_for_admin", insertable = false, updatable = false),
        @JoinColumn(name = "isbn", referencedColumnName = "isbn", insertable = false, updatable = false)
    })
    private OrderDetail orderDetail;
}