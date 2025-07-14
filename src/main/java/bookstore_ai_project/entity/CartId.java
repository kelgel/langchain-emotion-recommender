package bookstore_ai_project.entity;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.io.Serializable;

@Data                      // getter, setter, equals, hashCode 자동 생성
@NoArgsConstructor         // 기본 생성자
@AllArgsConstructor        // 모든 필드 생성자
public class CartId implements Serializable {  // 복합키는 Serializable 구현 필요

    private String idForAdmin;
    private String isbn;
}