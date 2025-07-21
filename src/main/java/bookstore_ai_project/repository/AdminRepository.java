package bookstore_ai_project.repository;

import bookstore_ai_project.entity.Admin;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AdminRepository extends JpaRepository<Admin, String> {
    /*
      활성 관리자 ID로 관리자 조회
      비즈니스 로직: 로그인 등 관리자 인증에 사용
    */
    @Query("SELECT a FROM Admin a WHERE a.adminId = :adminId AND a.adminStatus = 'ACTIVE'")
    Optional<Admin> findActiveAdminByAdminId(@Param("adminId") String adminId);
}
