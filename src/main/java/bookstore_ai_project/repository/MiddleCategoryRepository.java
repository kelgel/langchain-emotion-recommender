package bookstore_ai_project.repository;

import bookstore_ai_project.entity.MiddleCategory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MiddleCategoryRepository extends JpaRepository<MiddleCategory, Integer> {

    // 특정 대분류에 속한 중분류들 조회
    List<MiddleCategory> findByTopCategoryOrderByMidCategory(Integer topCategory);
}