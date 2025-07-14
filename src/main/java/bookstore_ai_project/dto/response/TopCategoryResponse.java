package bookstore_ai_project.dto.response;

import bookstore_ai_project.entity.TopCategory;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TopCategoryResponse {
    private Integer topCategory;
    private String topCategoryName;

    /**
     * Entity -> DTO 변환 메서드
     */
    public static TopCategoryResponse from(TopCategory entity) {
        return new TopCategoryResponse(
                entity.getTopCategory(),
                entity.getTopCategoryName()
        );
    }
}