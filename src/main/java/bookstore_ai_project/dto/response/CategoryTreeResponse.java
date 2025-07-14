package bookstore_ai_project.dto.response;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.util.List;
import java.util.Map;

/**
 * 헤더에서 사용할 카테고리 트리 전체 응답 DTO
 * 대분류, 중분류Map, 소분류Map을 모두 포함
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class CategoryTreeResponse {

    // 모든 대분류 목록
    private List<TopCategoryResponse> topCategories;

    // 대분류ID를 키로 하는 중분류 목록 Map
    private Map<Integer, List<MiddleCategoryResponse>> middleCategoriesMap;

    // 중분류ID를 키로 하는 소분류 목록 Map
    private Map<Integer, List<LowCategoryResponse>> lowCategoriesMap;

    /**
     * 빈 카테고리 트리 생성
     */
    public static CategoryTreeResponse empty() {
        return new CategoryTreeResponse(
                List.of(),
                Map.of(),
                Map.of()
        );
    }
}