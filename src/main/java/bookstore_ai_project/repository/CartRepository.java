package bookstore_ai_project.repository;

import bookstore_ai_project.entity.Cart;
import bookstore_ai_project.entity.CartId;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CartRepository extends JpaRepository<Cart, CartId> {
    boolean existsByIdForAdminAndIsbn(String idForAdmin, String isbn);
    void deleteByIdForAdminAndIsbn(String idForAdmin, String isbn);
    java.util.List<Cart> findAllByIdForAdmin(String idForAdmin);
}
