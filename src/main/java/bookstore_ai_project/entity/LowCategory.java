package bookstore_ai_project.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.util.List;

@Entity                       // JPA 엔티티임을 표시
@Table(name = "low_category") // DB 테이블명 지정
@Data                         // getter, setter, toString 자동 생성
@NoArgsConstructor            // 기본 생성자
@AllArgsConstructor           // 모든 필드 생성자
public class LowCategory {

    @Id                                              // 기본키 지정
    @Column(name = "low_category")                   // DB 컬럼명 지정
    private Integer lowCategory;

    @Column(name = "mid_category")
    private Integer midCategory;

    @Column(name = "low_category_name")
    private String lowCategoryName;

    // 연관관계 설정 (LowCategory와 MiddleCategory는 다대일 관계)
    @ManyToOne(fetch = FetchType.LAZY)               // 지연 로딩
    @JoinColumn(name = "mid_category", insertable = false, updatable = false)
    private MiddleCategory middleCategoryEntity;

    // 연관관계 설정 (LowCategory와 Product는 일대다 관계)
    @OneToMany(mappedBy = "lowCategoryEntity", fetch = FetchType.LAZY)
    private List<Product> products;
}