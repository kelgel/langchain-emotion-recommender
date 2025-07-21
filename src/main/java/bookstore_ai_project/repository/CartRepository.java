package bookstore_ai_project.repository;

import bookstore_ai_project.entity.Cart;
import bookstore_ai_project.entity.CartId;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CartRepository extends JpaRepository<Cart, CartId> {
    // - 장바구니에 해당 상품이 이미 담겨있는지 확인
    boolean existsByIdForAdminAndIsbn(String idForAdmin, String isbn);
    // - 장바구니에서 특정 상품 삭제
    void deleteByIdForAdminAndIsbn(String idForAdmin, String isbn);
    // - 사용자별 장바구니 전체 조회
    java.util.List<Cart> findAllByIdForAdmin(String idForAdmin);
}
