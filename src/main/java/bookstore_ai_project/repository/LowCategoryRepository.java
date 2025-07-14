package bookstore_ai_project.repository;

import bookstore_ai_project.entity.LowCategory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface LowCategoryRepository extends JpaRepository<LowCategory, Integer> {

    // 특정 중분류에 속한 소분류들 조회
    List<LowCategory> findByMidCategoryOrderByLowCategory(Integer midCategory);
}