package bookstore_ai_project.controller;

import bookstore_ai_project.dto.response.CategoryCountResponse;
import bookstore_ai_project.dto.response.LoginResponse;
import bookstore_ai_project.entity.Order;
import bookstore_ai_project.service.CategoryService;
import bookstore_ai_project.dto.response.ProductSimpleResponse;
import bookstore_ai_project.service.ProductService;
import bookstore_ai_project.dto.request.UserUpdateRequest;
import bookstore_ai_project.dto.response.OrderHistoryResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.http.ResponseEntity;
import java.util.*;
import java.util.ArrayList;
import java.time.LocalDateTime;
import java.time.temporal.TemporalAdjusters;
import java.time.DayOfWeek;
import bookstore_ai_project.repository.UserRepository;
import bookstore_ai_project.repository.OrderRepository;
import bookstore_ai_project.repository.OrderDetailRepository;
import bookstore_ai_project.repository.ProductRepository;
import bookstore_ai_project.repository.ProductReviewRepository;
import jakarta.servlet.http.HttpSession;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import bookstore_ai_project.entity.ProductReview;
import bookstore_ai_project.entity.OrderId;

@Controller
public class MainController {

    @Autowired(required = false)
    private CategoryService categoryService;

    @Autowired(required = false)
    private ProductService productService;

    @Autowired(required = false)
    private UserRepository userRepository;

    @Autowired(required = false)
    private OrderRepository orderRepository;

    @Autowired(required = false)
    private OrderDetailRepository orderDetailRepository;

    @Autowired(required = false)
    private ProductRepository productRepository;

    @Autowired(required = false)
    private ProductReviewRepository productReviewRepository;

    @RequestMapping("/main")
    public String mainPage(Model model) {
        var categoryTree = categoryService.getCategoryTreeForHeader();
        model.addAttribute("topCategories", categoryTree.getTopCategories());
        model.addAttribute("middleCategoriesMap", categoryTree.getMiddleCategoriesMap());
        model.addAttribute("lowCategoriesMap", categoryTree.getLowCategoriesMap());
        return "product/main";
    }

    @RequestMapping("/mypage")
    public String myPage(HttpSession session, Model model) {
        // 🔒 로그인 검증: 비로그인 시 로그인 페이지로 리다이렉트
        Object userObj = session.getAttribute("user");
        if (userObj == null || !(userObj instanceof LoginResponse.UserInfo)) {
            return "redirect:/login?redirectUrl=/mypage";
        }
        
        // 🔒 관리자 접근 차단
        Boolean isAdmin = (Boolean) session.getAttribute("isAdmin");
        if (isAdmin != null && isAdmin) {
            model.addAttribute("error", "일반 사용자 전용 화면입니다.");
            return "redirect:/admin";
        }
        
        LoginResponse.UserInfo userInfo =
            (LoginResponse.UserInfo) userObj;
        String userId = userInfo.getIdForUser();
        userRepository.findByIdForUser(userId).ifPresent(user -> model.addAttribute("userInfo", user));
        // 헤더 카테고리 데이터도 항상 추가 (CategoryTreeResponse 활용)
        var categoryTree = categoryService.getCategoryTreeForHeader();
        model.addAttribute("topCategories", categoryTree.getTopCategories());
        model.addAttribute("middleCategoriesMap", categoryTree.getMiddleCategoriesMap());
        model.addAttribute("lowCategoriesMap", categoryTree.getLowCategoriesMap());
        return "user/mypage";
    }

    @GetMapping("/api/popular-keywords")
    @ResponseBody
    public Map<String, Object> getPopularKeywords() {
        List<ProductSimpleResponse> keywords = productService.getPopularProducts(10);
        String baseTime = java.time.LocalDateTime.now().withMinute(0).withSecond(0).format(java.time.format.DateTimeFormatter.ofPattern("yyyy.MM.dd HH:00"));
        Map<String, Object> result = new java.util.HashMap<>();
        result.put("keywords", keywords);
        result.put("baseTime", baseTime);
        return result;
    }

