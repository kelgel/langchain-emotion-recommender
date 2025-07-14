package bookstore_ai_project.dto.response;

import lombok.Data;
import java.time.LocalDateTime;
import java.util.List;

@Data
public class OrderHistoryResponse {
    private String orderId;
    private LocalDateTime orderDate;
    private String orderStatus;
    private Integer totalProductCategory;
    private Integer totalProductQuantity;
    private Integer totalPaidPrice;
    private List<OrderDetailResponse> orderDetails;
    
    @Data
    public static class OrderDetailResponse {
        private String isbn;
        private String productTitle;
        private String author;
        private String img; // 상품 이미지 경로
        private Integer orderItemQuantity;
        private Integer eachProductPrice;
        private Integer totalProductPrice; // 추가
        private boolean hasReview;
        private Integer reviewId;
        private String reviewTitle;
        private String reviewContent;
        private java.time.LocalDateTime deleteDate;
    }
} 