package bookstore_ai_project.service;

import bookstore_ai_project.dto.response.TopCategoryResponse;
import bookstore_ai_project.dto.response.MiddleCategoryResponse;
import bookstore_ai_project.dto.response.LowCategoryResponse;
import bookstore_ai_project.dto.response.CategoryTreeResponse;
import bookstore_ai_project.dto.response.CategoryCountResponse;
import bookstore_ai_project.entity.TopCategory;
import bookstore_ai_project.entity.MiddleCategory;
import bookstore_ai_project.entity.LowCategory;
import bookstore_ai_project.repository.TopCategoryRepository;
import bookstore_ai_project.repository.MiddleCategoryRepository;
import bookstore_ai_project.repository.LowCategoryRepository;
import bookstore_ai_project.repository.ProductRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 카테고리 관리 비즈니스 로직 서비스
 *
 * 비즈니스 로직: 대/중/소분류 카테고리 조회, 카테고리 트리 구성, 카테고리별 도서 개수 집계 등
 */
@Service
public class CategoryService {

    /** 대분류 데이터 접근 리포지토리 */
    @Autowired
    private TopCategoryRepository topCategoryRepository;

    /** 중분류 데이터 접근 리포지토리 */
    @Autowired
    private MiddleCategoryRepository middleCategoryRepository;

    /** 소분류 데이터 접근 리포지토리 */
    @Autowired
    private LowCategoryRepository lowCategoryRepository;

    /** 상품 데이터 접근 리포지토리 */
    @Autowired
    private ProductRepository productRepository;

    /**
     * 전체 대분류 리스트 조회
     *
     * 비즈니스 로직: 모든 대분류 카테고리를 순서대로 조회하여 DTO로 변환 후 반환
     *
     * @return 대분류 리스트 (TopCategoryResponse)
     */
    public List<TopCategoryResponse> getAllTopCategories() {
        List<TopCategory> entities = topCategoryRepository.findAllByOrderByTopCategory();
        return entities.stream()
                .map(TopCategoryResponse::from)
                .collect(Collectors.toList());
    }

    /**
     * 특정 대분류에 속한 중분류 리스트 조회
     *
     * 비즈니스 로직: 지정된 대분류 ID에 해당하는 모든 중분류들을 조회하여 DTO로 변환 후 반환
     *
     * @param topCategoryId 대분류 카테고리 ID
     * @return 중분류 리스트 (MiddleCategoryResponse)
     */
    public List<MiddleCategoryResponse> getMiddleCategoriesByTopCategory(Integer topCategory) {
        List<MiddleCategory> entities = middleCategoryRepository.findByTopCategoryOrderByMidCategory(topCategory);
        return entities.stream()
                .map(MiddleCategoryResponse::from)
                .collect(Collectors.toList());
    }

    /**
     * 특정 중분류에 속한 소분류 리스트 조회
     *
     * 비즈니스 로직: 지정된 중분류 ID에 해당하는 모든 소분류들을 조회하여 DTO로 변환 후 반환
     *
     * @param midCategory 중분류 카테고리 ID
     * @return 소분류 리스트 (LowCategoryResponse)
     */
    public List<LowCategoryResponse> getLowCategoriesByMiddleCategory(Integer midCategory) {
        List<LowCategory> entities = lowCategoryRepository.findByMidCategoryOrderByLowCategory(midCategory);
        return entities.stream()
                .map(LowCategoryResponse::from)
                .collect(Collectors.toList());
    }

