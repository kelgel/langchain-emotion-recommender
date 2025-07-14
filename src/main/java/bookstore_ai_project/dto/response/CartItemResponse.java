package bookstore_ai_project.dto.response;

import lombok.Data;

@Data
public class CartItemResponse {
    private String isbn;
    private String productName;
    private String author;
    private Integer price;
    private Integer productQuantity;
    private String img;
    private String salesStatus;
} 