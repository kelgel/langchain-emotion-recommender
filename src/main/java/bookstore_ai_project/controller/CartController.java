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
    @Autowired
    private CartService cartService;

    @Autowired
    private StockRepository stockRepository;

    // 장바구니 페이지
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

    // 장바구니 단일 추가 API
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

    // 여러 상품 일괄 추가 API (add-bulk)
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

    // 여러 상품 중복 체크 API
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

    @GetMapping("/api/stock/{isbn}")
    @ResponseBody
    public ResponseEntity<?> getLatestStock(@PathVariable String isbn) {
        Integer stock = stockRepository.findCurrentStockByIsbnNative(isbn);
        if (stock == null) stock = 0;
        return ResponseEntity.ok(java.util.Map.of("stock", stock));
    }
}
