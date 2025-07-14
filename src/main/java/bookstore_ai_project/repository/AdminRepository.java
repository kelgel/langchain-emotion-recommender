package bookstore_ai_project.repository;

import bookstore_ai_project.entity.Admin;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AdminRepository extends JpaRepository<Admin, String> {
    
    @Query("SELECT a FROM Admin a WHERE a.adminId = :adminId AND a.adminStatus = 'ACTIVE'")
    Optional<Admin> findActiveAdminByAdminId(@Param("adminId") String adminId);
}
