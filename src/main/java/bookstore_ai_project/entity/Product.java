package bookstore_ai_project.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Entity                    // JPA 엔티티임을 표시
@Table(name = "product")   // DB 테이블명 지정
@Data                      // getter, setter, toString 자동 생성
@NoArgsConstructor         // 기본 생성자
@AllArgsConstructor        // 모든 필드 생성자
public class Product {

    @Id                                // 기본키 지정
    @Column(name = "isbn")             // DB 컬럼명과 길이 지정
    private String isbn;

    @Column(name = "low_category")
    private Integer lowCategory;

    @Column(name = "product_name")
    private String productName;

    @Column(name = "author")
    private String author;

    @Column(name = "publisher")
    private String publisher;

    @Column(name = "price")
    private Integer price;

    @Column(name = "rate", precision = 10, scale = 1)  // decimal(10,1) 매핑
    private BigDecimal rate;

    @Column(name = "brief_description", columnDefinition = "TEXT")  // TEXT 타입
    private String briefDescription;

    @Column(name = "detail_description", columnDefinition = "TEXT") // TEXT 타입
    private String detailDescription;

    @Column(name = "emotion_keyword", columnDefinition = "TEXT") // TEXT 타입
    private String emotionKeyword;

    @Column(name = "product_keyword", columnDefinition = "TEXT") // TEXT 타입
    private String productKeyword;

    @Column(name = "img", length = 1000)
    private String img;

    @Column(name = "width")
    private Integer width;

    @Column(name = "height")
    private Integer height;

    @Column(name = "page")
    private Integer page;

    @Enumerated(EnumType.STRING)                     // Enum을 문자열로 저장
    @Column(name = "sales_status")
    private SalesStatus salesStatus;

    @Column(name = "search_count")
    private Integer searchCount;

    @Column(name = "reg_date", columnDefinition = "DATE")
    private LocalDateTime regDate;

    // 연관관계 설정 (Product와 LowCategory는 다대일 관계)
    @ManyToOne(fetch = FetchType.LAZY)               // 지연 로딩
    @JoinColumn(name = "low_category", insertable = false, updatable = false)
    private LowCategory lowCategoryEntity;

    // 연관관계 설정 (Product와 Cart는 일대다 관계)
    @OneToMany(mappedBy = "product", fetch = FetchType.LAZY)
    private List<Cart> carts;

    // 연관관계 설정 (Product와 OrderDetail는 일대다 관계)
    @OneToMany(mappedBy = "product", fetch = FetchType.LAZY)
    private List<OrderDetail> orderDetails;

    // 연관관계 설정 (Product와 ProductHistory는 일대다 관계)
    @OneToMany(mappedBy = "product", fetch = FetchType.LAZY)
    private List<ProductHistory> productHistories;

    // ProductReview는 이제 OrderDetail을 통해 관리되므로 직접 관계 제거
    // 필요시 @JoinColumn으로 단방향 관계로 설정 가능하지만 현재는 제거

    // 연관관계 설정 (Product와 Stock는 일대다 관계)
    @OneToMany(mappedBy = "product", fetch = FetchType.LAZY)
    private List<Stock> stocks;

    // Enum 정의
    public enum SalesStatus {
        ON_SALE, OUT_OF_PRINT, TEMPORARILY_OUT_OF_STOCK, EXPECTED_IN_STOCK
    }
}