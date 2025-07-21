package bookstore_ai_project.controller;

import bookstore_ai_project.dto.response.CategoryTreeResponse;
import bookstore_ai_project.service.CategoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ModelAttribute;

@ControllerAdvice
public class CategoryGlobalAdvice {
    /** 카테고리 관리 비즈니스 로직 서비스 */
    @Autowired(required = false)
    private CategoryService categoryService;

    /**
     * 모든 뷰에 카테고리 트리 데이터를 전역으로 추가
     *
     * 비즈니스 로직: 헤더 등에서 카테고리 트리 구조를 공통으로 사용하도록 Model에 주입
     *
     * @param model 뷰 데이터 전달 모델
     */
    @ModelAttribute
    public void addGlobalCategoryAttributes(Model model) {
        if (categoryService != null) {
            try {
                CategoryTreeResponse categoryTree = categoryService.getCategoryTreeForHeader();
                model.addAttribute("topCategories", categoryTree.getTopCategories());
                model.addAttribute("middleCategoriesMap", categoryTree.getMiddleCategoriesMap());
                model.addAttribute("lowCategoriesMap", categoryTree.getLowCategoriesMap());
            } catch (Exception e) {
                System.err.println("카테고리 데이터 로드 실패: " + e.getMessage());
                e.printStackTrace();
                setEmptyCategories(model);
            }
        } else {
            setEmptyCategories(model);
        }
    }

    /**
     * 카테고리 데이터가 없을 때 빈 값으로 세팅
     *
     * 비즈니스 로직: 카테고리 서비스 실패 시 빈 카테고리 트리 반환
     *
     * @param model 뷰 데이터 전달 모델
     */
    private void setEmptyCategories(Model model) {
        CategoryTreeResponse emptyTree = CategoryTreeResponse.empty();
        model.addAttribute("topCategories", emptyTree.getTopCategories());
        model.addAttribute("middleCategoriesMap", emptyTree.getMiddleCategoriesMap());
        model.addAttribute("lowCategoriesMap", emptyTree.getLowCategoriesMap());
    }
} 