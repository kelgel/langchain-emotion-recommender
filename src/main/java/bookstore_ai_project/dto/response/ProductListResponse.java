package bookstore_ai_project.dto.response;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ProductListResponse {
    private String isbn;
    private String productName;
    private String author;
    private String publisher;
    private Integer price;
    private BigDecimal rate;
    private String img;
    private LocalDateTime regDate;
    private Long salesCount; // 판매량 (판매량순 정렬용)
    private String salesStatus; // 판매상태
    private Integer currentStock; // 현재 재고량
} 