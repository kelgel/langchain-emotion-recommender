package bookstore_ai_project.controller;

import bookstore_ai_project.dto.response.LoginResponse;
import bookstore_ai_project.repository.StockRepository;
import bookstore_ai_project.entity.User;
import bookstore_ai_project.service.CartService;
import bookstore_ai_project.dto.response.LoginResponse.UserInfo;
import bookstore_ai_project.dto.response.CartItemResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.HttpSession;
import java.util.Map;
import java.util.HashMap;
import java.util.stream.Collectors;
import org.springframework.http.ResponseEntity;

@Controller
@RequestMapping("/cart")
public class CartController {
    /** 장바구니 비즈니스 로직 서비스 */
    @Autowired
    private CartService cartService;

    /** 재고 데이터 접근 리포지토리 */
    @Autowired
    private StockRepository stockRepository;

    /**
     * 장바구니 페이지 진입
     *
     * 비즈니스 로직: 로그인한 사용자의 장바구니 정보를 조회하여 화면에 표시
     *
     * @param model 뷰 데이터 전달 모델
     * @param session HTTP 세션 (로그인 상태 확인용)
     * @return 장바구니 뷰 이름 또는 로그인 페이지 리다이렉트
     */
    @GetMapping("")
    public String cart(org.springframework.ui.Model model, jakarta.servlet.http.HttpSession session) {
        // 🔒 로그인 검증: 비로그인 시 로그인 페이지로 리다이렉트
        Object userObj = session.getAttribute("user");
        if (userObj == null || !(userObj instanceof LoginResponse.UserInfo)) {
            return "redirect:/login?redirectUrl=/cart";
        }
        
        // 🔒 관리자 접근 차단
        Boolean isAdmin = (Boolean) session.getAttribute("isAdmin");
        if (isAdmin != null && isAdmin) {
            model.addAttribute("error", "일반 사용자 전용 화면입니다.");
            return "redirect:/admin";
        }
        
        // 임시로 빈 장바구니 상태로 표시
        // 실제 구현에서는 로그인한 사용자의 장바구니 정보를 조회
        model.addAttribute("cartItems", java.util.List.of());
        model.addAttribute("isEmpty", true);
        
        return "user/cart";
    }

    /**
     * 장바구니 단일 추가 API
     *
     * 비즈니스 로직: 로그인한 사용자의 장바구니에 상품을 1개 추가
     *
     * @param isbn 상품 ISBN
     * @param quantity 수량
     * @param session HTTP 세션
     * @return 처리 결과(OK, ALREADY, NOT_LOGGED_IN 등)
     */
    @PostMapping("/add")
    @ResponseBody
    public String addToCart(@RequestParam String isbn, @RequestParam int quantity, HttpSession session) {
        Object userObj = session.getAttribute("user");
        if (userObj == null) {
            return "NOT_LOGGED_IN";
        }
        String idForAdmin;
        if (userObj instanceof User) {
            idForAdmin = ((User) userObj).getIdForAdmin();
        } else if (userObj instanceof UserInfo) {
            idForAdmin = ((UserInfo) userObj).getIdForAdmin();
        } else {
            return "ERROR: Unknown user type in session";
        }
        try {
            cartService.addToCart(idForAdmin, isbn, quantity);
            return "OK";
        } catch (IllegalStateException e) {
            if ("ALREADY".equals(e.getMessage())) {
                return "ALREADY";
            }
            return "ERROR: " + e.getMessage();
        } catch (Exception e) {
            return "ERROR: " + e.getMessage();
        }
    }

    /**
     * 여러 상품 일괄 추가 API
     *
     * 비즈니스 로직: 여러 ISBN 상품을 한 번에 장바구니에 추가
     *
     * @param body isbns(리스트), quantity(수량)
     * @param session HTTP 세션
     * @return 추가된 ISBN 리스트 및 상태
     */
    @PostMapping("/add-bulk")
    @ResponseBody
    public Map<String, Object> addToCartBulk(@RequestBody Map<String, Object> body, HttpSession session) {
        Object userObj = session.getAttribute("user");
        Map<String, Object> result = new HashMap<>();
        if (userObj == null) {
            result.put("status", "NOT_LOGGED_IN");
            return result;
        }
        String idForAdmin = userObj instanceof User ? ((User) userObj).getIdForAdmin() :
                userObj instanceof UserInfo ? ((UserInfo) userObj).getIdForAdmin() : null;
        if (idForAdmin == null) {
            result.put("status", "ERROR");
            return result;
        }
        java.util.List<String> isbns = (java.util.List<String>) body.get("isbns");
        int quantity = body.get("quantity") != null ? (int) body.get("quantity") : 1;
        java.util.List<String> added = new java.util.ArrayList<>();
        for (String isbn : isbns) {
            try {
                cartService.addToCart(idForAdmin, isbn, quantity);
                added.add(isbn);
            } catch (IllegalStateException e) {
                // 이미 담긴 상품은 무시
            }
        }
        result.put("added", added);
        result.put("status", "OK");
        return result;
    }

