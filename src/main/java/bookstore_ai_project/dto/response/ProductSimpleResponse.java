package bookstore_ai_project.dto.response;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ProductSimpleResponse {
    private String isbn;
    private String productName;
    private String img;
    private String author;
    private Integer searchCount;
    private LocalDateTime regDate;
    private Integer productQuantity;
    private Integer price;
} 