package bookstore_ai_project.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;

@Entity                    // JPA 엔티티임을 표시
@Table(name = "stock")     // DB 테이블명 지정
@Data                      // getter, setter, toString 자동 생성
@NoArgsConstructor         // 기본 생성자
@AllArgsConstructor        // 모든 필드 생성자
public class Stock {

    @Id                                              // 기본키 지정
    @GeneratedValue(strategy = GenerationType.IDENTITY) // 자동 증가
    @Column(name = "stock_id")                       // DB 컬럼명 지정
    private Integer stockId;

    @Column(name = "isbn")
    private String isbn;

    @Enumerated(EnumType.STRING)                     // Enum을 문자열로 저장
    @Column(name = "in_out_type")
    private InOutType inOutType;

    @Column(name = "in_out_quantity")
    private Integer inOutQuantity;

    @Column(name = "before_quantity")
    private Integer beforeQuantity;

    @Column(name = "after_quantity")
    private Integer afterQuantity;

    @Column(name = "update_date")
    private LocalDateTime updateDate;

    // 연관관계 설정 (Stock과 Product는 다대일 관계)
    @ManyToOne(fetch = FetchType.LAZY)               // 지연 로딩
    @JoinColumn(name = "isbn", insertable = false, updatable = false)
    private Product product;

    // Enum 정의
    public enum InOutType {
        INBOUND, OUTBOUND
    }
}