    @GetMapping("/api/bestseller")
    @ResponseBody
    public List<ProductSimpleResponse> getBestseller(@RequestParam String type) {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime startDate, endDate;
        if ("weekly".equalsIgnoreCase(type)) {
            // 이번 주 월요일 00:00 ~ 일요일 23:59:59
            startDate = now.with(DayOfWeek.MONDAY).withHour(0).withMinute(0).withSecond(0).withNano(0);
            endDate = now.with(DayOfWeek.SUNDAY).withHour(23).withMinute(59).withSecond(59).withNano(999_999_999);
        } else if ("monthly".equalsIgnoreCase(type)) {
            // 이번 달 1일 00:00 ~ 말일 23:59:59
            startDate = now.withDayOfMonth(1).withHour(0).withMinute(0).withSecond(0).withNano(0);
            endDate = now.with(TemporalAdjusters.lastDayOfMonth()).withHour(23).withMinute(59).withSecond(59).withNano(999_999_999);
        } else if ("yearly".equalsIgnoreCase(type)) {
            // 올해 1월 1일 00:00 ~ 12월 31일 23:59:59
            startDate = now.withDayOfYear(1).withHour(0).withMinute(0).withSecond(0).withNano(0);
            endDate = now.with(TemporalAdjusters.lastDayOfYear()).withHour(23).withMinute(59).withSecond(59).withNano(999_999_999);
        } else {
            // 기본: 주간
            startDate = now.with(DayOfWeek.MONDAY).withHour(0).withMinute(0).withSecond(0).withNano(0);
            endDate = now.with(DayOfWeek.SUNDAY).withHour(23).withMinute(59).withSecond(59).withNano(999_999_999);
        }
        return productService.getBestsellerByPeriod(startDate, endDate, 10);
    }

    @GetMapping("/api/newproducts")
    @ResponseBody
    public List<ProductSimpleResponse> getNewProducts() {
        return productService.getNewProducts(10);
    }

    @GetMapping("/api/category/top-count")
    @ResponseBody
    public List<CategoryCountResponse> getTopCategoryBookCount() {
        return categoryService.countBooksByTopCategory();
    }

    @GetMapping("/api/category/middle-count")
    @ResponseBody
    public List<CategoryCountResponse> getMiddleCategoryBookCount() {
        return categoryService.countBooksByMiddleCategory();
    }

    @GetMapping("/api/category/low-count")
    @ResponseBody
    public List<CategoryCountResponse> getLowCategoryBookCount() {
        return categoryService.countBooksByLowCategory();
    }

    @GetMapping("/api/user/check-nickname")
    @ResponseBody
    public Map<String, Object> checkNickname(@RequestParam String nickname) {
        boolean exists = userRepository.existsByUserNickname(nickname);
        Map<String, Object> result = new HashMap<>();
        result.put("result", !exists);
        result.put("message", exists ? "이미 사용중입니다." : "사용 가능합니다.");
        return result;
    }

    @GetMapping("/api/user/check-email")
    @ResponseBody
    public Map<String, Object> checkEmail(@RequestParam String email) {
        boolean exists = userRepository.existsByUserEmail(email);
        Map<String, Object> result = new HashMap<>();
        result.put("result", !exists);
        result.put("message", exists ? "이미 사용중입니다." : "사용 가능합니다.");
        return result;
    }

