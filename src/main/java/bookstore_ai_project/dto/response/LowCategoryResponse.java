package bookstore_ai_project.dto.response;

import bookstore_ai_project.entity.LowCategory;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class LowCategoryResponse {
    private Integer lowCategory;
    private Integer midCategory;
    private String lowCategoryName;

    /**
     * Entity -> DTO 변환 메서드
     */
    public static LowCategoryResponse from(LowCategory entity) {
        return new LowCategoryResponse(
                entity.getLowCategory(),
                entity.getMidCategory(),
                entity.getLowCategoryName()
        );
    }
}