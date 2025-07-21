package bookstore_ai_project.repository;

import bookstore_ai_project.entity.TopCategory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TopCategoryRepository extends JpaRepository<TopCategory, Integer> {

    // 모든 대분류 조회 (ID 순으로 정렬)
    List<TopCategory> findAllByOrderByTopCategory();
}