package bookstore_ai_project.controller;

import bookstore_ai_project.dto.response.LoginResponse;
import bookstore_ai_project.dto.response.ProductListPageResponse;
import bookstore_ai_project.dto.response.AdminOrderPageResponse;
import bookstore_ai_project.entity.Product;
import bookstore_ai_project.service.ProductService;
import bookstore_ai_project.service.CategoryService;
import bookstore_ai_project.service.OrderService;
import bookstore_ai_project.repository.OrderRepository;
import bookstore_ai_project.repository.UserRepository;
import bookstore_ai_project.entity.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.ui.Model;
import org.springframework.http.ResponseEntity;

import jakarta.servlet.http.HttpSession;

/**
 * 관리자 기능 컴트롤러
 *
 * 비즈니스 로직: 관리자만 접근 가능한 상품 관리, 주문 관리, 사용자 관리 기능 제공
 */
@Controller
@RequestMapping("/admin")
public class AdminController {

    /** 상품 관리 비즈니스 로직 서비스 */
    @Autowired
    private ProductService productService;

    /** 카테고리 관리 비즈니스 로직 서비스 */
    @Autowired
    private CategoryService categoryService;
    
    /** 주문 관리 비즈니스 로직 서비스 */
    @Autowired
    private OrderService orderService;
    
    /** 주문 데이터 접근 리포지토리 */
    @Autowired
    private OrderRepository orderRepository;
    
    /** 사용자 데이터 접근 리포지토리 */
    @Autowired
    private UserRepository userRepository;

    /**
     * 관리자 권한 확인 유틸리티 메서드
     *
     * 비즈니스 로직: 세션에서 관리자 권한 여부를 확인하여 비인가 접근 차단
     *
     * @param session HTTP 세션 객체
     * @return 관리자 여부 (true: 관리자, false: 일반 사용자)
     */
    private boolean isAdmin(HttpSession session) {
        Boolean isAdmin = (Boolean) session.getAttribute("isAdmin");
        return isAdmin != null && isAdmin;
    }

    /**
     * 관리자 메인 페이지 (상품조회 기본)
     *
     * 비즈니스 로직: 관리자 권한 확인 후 상품조회 페이지로 리다이렉트
     *
     * @param session HTTP 세션
     * @param model 뷰 데이터 전달 모델
     * @return 리다이렉트 경로
     */
    @GetMapping("")
    public String adminMain(HttpSession session, Model model) {
        if (!isAdmin(session)) {
            return "redirect:/login";
        }
        return "redirect:/admin/product-inquiry";
    }

    /**
     * 상품조회 페이지
     *
     * 비즈니스 로직: 관리자 권한 확인 후 상품조회 화면 표시
     *
     * @param session HTTP 세션
     * @param model 뷰 데이터 전달 모델
     * @return 상품조회 뷰 이름 또는 로그인 페이지 리다이렉트
     */
    @GetMapping("/product-inquiry")
    public String productInquiry(HttpSession session, Model model) {
        if (!isAdmin(session)) {
            return "redirect:/login";
        }
        
        Object user = session.getAttribute("user");
        if (user instanceof LoginResponse.UserInfo userInfo) {
            model.addAttribute("adminName", userInfo.getUserName());
            model.addAttribute("adminId", userInfo.getIdForUser());
        }
        
        model.addAttribute("currentPage", "product-inquiry");
        return "admin/admin_product_inquiry";
    }

    /**
     * 상품등록 페이지
     *
     * 비즈니스 로직: 관리자 권한 확인 후 상품등록 화면 표시
     *
     * @param session HTTP 세션
     * @param model 뷰 데이터 전달 모델
     * @return 상품등록 뷰 이름 또는 로그인 페이지 리다이렉트
     */
    @GetMapping("/product-register")
    public String productRegister(HttpSession session, Model model) {
        if (!isAdmin(session)) {
            return "redirect:/login";
        }
        
        Object user = session.getAttribute("user");
        if (user instanceof LoginResponse.UserInfo userInfo) {
            model.addAttribute("adminName", userInfo.getUserName());
            model.addAttribute("adminId", userInfo.getIdForUser());
        }
        
        model.addAttribute("currentPage", "product-register");
        return "admin/admin_product_register";
    }

