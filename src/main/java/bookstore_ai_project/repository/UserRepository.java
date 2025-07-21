package bookstore_ai_project.repository;

import bookstore_ai_project.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, String>, org.springframework.data.jpa.repository.JpaSpecificationExecutor<User> {

    // - 로그인용 사용자 조회 (idForUser로 검색)
    Optional<User> findByIdForUser(String idForUser);

    // - 추가: idForAdmin으로 사용자 조회 (주문 정보 조회용)
    Optional<User> findByIdForAdmin(String idForAdmin);

    // - 이메일과 이름으로 아이디 찾기
    Optional<User> findByUserEmailAndUserName(String userEmail, String userName);

    // - 아이디와 이름으로 사용자 찾기 (비밀번호 찾기용)
    Optional<User> findByIdForUserAndUserName(String idForUser, String userName);

    /*
      마지막 로그인 시간 업데이트
      비즈니스 로직: 로그인 시각 기록
    */
    @Modifying
    @Query("UPDATE User u SET u.lastLoginDate = :loginDate WHERE u.idForAdmin = :idForAdmin")
    int updateLastLoginDate(@Param("idForAdmin") String idForAdmin, @Param("loginDate") LocalDateTime loginDate);

    /*
      휴면 상태로 변경 (6개월 이상 미로그인 사용자)
      비즈니스 로직: 휴면 계정 자동 전환
    */
    @Modifying
    @Query("UPDATE User u SET u.userStatus = 'DORMANT', u.updateDate = :updateDate " +
            "WHERE u.userStatus = 'ACTIVE' AND u.lastLoginDate < :cutoffDate")
    int updateUserStatusToDormant(@Param("cutoffDate") LocalDateTime cutoffDate,
                                  @Param("updateDate") LocalDateTime updateDate);

    /*
      휴면 상태 체크 대상 사용자 조회 (6개월 이상 미로그인 활성 사용자)
      비즈니스 로직: 휴면 전환 대상 선별
    */
    @Query("SELECT u FROM User u WHERE u.userStatus = 'ACTIVE' AND u.lastLoginDate < :cutoffDate")
    List<User> findActiveUsersForDormantCheck(@Param("cutoffDate") LocalDateTime cutoffDate);

    /*
      휴면 해제 (비밀번호 찾기 시)
      비즈니스 로직: 휴면 → 활성 전환
    */
    @Modifying
    @Query("UPDATE User u SET u.userStatus = 'ACTIVE', u.updateDate = :updateDate " +
            "WHERE u.idForAdmin = :idForAdmin AND u.userStatus = 'DORMANT'")
    int activateFromDormant(@Param("idForAdmin") String idForAdmin,
                            @Param("updateDate") LocalDateTime updateDate);

    // - 사용자 상태 확인
    @Query("SELECT u.userStatus FROM User u WHERE u.idForUser = :idForUser")
    Optional<User.UserStatus> findUserStatusByIdForUser(@Param("idForUser") String idForUser);

    // - 이름과 생년월일로 회원을 찾는 메서드
    Optional<User> findByUserNameAndUserBirth(String userName, LocalDate userBirth);

    // - 닉네임 중복 체크
    boolean existsByUserNickname(String userNickname);
    // - 아이디 중복 체크
    boolean existsByIdForUser(String idForUser);
    // - 이메일 중복 체크
    boolean existsByUserEmail(String userEmail);

    /*
      최대 idForAdmin 값 조회 (U로 시작하는 ID 중에서)
      비즈니스 로직: 신규 관리자 ID 생성 시 사용
    */
    @Query("SELECT MAX(u.idForAdmin) FROM User u WHERE u.idForAdmin LIKE 'U%'")
    Optional<String> findMaxIdForAdmin();
    
    // - 관리자용 사용자 검색 - idForAdmin으로 정확 일치 검색
    @Query("SELECT u FROM User u WHERE u.idForAdmin = :searchTerm")
    List<User> findByIdForAdminExact(@Param("searchTerm") String searchTerm);
    
    // - 관리자용 사용자 검색 - idForUser로 정확 일치 검색
    @Query("SELECT u FROM User u WHERE u.idForUser = :searchTerm")
    List<User> findByIdForUserExact(@Param("searchTerm") String searchTerm);
    
    // - 회원조회용 메서드들 (페이징)
    org.springframework.data.domain.Page<User> findByUserNameContainingIgnoreCase(String userName, org.springframework.data.domain.Pageable pageable);
    
    // - 포함이 아닌 정확히 일치하는 회원ID 검색
    org.springframework.data.domain.Page<User> findByIdForAdmin(String idForAdmin, org.springframework.data.domain.Pageable pageable);
    org.springframework.data.domain.Page<User> findByIdForUser(String idForUser, org.springframework.data.domain.Pageable pageable);
    org.springframework.data.domain.Page<User> findByIdForAdminOrIdForUser(String idForAdmin, String idForUser, org.springframework.data.domain.Pageable pageable);
    
    org.springframework.data.domain.Page<User> findByIdForAdminContainingIgnoreCase(String idForAdmin, org.springframework.data.domain.Pageable pageable);
    org.springframework.data.domain.Page<User> findByIdForUserContainingIgnoreCase(String idForUser, org.springframework.data.domain.Pageable pageable);
    org.springframework.data.domain.Page<User> findByIdForAdminContainingIgnoreCaseOrIdForUserContainingIgnoreCase(
        String idForAdmin, String idForUser, org.springframework.data.domain.Pageable pageable);
}