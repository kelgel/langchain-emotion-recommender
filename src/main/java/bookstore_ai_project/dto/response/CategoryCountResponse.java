package bookstore_ai_project.dto.response;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CategoryCountResponse {
    private Integer topCategory;
    private String topCategoryName;
    private Integer midCategory;
    private String midCategoryName;
    private Integer lowCategory;
    private String lowCategoryName;
    private Long bookCount;
} 