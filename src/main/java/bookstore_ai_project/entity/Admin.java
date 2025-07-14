package bookstore_ai_project.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity                    // JPA 엔티티임을 표시
@Table(name = "admin")     // DB 테이블명 지정
@Data                      // getter, setter, toString 자동 생성
@NoArgsConstructor         // 기본 생성자
@AllArgsConstructor        // 모든 필드 생성자
public class Admin {

    @Id                                // 기본키 지정
    @Column(name = "admin_id")         // DB 컬럼명과 길이 지정
    private String adminId;

    @Column(name = "admin_pwd")
    private String adminPwd;

    @Column(name = "admin_name")
    private String adminName;

    @Enumerated(EnumType.STRING)       // Enum을 문자열로 저장
    @Column(name = "admin_status")
    private AdminStatus adminStatus;

    @Column(name = "admin_phone_number")
    private String adminPhoneNumber;

    // Enum 정의
    public enum AdminStatus {
        ACTIVE, INACTIVE
    }
}