    @PostMapping("/api/user/update")
    @ResponseBody
    public Map<String, Object> updateUser(@RequestBody UserUpdateRequest request, HttpSession session) {
        Map<String, Object> result = new HashMap<>();
        
        try {
            Object userObj = session.getAttribute("user");
            if (userObj == null || !(userObj instanceof LoginResponse.UserInfo userInfo)) {
                result.put("success", false);
                result.put("message", "로그인이 필요합니다.");
                return result;
            }
            
            String userId = userInfo.getIdForUser();
            var userOpt = userRepository.findByIdForUser(userId);
            
            if (userOpt.isEmpty()) {
                result.put("success", false);
                result.put("message", "사용자를 찾을 수 없습니다.");
                return result;
            }
            
            var user = userOpt.get();
            
            // 회원정보 업데이트
            if (request.getUserName() != null && !request.getUserName().trim().isEmpty()) {
                user.setUserName(request.getUserName().trim());
            }
            
            if (request.getUserNickname() != null && !request.getUserNickname().trim().isEmpty()) {
                user.setUserNickname(request.getUserNickname().trim());
            }
            
            if (request.getUserPwd() != null && !request.getUserPwd().trim().isEmpty()) {
                user.setUserPwd(request.getUserPwd().trim());
            }
            
            if (request.getUserEmailId() != null && request.getUserEmailDomain() != null) {
                String email = request.getUserEmailId().trim() + "@" + request.getUserEmailDomain().trim();
                user.setUserEmail(email);
            }
            
            if (request.getUserPhone1() != null && request.getUserPhone2() != null && request.getUserPhone3() != null) {
                String phone = request.getUserPhone1().trim() + request.getUserPhone2().trim() + request.getUserPhone3().trim();
                user.setUserPhoneNumber(phone);
            }
            
            if (request.getUserAddress() != null && !request.getUserAddress().trim().isEmpty()) {
                user.setUserAddress(request.getUserAddress().trim());
            }
            
            if (request.getUserAddressDetail() != null && !request.getUserAddressDetail().trim().isEmpty()) {
                user.setUserAddressDetail(request.getUserAddressDetail().trim());
            }
            
            // 업데이트 날짜 설정
            user.setUpdateDate(java.time.LocalDateTime.now());
            
            // DB에 저장
            userRepository.save(user);
            
            result.put("success", true);
            result.put("message", "회원정보가 성공적으로 수정되었습니다.");
            
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "회원정보 수정 중 문제가 발생했습니다. 입력 정보를 확인하고 다시 시도해주세요.");
        }
        
