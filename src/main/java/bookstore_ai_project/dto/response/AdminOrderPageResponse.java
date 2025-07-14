package bookstore_ai_project.dto.response;

import lombok.Data;
import java.util.List;

@Data
public class AdminOrderPageResponse {
    private List<AdminOrderHistoryResponse> orders;
    private int totalPages;
    private int currentPage;
    private long totalElements;
    private int pageSize;
}