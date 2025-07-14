package bookstore_ai_project.entity;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.io.Serializable;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class OrderId implements Serializable {
    
    private String orderId;
    private String idForAdmin;
} 