    /**
     * 헤더에서 사용할 전체 카테고리 트리 구조 조회
     *
     * 비즈니스 로직: 한 번의 호출로 모든 카테고리(대/중/소분류) 데이터를 트리 구조로 구성하여 DTO 반환
     *
     * @return 전체 카테고리 트리 구조 (CategoryTreeResponse)
     */
    public CategoryTreeResponse getCategoryTreeForHeader() {
        try {
            // 1. 모든 대분류 조회
            List<TopCategoryResponse> topCategories = getAllTopCategories();

            if (topCategories.isEmpty()) {
                return CategoryTreeResponse.empty();
            }

            // 2. 각 대분류별로 중분류 조회하여 Map에 저장
            Map<Integer, List<MiddleCategoryResponse>> middleCategoriesMap = new LinkedHashMap<>();

            // 3. 각 중분류별로 소분류 조회하여 Map에 저장
            Map<Integer, List<LowCategoryResponse>> lowCategoriesMap = new LinkedHashMap<>();

            for (TopCategoryResponse topCategory : topCategories) {
                // 특정 대분류에 속한 중분류들 조회
                List<MiddleCategoryResponse> midCategories = getMiddleCategoriesByTopCategory(topCategory.getTopCategory());
                middleCategoriesMap.put(topCategory.getTopCategory(), midCategories);

                for (MiddleCategoryResponse midCategory : midCategories) {
                    // 특정 중분류에 속한 소분류들 조회
                    List<LowCategoryResponse> lowCategories = getLowCategoriesByMiddleCategory(midCategory.getMidCategory());
                    lowCategoriesMap.put(midCategory.getMidCategory(), lowCategories);
                }
            }

            return new CategoryTreeResponse(topCategories, middleCategoriesMap, lowCategoriesMap);

        } catch (Exception e) {
            System.err.println("카테고리 트리 데이터 로드 실패: " + e.getMessage());
            e.printStackTrace();
            return CategoryTreeResponse.empty();
        }
    }

    /**
     * 대분류별 도서 개수 집계
     *
     * 비즈니스 로직: 각 대분류에 해당하는 도서의 총 개수를 집계하여 통계 데이터로 제공
     *
     * @return 대분류별 도서 개수 리스트 (CategoryCountResponse)
     */
    public List<CategoryCountResponse> countBooksByTopCategory() {
        List<Object[]> result = productRepository.countBooksByTopCategory();
        return result.stream().map(arr -> new CategoryCountResponse(
                (Integer) arr[0], // topCategory
                (String) arr[1],  // topCategoryName
                null,             // midCategory
                null,             // midCategoryName
                null,             // lowCategory
                null,             // lowCategoryName
                (Long) arr[2]     // bookCount
        )).toList();
    }

    /**
     * 중분류별 도서 개수 집계
     *
     * 비즈니스 로직: 각 중분류에 해당하는 도서의 총 개수를 집계하여 통계 데이터로 제공
     *
     * @return 중분류별 도서 개수 리스트 (CategoryCountResponse)
     */
    public List<CategoryCountResponse> countBooksByMiddleCategory() {
        List<Object[]> result = productRepository.countBooksByMiddleCategory();
        return result.stream().map(arr -> new CategoryCountResponse(
                (Integer) arr[2], // topCategory
                (String) arr[3],  // topCategoryName
                (Integer) arr[0], // midCategory
                (String) arr[1],  // midCategoryName
                null,             // lowCategory
                null,             // lowCategoryName
                (Long) arr[4]     // bookCount
        )).toList();
    }

    /**
     * 소분류별 도서 개수 집계
     *
     * 비즈니스 로직: 각 소분류에 해당하는 도서의 총 개수를 집계하여 통계 데이터로 제공
     *
     * @return 소분류별 도서 개수 리스트 (CategoryCountResponse)
     */
    public List<CategoryCountResponse> countBooksByLowCategory() {
        List<Object[]> result = productRepository.countBooksByLowCategory();
        return result.stream().map(arr -> new CategoryCountResponse(
                (Integer) arr[4], // topCategory
                (String) arr[5],  // topCategoryName
                (Integer) arr[2], // midCategory
                (String) arr[3],  // midCategoryName
                (Integer) arr[0], // lowCategory
                (String) arr[1],  // lowCategoryName
                (Long) arr[6]     // bookCount
        )).toList();
    }
}