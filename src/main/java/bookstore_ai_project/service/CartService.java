package bookstore_ai_project.service;

import bookstore_ai_project.entity.Cart;
import bookstore_ai_project.entity.CartId;
import bookstore_ai_project.repository.CartRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;
import bookstore_ai_project.dto.response.CartItemResponse;
import java.util.ArrayList;
import java.util.List;

@Service
public class CartService {
    @Autowired
    private CartRepository cartRepository;

    @Transactional
    public void addToCart(String idForAdmin, String isbn, int quantity) {
        // 이미 담긴 상품인지 체크
        if (cartRepository.existsByIdForAdminAndIsbn(idForAdmin, isbn)) {
            throw new IllegalStateException("ALREADY");
        }
        Cart cart = new Cart();
        cart.setIdForAdmin(idForAdmin);
        cart.setIsbn(isbn);
        cart.setProductQuantity(quantity);
        cart.setCartRegDate(LocalDateTime.now());
        cartRepository.save(cart);
    }

    @Transactional
    public void deleteCartItem(String idForAdmin, String isbn) {
        cartRepository.deleteByIdForAdminAndIsbn(idForAdmin, isbn);
    }

    @Transactional
    public void updateCartItem(String idForAdmin, String isbn, int quantity) {
        Cart cart = cartRepository.findById(new CartId(idForAdmin, isbn)).orElseThrow();
        cart.setProductQuantity(quantity);
        cartRepository.save(cart);
    }

    public java.util.List<Cart> getCartList(String idForAdmin) {
        return cartRepository.findAllByIdForAdmin(idForAdmin);
    }

    public List<CartItemResponse> getCartListDto(String idForAdmin) {
        List<Cart> carts = cartRepository.findAllByIdForAdmin(idForAdmin);
        List<CartItemResponse> result = new ArrayList<>();
        for (Cart cart : carts) {
            CartItemResponse dto = new CartItemResponse();
            dto.setIsbn(cart.getIsbn());
            if (cart.getProduct() != null) {
                dto.setProductName(cart.getProduct().getProductName());
                dto.setAuthor(cart.getProduct().getAuthor());
                dto.setPrice(cart.getProduct().getPrice());
                dto.setImg(cart.getProduct().getImg());
                dto.setSalesStatus(cart.getProduct().getSalesStatus() != null ? cart.getProduct().getSalesStatus().name() : null);
            }
            dto.setProductQuantity(cart.getProductQuantity());
            result.add(dto);
        }
        return result;
    }

    // 장바구니 중복 체크 메서드
    public boolean isInCart(String idForAdmin, String isbn) {
        return cartRepository.existsByIdForAdminAndIsbn(idForAdmin, isbn);
    }
}
