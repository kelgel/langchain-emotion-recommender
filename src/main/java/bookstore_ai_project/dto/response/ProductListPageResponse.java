package bookstore_ai_project.dto.response;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ProductListPageResponse {
    private List<ProductListResponse> products;
    private int currentPage;
    private int totalPages;
    private long totalItems;
    private int pageSize;
    private String categoryName;
    private Integer categoryId;
} 