    /**
     * 여러 상품 중복 체크 API
     *
     * 비즈니스 로직: 여러 ISBN 중 이미 장바구니에 담긴 상품만 반환
     *
     * @param body isbns(리스트)
     * @param session HTTP 세션
     * @return 이미 담긴 ISBN 리스트
     */
    @PostMapping("/check")
    @ResponseBody
    public Map<String, Object> checkCart(@RequestBody Map<String, Object> body, HttpSession session) {
        Object userObj = session.getAttribute("user");
        Map<String, Object> result = new HashMap<>();
        if (userObj == null) {
            result.put("alreadyInCart", new java.util.ArrayList<>());
            return result;
        }
        String idForAdmin = userObj instanceof User ? ((User) userObj).getIdForAdmin() :
                userObj instanceof UserInfo ? ((UserInfo) userObj).getIdForAdmin() : null;
        if (idForAdmin == null) {
            result.put("alreadyInCart", new java.util.ArrayList<>());
            return result;
        }
        java.util.List<String> isbns = (java.util.List<String>) body.get("isbns");
        java.util.List<String> already = isbns.stream()
            .filter(isbn -> cartService.isInCart(idForAdmin, isbn))
            .collect(Collectors.toList());
        result.put("alreadyInCart", already);
        return result;
    }

    /**
     * 장바구니 상품 삭제 API
     *
     * 비즈니스 로직: 장바구니에서 특정 상품을 삭제
     *
     * @param isbn 상품 ISBN
     * @param session HTTP 세션
     * @return 처리 결과(OK, NOT_LOGGED_IN 등)
     */
    @PostMapping("/delete")
    @ResponseBody
    public String deleteCartItem(@RequestParam String isbn, HttpSession session) {
        Object userObj = session.getAttribute("user");
        if (userObj == null) {
            return "NOT_LOGGED_IN";
        }
        String idForAdmin;
        if (userObj instanceof User) {
            idForAdmin = ((User) userObj).getIdForAdmin();
        } else if (userObj instanceof UserInfo) {
            idForAdmin = ((UserInfo) userObj).getIdForAdmin();
        } else {
            return "ERROR: Unknown user type in session";
        }
        try {
            cartService.deleteCartItem(idForAdmin, isbn);
            return "OK";
        } catch (Exception e) {
            return "ERROR: " + e.getMessage();
        }
    }

    /**
     * 장바구니 상품 수량 변경 API
     *
     * 비즈니스 로직: 장바구니에 담긴 상품의 수량을 변경
     *
     * @param isbn 상품 ISBN
     * @param quantity 변경할 수량
     * @param session HTTP 세션
     * @return 처리 결과(OK, NOT_LOGGED_IN, ERROR 등)
     */
    @PostMapping("/update")
    @ResponseBody
    public String updateCartItem(@RequestParam String isbn, @RequestParam int quantity, HttpSession session) {
        Object userObj = session.getAttribute("user");
        if (userObj == null) {
            return "NOT_LOGGED_IN";
        }
        String idForAdmin;
        if (userObj instanceof User) {
            idForAdmin = ((User) userObj).getIdForAdmin();
        } else if (userObj instanceof UserInfo) {
            idForAdmin = ((UserInfo) userObj).getIdForAdmin();
        } else {
            return "ERROR: Unknown user type in session";
        }
        // 최신 재고 체크
        Integer stock = stockRepository.findCurrentStockByIsbnNative(isbn);
        if (stock == null) stock = 0;
        if (quantity > stock) {
            return "ERROR: 재고가 부족합니다. 최대 수량: " + stock;
        }
        try {
            cartService.updateCartItem(idForAdmin, isbn, quantity);
            return "OK";
        } catch (Exception e) {
            return "ERROR: " + e.getMessage();
        }
    }

    /**
     * 장바구니 목록 조회 API
     *
     * 비즈니스 로직: 로그인한 사용자의 장바구니 목록을 반환
     *
     * @param session HTTP 세션
     * @return 장바구니 아이템 리스트
     */
    @GetMapping("/list")
    @ResponseBody
    public java.util.List<CartItemResponse> getCartList(HttpSession session) {
        Object userObj = session.getAttribute("user");
        if (userObj == null) {
            return java.util.Collections.emptyList();
        }
        String idForAdmin;
        if (userObj instanceof User) {
            idForAdmin = ((User) userObj).getIdForAdmin();
        } else if (userObj instanceof UserInfo) {
            idForAdmin = ((UserInfo) userObj).getIdForAdmin();
        } else {
            return java.util.Collections.emptyList();
        }
        return cartService.getCartListDto(idForAdmin);
    }

    /**
     * 특정 ISBN의 최신 재고 조회 API
     *
     * 비즈니스 로직: 상품의 최신 재고 수량을 반환
     *
     * @param isbn 상품 ISBN
     * @return 재고 수량
     */
    @GetMapping("/api/stock/{isbn}")
    @ResponseBody
    public ResponseEntity<?> getLatestStock(@PathVariable String isbn) {
        Integer stock = stockRepository.findCurrentStockByIsbnNative(isbn);
        if (stock == null) stock = 0;
        return ResponseEntity.ok(java.util.Map.of("stock", stock));
    }
}
