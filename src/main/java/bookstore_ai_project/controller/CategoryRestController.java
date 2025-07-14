package bookstore_ai_project.controller;

import bookstore_ai_project.dto.response.TopCategoryResponse;
import bookstore_ai_project.dto.response.MiddleCategoryResponse;
import bookstore_ai_project.dto.response.LowCategoryResponse;
import bookstore_ai_project.service.CategoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;

@RestController
public class CategoryRestController {
    @Autowired
    private CategoryService categoryService;

    // 대분류 전체 조회
    @GetMapping("/api/category/top")
    public List<TopCategoryResponse> getTopCategories() {
        return categoryService.getAllTopCategories();
    }

    // 중분류 조회 (대분류 선택 시)
    @GetMapping("/api/category/middle")
    public List<MiddleCategoryResponse> getMiddleCategories(@RequestParam Integer topCategory) {
        return categoryService.getMiddleCategoriesByTopCategory(topCategory);
    }

    // 소분류 조회 (중분류 선택 시)
    @GetMapping("/api/category/low")
    public List<LowCategoryResponse> getLowCategories(@RequestParam Integer midCategory) {
        return categoryService.getLowCategoriesByMiddleCategory(midCategory);
    }
} 