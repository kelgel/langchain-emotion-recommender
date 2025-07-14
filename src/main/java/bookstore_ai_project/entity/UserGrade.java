package bookstore_ai_project.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.util.List;

@Entity                     // JPA 엔티티임을 표시
@Table(name = "user_grade") // DB 테이블명 지정
@Data                       // getter, setter, toString 자동 생성
@NoArgsConstructor          // 기본 생성자
@AllArgsConstructor         // 모든 필드 생성자
public class UserGrade {

    @Id                                              // 기본키 지정
    @Column(name = "user_grade_id")                  // DB 컬럼명과 길이 지정
    private String userGradeId;

    @Enumerated(EnumType.STRING)                     // Enum을 문자열로 저장
    @Column(name = "user_grade_name")
    private GradeName userGradeName;

    @Column(name = "grade_criteria_start_price")
    private Integer gradeCriteriaStartPrice;

    @Column(name = "grade_criteria_end_price")
    private Integer gradeCriteriaEndPrice;

    // 연관관계 설정 (UserGrade와 User는 일대다 관계)
    @OneToMany(mappedBy = "userGrade", fetch = FetchType.LAZY)  // 지연 로딩
    private List<User> users;

    // Enum 정의
    public enum GradeName {
        BRONZE, SILVER, GOLD, PLATINUM
    }
}