    /**
     * 주문조회 페이지
     *
     * 비즈니스 로직: 관리자 권한 확인 후 주문조회 화면 표시
     *
     * @param session HTTP 세션
     * @param model 뷰 데이터 전달 모델
     * @return 주문조회 뷰 이름 또는 로그인 페이지 리다이렉트
     */
    @GetMapping("/order-inquiry")
    public String orderInquiry(HttpSession session, Model model) {
        if (!isAdmin(session)) {
            return "redirect:/login";
        }
        
        Object user = session.getAttribute("user");
        if (user instanceof LoginResponse.UserInfo userInfo) {
            model.addAttribute("adminName", userInfo.getUserName());
            model.addAttribute("adminId", userInfo.getIdForUser());
        }
        
        model.addAttribute("currentPage", "order-inquiry");
        return "admin/admin_order_inquiry";
    }

    /**
     * 관리자 회원조회 페이지
     *
     * 비즈니스 로직: 관리자 권한 확인 후 회원조회 화면 표시
     *
     * @param session HTTP 세션
     * @param model 뷰 데이터 전달 모델
     * @return 회원조회 뷰 이름 또는 로그인 페이지 리다이렉트
     */
    @GetMapping("/user-inquiry")
    public String userInquiry(HttpSession session, Model model) {
        if (!isAdmin(session)) {
            return "redirect:/login";
        }
        
        Object user = session.getAttribute("user");
        if (user instanceof LoginResponse.UserInfo userInfo) {
            model.addAttribute("adminName", userInfo.getUserName());
            model.addAttribute("adminId", userInfo.getIdForUser());
        }
        
        model.addAttribute("currentPage", "user-inquiry");
        return "admin/admin_user_inquiry";
    }

    /**
     * 관리자 로그아웃
     *
     * 비즈니스 로직: 세션 무효화 후 메인페이지로 리다이렉트
     *
     * @param session HTTP 세션
     * @return 리다이렉트 경로
     */
    @PostMapping("/logout")
    public String logout(HttpSession session) {
        session.invalidate();
        return "redirect:/main";
    }

    /**
     * GET 방식 관리자 로그아웃
     *
     * 비즈니스 로직: GET 요청으로 로그아웃 처리
     *
     * @param session HTTP 세션
     * @return 리다이렉트 경로
     */
    @GetMapping("/logout")
    public String logoutGet(HttpSession session) {
        return logout(session);
    }

