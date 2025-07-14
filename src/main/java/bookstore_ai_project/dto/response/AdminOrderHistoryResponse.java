package bookstore_ai_project.dto.response;

import lombok.Data;
import java.time.LocalDateTime;
import java.util.List;

@Data
public class AdminOrderHistoryResponse {
    private String orderId;
    private LocalDateTime orderDate;
    private String orderStatus;
    private String userIdForAdmin; // 주문자 관리자용 ID
    private String userIdForUser;  // 주문자 사용자용 ID
    private Integer totalProductCategory;
    private Integer totalProductQuantity;
    private Integer totalPaidPrice;
    private List<OrderDetailResponse> orderDetails;
    
    @Data
    public static class OrderDetailResponse {
        private String isbn;
        private String productTitle;
        private String author;
        private String img;
        private Integer orderItemQuantity;
        private Integer eachProductPrice;
        private Integer totalProductPrice;
    }
}