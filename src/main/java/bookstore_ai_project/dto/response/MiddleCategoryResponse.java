package bookstore_ai_project.dto.response;

import bookstore_ai_project.entity.MiddleCategory;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class MiddleCategoryResponse {
    private Integer midCategory;
    private Integer topCategory;
    private String midCategoryName;

    /**
     * Entity -> DTO 변환 메서드
     */
    public static MiddleCategoryResponse from(MiddleCategory entity) {
        return new MiddleCategoryResponse(
                entity.getMidCategory(),
                entity.getTopCategory(),
                entity.getMidCategoryName()
        );
    }
}