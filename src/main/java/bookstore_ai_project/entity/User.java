package bookstore_ai_project.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Entity                    // JPA 엔티티임을 표시
@Table(name = "user")      // DB 테이블명 지정
@Data                      // getter, setter, toString 자동 생성
@NoArgsConstructor         // 기본 생성자
@AllArgsConstructor        // 모든 필드 생성자
public class User {

    @Id                                // 기본키 지정
    @Column(name = "id_for_admin")     // DB 컬럼명과 길이 지정
    private String idForAdmin;

    @Column(name = "id_for_user")
    private String idForUser;

    @Column(name = "user_pwd")
    private String userPwd;

    @Column(name = "user_name")
    private String userName;

    @Column(name = "user_nickname")
    private String userNickname;

    @Column(name = "user_birth")
    private LocalDate userBirth;

    @Enumerated(EnumType.STRING)        // Enum을 문자열로 저장
    @Column(name = "user_gender")
    private Gender userGender;

    @Column(name = "user_email")
    private String userEmail;

    @Column(name = "user_phone_number")
    private String userPhoneNumber;

    @Column(name = "user_address")
    private String userAddress;

    @Column(name = "user_address_detail")
    private String userAddressDetail;

    @Column(name = "user_grade_id")
    private String userGradeId;

    @Enumerated(EnumType.STRING)         // Enum을 문자열로 저장
    @Column(name = "user_status")
    private UserStatus userStatus;

    @Column(name = "last_login_date")
    private LocalDateTime lastLoginDate;

    @Column(name = "reg_date")
    private LocalDateTime regDate;

    @Column(name = "update_date")
    private LocalDateTime updateDate;

    // 연관관계 설정 (User와 UserGrade는 다대일 관계)
    @ManyToOne(fetch = FetchType.LAZY)   // 지연 로딩
    @JoinColumn(name = "user_grade_id", insertable = false, updatable = false)
    private UserGrade userGrade;

    // 연관관계 설정 (User와 Cart는 일대다 관계)
    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
    private List<Cart> carts;

    // 연관관계 설정 (User와 Order는 일대다 관계)
    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
    private List<Order> orders;

    // ProductReview는 이제 OrderDetail을 통해 관리되므로 직접 관계 제거
    // 필요시 Repository 쿼리로 사용자의 리뷰 조회 가능

    // Enum 정의
    public enum Gender {
        MALE, FEMALE
    }

    public enum UserStatus {
        ACTIVE, INACTIVE, DORMANT, WITHDRAWN
    }

    public String getStatus() {
        return this.userStatus.toString();
    }
}