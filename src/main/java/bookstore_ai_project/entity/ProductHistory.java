package bookstore_ai_project.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;

@Entity                          // JPA 엔티티임을 표시
@Table(name = "product_history") // DB 테이블명 지정
@Data                            // getter, setter, toString 자동 생성
@NoArgsConstructor               // 기본 생성자
@AllArgsConstructor              // 모든 필드 생성자
public class ProductHistory {

    @Id                                              // 기본키 지정
    @GeneratedValue(strategy = GenerationType.IDENTITY) // 자동 증가
    @Column(name = "product_history_id")             // DB 컬럼명 지정
    private Integer productHistoryId;

    @Column(name = "isbn")
    private String isbn;

    @Enumerated(EnumType.STRING)                     // Enum을 문자열로 저장
    @Column(name = "status_modified_history")
    private StatusModifiedHistory statusModifiedHistory;

    @Column(name = "price_modified_history")
    private Integer priceModifiedHistory;

    @Column(name = "update_date")
    private LocalDateTime updateDate;

    // 연관관계 설정 (ProductHistory와 Product는 다대일 관계)
    @ManyToOne(fetch = FetchType.LAZY)               // 지연 로딩
    @JoinColumn(name = "isbn", insertable = false, updatable = false)
    private Product product;

    // Enum 정의
    public enum StatusModifiedHistory {
        ON_SALE, OUT_OF_PRINT, TEMPORARILY_OUT_OF_STOCK, EXPECTED_IN_STOCK
    }
}