        return result;
    }

    @GetMapping("/api/user/orders")
    @ResponseBody
    public List<OrderHistoryResponse> getUserOrders(HttpSession session) {
        List<OrderHistoryResponse> orderHistory = new ArrayList<>();
        
        try {
            Object userObj = session.getAttribute("user");
            if (userObj == null || !(userObj instanceof LoginResponse.UserInfo userInfo)) {
                return orderHistory;
            }
            
            String userId = userInfo.getIdForUser();
            var userOpt = userRepository.findByIdForUser(userId);
            
            if (userOpt.isEmpty()) {
                return orderHistory;
            }
            
            var user = userOpt.get();
            var orders = orderRepository.findByIdForAdminOrderByOrderDateDesc(user.getIdForAdmin());
            
            for (var order : orders) {
                // 주문상태가 ORDER_FAILED 또는 ORDER_REQUESTED인 경우 건너뜀
                if (order.getOrderStatus() == Order.OrderStatus.ORDER_FAILED ||
                    order.getOrderStatus() == Order.OrderStatus.ORDER_REQUESTED) {
                    continue;
                }
                OrderHistoryResponse orderResponse = new OrderHistoryResponse();
                orderResponse.setOrderId(order.getOrderId());
                orderResponse.setOrderDate(order.getOrderDate());
                orderResponse.setOrderStatus(order.getOrderStatus().toString());
                orderResponse.setTotalProductCategory(order.getTotalProductCategory());
                orderResponse.setTotalProductQuantity(order.getTotalProductQuantity());
                orderResponse.setTotalPaidPrice(order.getTotalPaidPrice());
                
                // 주문 상세 정보 조회
                var orderDetails = orderDetailRepository.findByOrderIdAndIdForAdmin(order.getOrderId(), order.getIdForAdmin());
                List<OrderHistoryResponse.OrderDetailResponse> detailResponses = new ArrayList<>();
                
                for (var detail : orderDetails) {
                    OrderHistoryResponse.OrderDetailResponse detailResponse = new OrderHistoryResponse.OrderDetailResponse();
                    detailResponse.setIsbn(detail.getIsbn());
                    detailResponse.setOrderItemQuantity(detail.getOrderItemQuantity());
                    detailResponse.setEachProductPrice(detail.getEachProductPrice());
                    detailResponse.setTotalProductPrice(detail.getTotalProductPrice()); // 추가
                    
                    // 상품 정보 조회
                    var productOpt = productRepository.findById(detail.getIsbn());
                    if (productOpt.isPresent()) {
                        var product = productOpt.get();
                        detailResponse.setProductTitle(product.getProductName());
                        detailResponse.setAuthor(product.getAuthor());
                        detailResponse.setImg(product.getImg()); // 이미지 세팅
                    }
                    
                    // 주문별 리뷰 조회 (soft delete 제외)
                    var reviewOpt = productReviewRepository.findActiveByOrderIdAndIsbnAndIdForAdmin(
                        order.getOrderId(), detail.getIsbn(), user.getIdForAdmin());
                    if (reviewOpt.isPresent()) {
                        var review = reviewOpt.get();
                        detailResponse.setHasReview(true);
                        detailResponse.setReviewId(review.getProductReviewId());
                        detailResponse.setReviewTitle(review.getReviewTitle());
                        detailResponse.setReviewContent(review.getReviewContent());
                        detailResponse.setDeleteDate(null);
                    } else {
                        detailResponse.setHasReview(false);
                        detailResponse.setReviewId(null);
                        detailResponse.setReviewTitle(null);
                        detailResponse.setReviewContent(null);
                        detailResponse.setDeleteDate(null);
                    }
                    
                    detailResponses.add(detailResponse);
                }
                
                orderResponse.setOrderDetails(detailResponses);
                orderHistory.add(orderResponse);
            }
            
        } catch (Exception e) {
            System.err.println("주문내역 조회 오류: " + e.getMessage());
            // 예외 발생 시에도 항상 빈 리스트 반환
            return orderHistory;
        }
        
        return orderHistory;
    }

    @PostMapping("/api/orders/cancel")
    @ResponseBody
    public Map<String, Object> cancelOrder(@RequestBody Map<String, Object> req, HttpSession session) {
        Map<String, Object> result = new HashMap<>();
        try {
            Object userObj = session.getAttribute("user");
            if (userObj == null || !(userObj instanceof LoginResponse.UserInfo userInfo)) {
                result.put("success", false);
                result.put("message", "로그인이 필요합니다.");
                return result;
            }
            String idForAdmin = userInfo.getIdForAdmin();
            String orderId = (String) req.get("orderId");
            if (orderId == null) {
                result.put("success", false);
                result.put("message", "주문번호가 필요합니다.");
                return result;
            }
            var orderOpt = orderRepository.findById(new OrderId(orderId, idForAdmin));
            if (orderOpt.isEmpty()) {
                result.put("success", false);
                result.put("message", "주문을 찾을 수 없습니다.");
                return result;
            }
            var order = orderOpt.get();
            if (!idForAdmin.equals(order.getIdForAdmin())) {
                result.put("success", false);
                result.put("message", "본인 주문만 취소할 수 있습니다.");
                return result;
            }
            if (!"ORDER_COMPLETED".equals(order.getOrderStatus().toString())) {
                result.put("success", false);
                result.put("message", "이 상태에서는 주문취소가 불가능합니다.");
                return result;
            }
            order.setOrderStatus(Order.OrderStatus.CANCEL_COMPLETED);
            orderRepository.save(order);
            result.put("success", true);
            result.put("message", "주문취소가 완료되었습니다.");
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "주문취소 중 오류: " + e.getMessage());
        }
        return result;
    }

    @PostMapping("/api/review/write")
    @ResponseBody
    public Map<String, Object> writeReview(@RequestBody Map<String, Object> req, HttpSession session) {
        Map<String, Object> result = new HashMap<>();
        try {
            Object userObj = session.getAttribute("user");
            if (userObj == null || !(userObj instanceof LoginResponse.UserInfo userInfo)) {
                result.put("success", false);
                result.put("message", "로그인이 필요합니다.");
                return result;
            }
            String idForAdmin = userInfo.getIdForAdmin();
            String orderId = (String) req.get("orderId");
            String isbn = (String) req.get("isbn");
            String title = (String) req.get("title");
            String content = (String) req.get("content");
            if (orderId == null || isbn == null || title == null || content == null) {
                result.put("success", false);
                result.put("message", "필수값 누락");
                return result;
            }
            // 해당 주문의 해당 상품에 이미 리뷰가 있으면 등록 불가 (soft delete 제외)
            boolean exists = productReviewRepository.existsActiveByOrderIdAndIsbnAndIdForAdmin(orderId, isbn, idForAdmin);
            if (exists) {
                result.put("success", false);
                result.put("message", "이미 리뷰가 존재합니다.");
                return result;
            }
            ProductReview review = new ProductReview();
            review.setOrderId(orderId);
            review.setIsbn(isbn);
            review.setIdForAdmin(idForAdmin);
            review.setReviewTitle(title);
            review.setReviewContent(content);
            review.setRegDate(LocalDateTime.now());
            productReviewRepository.save(review);
            result.put("success", true);
            result.put("message", "리뷰가 등록되었습니다.");
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "리뷰 등록 중 오류: " + e.getMessage());
        }
        return result;
    }

    @PostMapping("/api/review/edit")
    @ResponseBody
    public Map<String, Object> editReview(@RequestBody Map<String, Object> req, HttpSession session) {
        Map<String, Object> result = new HashMap<>();
        try {
            Object userObj = session.getAttribute("user");
            if (userObj == null || !(userObj instanceof LoginResponse.UserInfo userInfo)) {
                result.put("success", false);
                result.put("message", "로그인이 필요합니다.");
                return result;
            }
            if (req.get("reviewId") == null || "undefined".equals(req.get("reviewId").toString())) {
                result.put("success", false);
                result.put("message", "리뷰 ID가 올바르지 않습니다.");
                return result;
            }
            Integer reviewId = req.get("reviewId") instanceof Integer ? (Integer) req.get("reviewId") : Integer.parseInt(req.get("reviewId").toString());
            String title = (String) req.get("title");
            String content = (String) req.get("content");
            var reviewOpt = productReviewRepository.findById(reviewId);
            if (reviewOpt.isEmpty()) {
                result.put("success", false);
                result.put("message", "리뷰를 찾을 수 없습니다.");
                return result;
            }
            ProductReview review = reviewOpt.get();
            review.setReviewTitle(title);
            review.setReviewContent(content);
            review.setUpdateDate(LocalDateTime.now());
            productReviewRepository.save(review);
            result.put("success", true);
            result.put("message", "리뷰가 수정되었습니다.");
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "리뷰 수정 중 오류: " + e.getMessage());
        }
        return result;
    }

    @PostMapping("/api/review/delete")
    @ResponseBody
    public Map<String, Object> deleteReview(@RequestBody Map<String, Object> req, HttpSession session) {
        Map<String, Object> result = new HashMap<>();
        try {
            Object userObj = session.getAttribute("user");
            if (userObj == null || !(userObj instanceof LoginResponse.UserInfo userInfo)) {
                result.put("success", false);
                result.put("message", "로그인이 필요합니다.");
                return result;
            }
            if (req.get("reviewId") == null || "undefined".equals(req.get("reviewId").toString())) {
                result.put("success", false);
                result.put("message", "리뷰 ID가 올바르지 않습니다.");
                return result;
            }
            Integer reviewId = req.get("reviewId") instanceof Integer ? (Integer) req.get("reviewId") : Integer.parseInt(req.get("reviewId").toString());
            var reviewOpt = productReviewRepository.findById(reviewId);
            if (reviewOpt.isEmpty()) {
                result.put("success", false);
                result.put("message", "리뷰를 찾을 수 없습니다.");
                return result;
            }
            ProductReview review = reviewOpt.get();
            review.setDeleteDate(LocalDateTime.now());
            productReviewRepository.save(review);
            result.put("success", true);
            result.put("message", "리뷰가 삭제되었습니다.");
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "리뷰 삭제 중 오류: " + e.getMessage());
        }
        return result;
    }

    /**
     * 카테고리별 책 개수 조회 API (메인 헤더용)
     */
    @GetMapping("/api/category-counts/{level}")
    @ResponseBody
    public ResponseEntity<?> getCategoryCounts(@PathVariable String level) {
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
     * 전체 상품 개수 조회 API (메인 헤더용)
     */
    @GetMapping("/api/total-product-count")
    @ResponseBody
    public ResponseEntity<?> getTotalProductCount() {
        long totalCount = productService.getTotalProductCount();
        return ResponseEntity.ok(totalCount);
    }
}