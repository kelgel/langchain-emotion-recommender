package bookstore_ai_project.controller;

import bookstore_ai_project.dto.response.CategoryTreeResponse;
import bookstore_ai_project.service.CategoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ModelAttribute;

@ControllerAdvice
public class CategoryGlobalAdvice {
    @Autowired(required = false)
    private CategoryService categoryService;

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

    private void setEmptyCategories(Model model) {
        CategoryTreeResponse emptyTree = CategoryTreeResponse.empty();
        model.addAttribute("topCategories", emptyTree.getTopCategories());
        model.addAttribute("middleCategoriesMap", emptyTree.getMiddleCategoriesMap());
        model.addAttribute("lowCategoriesMap", emptyTree.getLowCategoriesMap());
    }
} 