    /**
     * 관리자 상품 조회 API - 전체 상품 리스트 조회
     *
     * 비즈니스 로직: 관리자 권한 확인 후 상품 리스트를 페이지네이션과 검색 조건에 따라 조회
     *
     * @param session HTTP 세션 (관리자 권한 확인용)
     * @param sort 정렬 기준 (기본값: latest)
     * @param page 페이지 번호 (기본값: 1)
     * @param size 페이지 크기 (기본값: 30)
     * @param title 제목 검색어
     * @param author 저자 검색어
     * @param publisher 출판사 검색어
     * @param salesStatus 판매 상태
     * @param startDate 시작 날짜
     * @param endDate 종료 날짜
     * @return 상품 리스트 데이터 (ProductListPageResponse) 또는 권한 오류
     */
    @GetMapping("/api/products")
    @ResponseBody
    public ResponseEntity<ProductListPageResponse> getProducts(
            HttpSession session,
            @RequestParam(defaultValue = "latest") String sort,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "30") int size,
            @RequestParam(required = false) String title,
            @RequestParam(required = false) String author,
            @RequestParam(required = false) String publisher,
            @RequestParam(required = false) String salesStatus,
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate) {
        
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }

        ProductListPageResponse response = productService.searchProductsAdvanced(null, title, author, publisher, sort, page, size, salesStatus, startDate, endDate);
        return ResponseEntity.ok(response);
    }

    /**
     * 관리자 상품 조회 API - 소분류 카테고리별 상품 리스트 조회
     *
     * 비즈니스 로직: 관리자 권한 확인 후 특정 소분류 카테고리에 속한 상품들을 페이지네이션과 검색 조건에 따라 조회
     *
     * @param session HTTP 세션 (관리자 권한 확인용)
     * @param lowCategoryId 소분류 카테고리 ID
     * @param sort 정렬 기준 (기본값: latest)
     * @param page 페이지 번호 (기본값: 1)
     * @param size 페이지 크기 (기본값: 30)
     * @param title 제목 검색어
     * @param author 저자 검색어
     * @param publisher 출판사 검색어
     * @param salesStatus 판매 상태
     * @param startDate 시작 날짜
     * @param endDate 종료 날짜
     * @return 소분류별 상품 리스트 데이터 또는 권한 오류
     */
    @GetMapping("/api/products/category/{lowCategoryId}")
    @ResponseBody
    public ResponseEntity<ProductListPageResponse> getProductsByCategory(
            HttpSession session,
            @PathVariable Integer lowCategoryId,
            @RequestParam(defaultValue = "latest") String sort,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "30") int size,
            @RequestParam(required = false) String title,
            @RequestParam(required = false) String author,
            @RequestParam(required = false) String publisher,
            @RequestParam(required = false) String salesStatus,
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate) {
        
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }

        ProductListPageResponse response = productService.getProductsByLowCategoryAdvanced(lowCategoryId, sort, page, size, title, author, publisher, salesStatus, startDate, endDate);
        return ResponseEntity.ok(response);
    }

    /**
     * 관리자 카테고리 트리 조회 API
     *
     * 비즈니스 로직: 관리자 권한 확인 후 전체 카테고리 트리 구조 반환 (대-중-소분류)
     *
     * @param session HTTP 세션 (관리자 권한 확인용)
     * @return 카테고리 트리 데이터 (CategoryTreeResponse) 또는 권한 오류
     */
    @GetMapping("/api/categories")
    @ResponseBody
    public ResponseEntity<?> getCategories(HttpSession session) {
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }

        return ResponseEntity.ok(categoryService.getCategoryTreeForHeader());
    }

    /**
     * 관리자 카테고리별 도서 개수 조회 API
     *
     * 비즈니스 로직: 관리자 권한 확인 후 대/중/소분류별 도서 개수 통계 제공
     *
     * @param session HTTP 세션 (관리자 권한 확인용)
     * @param level 카테고리 레벨 (top/middle/low)
     * @return 카테고리별 도서 개수 리스트 또는 권한 오류
     */
    @GetMapping("/api/category-counts/{level}")
    @ResponseBody
    public ResponseEntity<?> getCategoryCounts(
            HttpSession session,
            @PathVariable String level) {
        
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }

        switch (level) {
            case "top":
                return ResponseEntity.ok(categoryService.countBooksByTopCategory());
            case "middle":
                return ResponseEntity.ok(categoryService.countBooksByMiddleCategory());
            case "low":
                return ResponseEntity.ok(categoryService.countBooksByLowCategory());
            default:
                return ResponseEntity.badRequest().body("Invalid level parameter");
        }
    }

    /**
     * 관리자 전체 상품 개수 조회 API
     *
     * 비즈니스 로직: 관리자 권한 확인 후 데이터베이스에 등록된 전체 상품 수 반환
     *
     * @param session HTTP 세션 (관리자 권한 확인용)
     * @return 전체 상품 개수 (Long) 또는 권한 오류
     */
    @GetMapping("/api/total-product-count")
    @ResponseBody
    public ResponseEntity<?> getTotalProductCount(HttpSession session) {
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }

        long totalCount = productService.getTotalProductCount();
        return ResponseEntity.ok(totalCount);
    }

    /**
     * 관리자 상품 입고 처리 API
     *
     * 비즈니스 로직: 관리자 권한 확인 후 특정 상품의 재고를 입고 수량만큼 증가
     *
     * @param session HTTP 세션 (관리자 권한 확인용)
     * @param isbn 입고할 상품의 ISBN 코드
     * @param quantity 입고 수량
     * @return 입고 처리 결과 메시지 또는 오류 메시지
     */
    @PostMapping("/api/products/{isbn}/stock-in")
    @ResponseBody
    public ResponseEntity<?> stockIn(
            HttpSession session,
            @PathVariable String isbn,
            @RequestParam int quantity) {
        
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }

        try {
            productService.stockIn(isbn, quantity);
            return ResponseEntity.ok().body("입고 처리되었습니다.");
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("입고 처리 중 오류가 발생했습니다: " + e.getMessage());
        }
    }

    /**
     * 관리자 상품 판매 상태 변경 API
     *
     * 비즈니스 로직: 관리자 권한 확인 후 특정 상품의 판매 상태 변경 (판매중/절판/품절 등)
     *
     * @param session HTTP 세션 (관리자 권한 확인용)
     * @param isbn 상태를 변경할 상품의 ISBN 코드
     * @param status 새로운 판매 상태
     * @return 상태 변경 결과 메시지 또는 오류 메시지
     */
    @PostMapping("/api/products/{isbn}/status")
    @ResponseBody
    public ResponseEntity<?> changeStatus(
            HttpSession session,
            @PathVariable String isbn,
            @RequestParam String status) {
        
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }

        try {
            productService.changeProductStatus(isbn, status);
            return ResponseEntity.ok().body("상태가 변경되었습니다.");
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("상태 변경 중 오류가 발생했습니다: " + e.getMessage());
        }
    }

    /**
     * 관리자 상품 상세 정보 조회 API
     *
     * 비즈니스 로직: 관리자 권한 확인 후 특정 상품의 상세 정보 및 재고 상태 조회
     *
     * @param session HTTP 세션 (관리자 권한 확인용)
     * @param isbn 조회할 상품의 ISBN 코드
     * @return 상품 상세 정보 (Product) 또는 오류 메시지
     */
    @GetMapping("/api/products/{isbn}/detail")
    @ResponseBody
    public ResponseEntity<?> getProductDetail(
            HttpSession session,
            @PathVariable String isbn) {
        
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }

        try {
            Product product = productService.getProductDetailByIsbn(isbn);
            if (product == null) {
                return ResponseEntity.notFound().build();
            }
            
            // DTO로 변환하여 반환 (연관관계 제외)
            java.util.Map<String, Object> productDto = new java.util.HashMap<>();
            productDto.put("isbn", product.getIsbn());
            productDto.put("lowCategory", product.getLowCategory());
            productDto.put("productName", product.getProductName());
            productDto.put("author", product.getAuthor());
            productDto.put("publisher", product.getPublisher());
            productDto.put("price", product.getPrice());
            productDto.put("rate", product.getRate());
            productDto.put("briefDescription", product.getBriefDescription());
            productDto.put("detailDescription", product.getDetailDescription());
            productDto.put("img", product.getImg());
            productDto.put("width", product.getWidth());
            productDto.put("height", product.getHeight());
            productDto.put("page", product.getPage());
            productDto.put("salesStatus", product.getSalesStatus() != null ? product.getSalesStatus().name() : null);
            productDto.put("searchCount", product.getSearchCount());
            productDto.put("regDate", product.getRegDate());
            
            return ResponseEntity.ok(productDto);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("상품 정보 조회 중 오류가 발생했습니다: " + e.getMessage());
        }
    }

    /**
     * 관리자 상품 정보 수정 API
     *
     * 비즈니스 로직: 관리자 권한 확인 후 특정 상품의 기본 정보 (가격 등) 수정
     *
     * @param session HTTP 세션 (관리자 권한 확인용)
     * @param isbn 수정할 상품의 ISBN 코드
     * @param price 새로운 가격 (선택사항)
     * @return 수정 결과 메시지 또는 오류 메시지
     */
    @PostMapping("/api/products/{isbn}/edit")
    @ResponseBody
    public ResponseEntity<?> editProduct(
            HttpSession session,
            @PathVariable String isbn,
            @RequestParam(required = false) Integer price) {
        
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }

        try {
            productService.editProduct(isbn, price);
            return ResponseEntity.ok().body("상품 정보가 수정되었습니다.");
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("상품 정보 수정 중 오류가 발생했습니다: " + e.getMessage());
        }
    }

    /**
     * 관리자 ISBN 중복 확인 API
     *
     * 비즈니스 로직: 관리자 권한 확인 후 상품 등록 시 ISBN 코드 중복 여부 확인
     *
     * @param session HTTP 세션 (관리자 권한 확인용)
     * @param isbn 확인할 ISBN 코드
     * @return 중복 여부 결과 (duplicated: boolean)
     */
    @GetMapping("/api/product/check-isbn")
    @ResponseBody
    public ResponseEntity<java.util.Map<String, Boolean>> checkIsbn(HttpSession session, @RequestParam String isbn) {
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }
        boolean exists = productService.existsById(isbn);
        return ResponseEntity.ok(java.util.Map.of("duplicated", exists));
    }

    /**
     * 관리자 신규 상품 등록 API
     *
     * 비즈니스 로직: 관리자 권한 확인 후 신규 도서 상품 정보를 데이터베이스에 등록
     *
     * @param session HTTP 세션 (관리자 권한 확인용)
     * @param productData 등록할 상품 정보 (ISBN, 상품명, 저자, 가격 등)
     * @return 등록 결과 메시지 또는 오류 메시지
     */
    @PostMapping("/api/product/register")
    @ResponseBody
    public ResponseEntity<?> registerProduct(HttpSession session, @RequestBody java.util.Map<String, Object> body) {
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }
        
        try {
            productService.registerProduct(body);
            return ResponseEntity.ok(java.util.Map.of("success", true, "message", "상품이 성공적으로 등록되었습니다."));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(java.util.Map.of("success", false, "message", e.getMessage()));
        }
    }

    /**
     * 상품 전체 정보 수정 API
     */
    @PostMapping("/api/products/{isbn}/update")
    @ResponseBody
    public ResponseEntity<?> updateProduct(HttpSession session, @PathVariable String isbn, @RequestBody java.util.Map<String, Object> body) {
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }
        
        try {
            productService.updateProductAll(isbn, body);
            return ResponseEntity.ok(java.util.Map.of("success", true, "message", "상품 정보가 수정되었습니다."));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(java.util.Map.of("success", false, "message", e.getMessage()));
        }
    }

    /**
     * 관리자 주문 내역 조회 API
     *
     * 비즈니스 로직: 관리자 권한 확인 후 전체 주문 내역을 검색 조건에 따라 페이지네이션으로 조회
     *
     * @param session HTTP 세션 (관리자 권한 확인용)
     * @param sort 정렬 기준 (기본값: latest)
     * @param page 페이지 번호 (기본값: 1)
     * @param size 페이지 크기 (기본값: 30)
     * @param orderId 주문번호 검색어
     * @param userId 사용자 ID 검색어
     * @param minAmount 최소 주문 금액
     * @param maxAmount 최대 주문 금액
     * @param startDate 조회 시작 날짜
     * @param endDate 조회 종료 날짜
     * @param orderStatus 주문 상태 필터
     * @return 주문 내역 리스트 (AdminOrderPageResponse) 또는 권한 오류
     */
    @GetMapping("/api/orders")
    @ResponseBody
    public ResponseEntity<AdminOrderPageResponse> getOrders(
            HttpSession session,
            @RequestParam(defaultValue = "latest") String sort,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "30") int size,
            @RequestParam(required = false) String orderId,
            @RequestParam(required = false) String userId,
            @RequestParam(required = false) String minAmount,
            @RequestParam(required = false) String maxAmount,
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate,
            @RequestParam(required = false) String orderStatus) {
        
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }

        try {
            System.out.println("주문조회 요청 - sort: " + sort + ", page: " + page + ", size: " + size);
            AdminOrderPageResponse response = orderService.getAdminOrders(
                sort, page, size, orderId, userId, minAmount, maxAmount, 
                startDate, endDate, orderStatus);
            
            System.out.println("주문조회 결과 - 총 " + response.getTotalElements() + "건, " + response.getOrders().size() + "개 반환");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            System.err.println("주문조회 API 실패: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.badRequest().body(null);
        }
    }

    /**
     * 관리자 주문 상태 변경 API
     *
     * 비즈니스 로직: 관리자 권한 확인 후 특정 주문의 상태를 변경 (배송준비/배송완료 등)
     *
     * @param session HTTP 세션 (관리자 권한 확인용)
     * @param orderId 상태를 변경할 주문 ID
     * @param status 새로운 주문 상태
     * @param idForAdmin 주문자 관리 ID
     * @return 상태 변경 결과 메시지 또는 오류 메시지
     */
    @PostMapping("/api/orders/{orderId}/status")
    @ResponseBody
    public ResponseEntity<?> changeOrderStatus(
            HttpSession session,
            @PathVariable String orderId,
            @RequestParam String status,
            @RequestParam String idForAdmin) {
        
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }

        try {
            orderService.updateOrderStatus(orderId, idForAdmin, status);
            return ResponseEntity.ok("주문 상태가 변경되었습니다.");
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("주문 상태 변경 중 오류가 발생했습니다: " + e.getMessage());
        }
    }
    
    /**
     * 관리자 주문 테이블 테스트 API (임시 디버깅용)
     *
     * 비즈니스 로직: 관리자 권한 확인 후 주문 테이블의 전체 데이터 상태를 확인하여 디버깅 정보 제공
     *
     * @param session HTTP 세션 (관리자 권한 확인용)
     * @return 주문 테이블 통계 정보 (Map) 또는 오류 메시지
     */
    @GetMapping("/api/orders/test")
    @ResponseBody
    public ResponseEntity<?> testOrders(HttpSession session) {
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }
        
        try {
            // 단순히 모든 주문 조회해서 개수 확인
            long count = orderRepository.count();
            var allOrders = orderRepository.findAll();
            
            java.util.Map<String, Object> result = new java.util.HashMap<>();
            result.put("totalCount", count);
            result.put("orderCount", allOrders.size());
            result.put("firstOrderId", allOrders.isEmpty() ? null : allOrders.get(0).getOrderId());
            
            // 첫 번째 주문의 상세 정보도 추가
            if (!allOrders.isEmpty()) {
                var firstOrder = allOrders.get(0);
                result.put("firstOrderStatus", firstOrder.getOrderStatus());
                result.put("firstOrderDate", firstOrder.getOrderDate());
                result.put("firstOrderAmount", firstOrder.getTotalPaidPrice());
            }
            
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.badRequest().body("테스트 실패: " + e.getMessage());
        }
    }
    
    /**
     * 관리자 간단 주문 조회 API (임시 디버깅용)
     *
     * 비즈니스 로직: 관리자 권한 확인 후 간단한 주문 리스트를 제공 (복잡한 조인 없이)
     *
     * @param session HTTP 세션 (관리자 권한 확인용)
     * @return 간단 주문 리스트 또는 오류 메시지
     */
    @GetMapping("/api/orders/simple")
    @ResponseBody
    public ResponseEntity<?> getSimpleOrders(HttpSession session) {
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }
        
        try {
            // 페이징 없이 최근 10개 주문만 조회
            var allOrders = orderRepository.findAll();
            
            java.util.List<java.util.Map<String, Object>> simpleOrders = new java.util.ArrayList<>();
            
            for (int i = 0; i < Math.min(10, allOrders.size()); i++) {
                var order = allOrders.get(i);
                java.util.Map<String, Object> orderMap = new java.util.HashMap<>();
                orderMap.put("orderId", order.getOrderId());
                orderMap.put("orderDate", order.getOrderDate());
                orderMap.put("orderStatus", order.getOrderStatus());
                orderMap.put("totalPaidPrice", order.getTotalPaidPrice());
                orderMap.put("idForAdmin", order.getIdForAdmin());
                simpleOrders.add(orderMap);
            }
            
            java.util.Map<String, Object> result = new java.util.HashMap<>();
            result.put("orders", simpleOrders);
            result.put("totalCount", allOrders.size());
            
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.badRequest().body("간단 조회 실패: " + e.getMessage());
        }
    }
    
    /**
     * 관리자 회원조회 API
     *
     * 비즈니스 로직: 관리자 권한 확인 후 전체 회원 정보를 검색 조건에 따라 페이지네이션으로 조회
     *
     * @param session HTTP 세션 (관리자 권한 확인용)
     * @param sort 정렬 기준 (기본값: idAdminAsc)
     * @param page 페이지 번호 (기본값: 1)
     * @param size 페이지 크기 (기본값: 30)
     * @param userName 회원명 검색어 (선택)
     * @param userId 회원 ID 검색어 (선택)
     * @param userGrade 회원 등급 (선택)
     * @param userStatus 회원 상태 (선택)
     * @param startDate 가입 시작일 (선택)
     * @param endDate 가입 종료일 (선택)
     * @return 회원 리스트 및 페이징 정보(Map) 또는 권한 오류
     */
    @GetMapping("/api/users")
    @ResponseBody
    public ResponseEntity<?> getUsers(HttpSession session,
            @RequestParam(defaultValue = "idAdminAsc") String sort,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "30") int size,
            @RequestParam(required = false) String userName,
            @RequestParam(required = false) String userId,
            @RequestParam(required = false) String userGrade,
            @RequestParam(required = false) String userStatus,
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate) {
        if (!isAdmin(session)) {
            return ResponseEntity.status(401).build();
        }
        try {
            org.springframework.data.domain.Sort sortObj;
            switch (sort) {
                case "nameAsc": sortObj = org.springframework.data.domain.Sort.by("userName").ascending(); break;
                case "nameDesc": sortObj = org.springframework.data.domain.Sort.by("userName").descending(); break;
                case "idAdminAsc": sortObj = org.springframework.data.domain.Sort.by("idForAdmin").ascending(); break;
                case "idAdminDesc": sortObj = org.springframework.data.domain.Sort.by("idForAdmin").descending(); break;
                case "idUserAsc": sortObj = org.springframework.data.domain.Sort.by("idForUser").ascending(); break;
                case "idUserDesc": sortObj = org.springframework.data.domain.Sort.by("idForUser").descending(); break;
                case "regDateAsc": sortObj = org.springframework.data.domain.Sort.by("regDate").ascending(); break;
                case "regDateDesc": sortObj = org.springframework.data.domain.Sort.by("regDate").descending(); break;
                default: sortObj = org.springframework.data.domain.Sort.by("idForAdmin").ascending();
            }
            org.springframework.data.domain.PageRequest pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, sortObj);

            // 동적 쿼리(Specification) 조립
            org.springframework.data.jpa.domain.Specification<User> spec = (root, query, cb) -> cb.conjunction();
            if (userName != null && !userName.trim().isEmpty()) {
                spec = spec.and((root, query, cb) -> cb.like(cb.lower(root.get("userName")), "%" + userName.trim().toLowerCase() + "%"));
            }
            if (userId != null && !userId.trim().isEmpty()) {
                spec = spec.and((root, query, cb) -> cb.or(
                    cb.equal(root.get("idForAdmin"), userId.trim()),
                    cb.equal(root.get("idForUser"), userId.trim())
                ));
            }
            if (userGrade != null && !userGrade.trim().isEmpty()) {
                spec = spec.and((root, query, cb) -> cb.equal(root.get("userGradeId"), userGrade.trim()));
            }
            if (userStatus != null && !userStatus.trim().isEmpty()) {
                spec = spec.and((root, query, cb) -> cb.equal(root.get("userStatus"), userStatus.trim()));
            }
            if ((startDate != null && !startDate.isEmpty()) || (endDate != null && !endDate.isEmpty())) {
                java.time.LocalDateTime start = (startDate != null && !startDate.isEmpty()) ? java.time.LocalDate.parse(startDate).atStartOfDay() : java.time.LocalDateTime.MIN;
                java.time.LocalDateTime end = (endDate != null && !endDate.isEmpty()) ? java.time.LocalDate.parse(endDate).atTime(23,59,59) : java.time.LocalDateTime.MAX;
                spec = spec.and((root, query, cb) -> cb.between(root.get("regDate"), start, end));
            }

            org.springframework.data.domain.Page<User> userPage = userRepository.findAll(spec, pageRequest);

            java.util.List<java.util.Map<String, Object>> users = new java.util.ArrayList<>();
            for (User user : userPage.getContent()) {
                java.util.Map<String, Object> userMap = new java.util.HashMap<>();
                userMap.put("idForAdmin", user.getIdForAdmin());
                userMap.put("idForUser", user.getIdForUser());
                userMap.put("password", user.getUserPwd());
                userMap.put("userName", user.getUserName());
                userMap.put("nickname", user.getUserNickname());
                userMap.put("email", user.getUserEmail());
                userMap.put("phoneNumber", user.getUserPhoneNumber());
                // 주소 합치기
                String fullAddress = "";
                if (user.getUserAddress() != null && !user.getUserAddress().trim().isEmpty()) {
                    fullAddress = user.getUserAddress().trim();
                }
                if (user.getUserAddressDetail() != null && !user.getUserAddressDetail().trim().isEmpty()) {
                    if (!fullAddress.isEmpty()) {
                        fullAddress += ", " + user.getUserAddressDetail().trim();
                    } else {
                        fullAddress = user.getUserAddressDetail().trim();
                    }
                }
                userMap.put("address", fullAddress.isEmpty() ? "N/A" : fullAddress);
                userMap.put("birthDate", user.getUserBirth());
                userMap.put("gender", user.getUserGender() != null ? (user.getUserGender() == User.Gender.MALE ? "남" : "여") : "N/A");
                userMap.put("userGrade", user.getUserGradeId());
                userMap.put("regDate", user.getRegDate());
                userMap.put("updateDate", user.getUpdateDate());
                userMap.put("lastLogin", user.getLastLoginDate());
                userMap.put("userStatus", user.getUserStatus() != null ? user.getUserStatus().toString() : "N/A");
                users.add(userMap);
            }
            java.util.Map<String, Object> result = new java.util.HashMap<>();
            result.put("users", users);
            result.put("currentPage", page);
            result.put("totalPages", userPage.getTotalPages());
            result.put("totalElements", userPage.getTotalElements());
            result.put("pageSize", size);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.badRequest().body("회원 조회 실패: " + e.getMessage());
        }
    }
}