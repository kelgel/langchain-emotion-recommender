package bookstore_ai_project.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.util.List;

@Entity                       // JPA 엔티티임을 표시
@Table(name = "top_category") // DB 테이블명 지정
@Data                         // getter, setter, toString 자동 생성
@NoArgsConstructor            // 기본 생성자
@AllArgsConstructor           // 모든 필드 생성자
public class TopCategory {

    @Id                                              // 기본키 지정
    @Column(name = "top_category")                   // DB 컬럼명 지정
    private Integer topCategory;

    @Column(name = "top_category_name")
    private String topCategoryName;

    // 연관관계 설정 (TopCategory와 MiddleCategory는 일대다 관계)
    @OneToMany(mappedBy = "topCategoryEntity", fetch = FetchType.LAZY)  // 지연 로딩
    private List<MiddleCategory> middleCategories;
}