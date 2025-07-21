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

/**
 * 장바구니 관리 비즈니스 로직 서비스
 *
 * 비즈니스 로직: 장바구니 상품 추가/제거/수정, 장바구니 리스트 조회, 중복 상품 처리 등
 */
@Service
public class CartService {
    /** 장바구니 데이터 접근 리포지토리 */
    @Autowired
    private CartRepository cartRepository;

    /**
     * 장바구니에 상품 추가
     *
     * 비즈니스 로직: 사용자의 장바구니에 상품 추가 (중복 상품 처리 포함)
     *
     * @param idForAdmin 사용자 관리 ID
     * @param isbn 추가할 상품 ISBN
     * @param quantity 추가할 수량
     * @throws IllegalStateException 이미 장바구니에 담긴 상품인 경우
     */
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

    /**
     * 장바구니에서 상품 제거
     *
     * 비즈니스 로직: 사용자의 장바구니에서 지정된 상품을 완전 삭제
     *
     * @param idForAdmin 사용자 관리 ID
     * @param isbn 삭제할 상품 ISBN
     */
    @Transactional
    public void deleteCartItem(String idForAdmin, String isbn) {
        cartRepository.deleteByIdForAdminAndIsbn(idForAdmin, isbn);
    }

    /**
     * 장바구니 상품 수량 수정
     *
     * 비즈니스 로직: 사용자의 장바구니에 담긴 상품의 수량을 수정
     *
     * @param idForAdmin 사용자 관리 ID
     * @param isbn 수정할 상품 ISBN
     * @param quantity 새로운 수량
     */
    @Transactional
    public void updateCartItem(String idForAdmin, String isbn, int quantity) {
        Cart cart = cartRepository.findById(new CartId(idForAdmin, isbn)).orElseThrow();
        cart.setProductQuantity(quantity);
        cartRepository.save(cart);
    }

    /**
     * 사용자의 장바구니 목록 조회 (Entity 반환)
     *
     * 비즈니스 로직: 특정 사용자의 장바구니에 담긴 모든 상품을 Entity 형태로 조회
     *
     * @param idForAdmin 사용자 관리 ID
     * @return 장바구니 상품 리스트 (Cart Entity)
     */
    public java.util.List<Cart> getCartList(String idForAdmin) {
        return cartRepository.findAllByIdForAdmin(idForAdmin);
    }

    /**
     * 사용자의 장바구니 목록 조회 (DTO 반환)
     *
     * 비즈니스 로직: 특정 사용자의 장바구니에 담긴 모든 상품을 상세 정보와 함께 DTO 형태로 조회
     *
     * @param idForAdmin 사용자 관리 ID
     * @return 장바구니 상품 상세 리스트 (CartItemResponse DTO)
     */
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

    /**
     * 장바구니 상품 중복 체크
     *
     * 비즈니스 로직: 특정 사용자의 장바구니에 해당 상품이 이미 담겨있는지 확인
     *
     * @param idForAdmin 사용자 관리 ID
     * @param isbn 확인할 상품 ISBN
     * @return 이미 담긴 상품인 경우 true, 아닌 경우 false
     */
    public boolean isInCart(String idForAdmin, String isbn) {
        return cartRepository.existsByIdForAdminAndIsbn(idForAdmin, isbn);
    }
}
