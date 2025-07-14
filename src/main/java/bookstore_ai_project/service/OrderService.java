package bookstore_ai_project.service;

import bookstore_ai_project.dto.response.ProductSimpleResponse;
import bookstore_ai_project.dto.response.AdminOrderHistoryResponse;
import bookstore_ai_project.dto.response.AdminOrderPageResponse;
import bookstore_ai_project.entity.OrderId;
import bookstore_ai_project.entity.Product;
import bookstore_ai_project.entity.Order;
import bookstore_ai_project.entity.User;
import bookstore_ai_project.repository.ProductRepository;
import bookstore_ai_project.repository.OrderRepository;
import bookstore_ai_project.repository.OrderDetailRepository;
import bookstore_ai_project.repository.UserRepository;
import bookstore_ai_project.repository.StockRepository;
import bookstore_ai_project.entity.Stock;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeParseException;

@Service
public class OrderService {
    @Autowired
    private ProductRepository productRepository;
    
    @Autowired
    private OrderRepository orderRepository;
    
    @Autowired
    private OrderDetailRepository orderDetailRepository;
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private StockRepository stockRepository;

    // 상품정보 조회 예시 (실제 구현에서는 ProductRepository 등에서 조회)
    public List<ProductSimpleResponse> getOrderProductList(List<String> isbns, List<Integer> quantities, HttpSession session) {
        List<ProductSimpleResponse> result = new ArrayList<>();
        for (int i = 0; i < isbns.size(); i++) {
            String isbn = isbns.get(i);
            int qty = (quantities != null && quantities.size() > i) ? quantities.get(i) : 1;
            // 실제 구현: 상품정보 DB에서 조회
            ProductSimpleResponse product = findProductByIsbn(isbn);
            if (product != null) {
                product.setProductQuantity(qty);
                result.add(product);
            }
        }
        return result;
    }

    // 실제 상품정보 조회 로직 구현
    private ProductSimpleResponse findProductByIsbn(String isbn) {
        Product product = productRepository.findById(isbn).orElse(null);
        if (product == null) {
            return null;
        }
        return new ProductSimpleResponse(
            product.getIsbn(),
            product.getProductName(),
            product.getImg(),
            product.getAuthor(),
            product.getSearchCount(),
            product.getRegDate(),
            null, // productQuantity는 나중에 setProductQuantity로 설정
            product.getPrice() // price 필드 추가
        );
    }

    /**
     * 관리자용 주문 조회 (페이징, 정렬, 검색 지원)
     */
    public AdminOrderPageResponse getAdminOrders(String sort, int page, int size, 
            String orderId, String userId, String minAmount, String maxAmount, 
            String startDate, String endDate, String orderStatus) {
        
        // 정렬 기준 설정
        Sort sortBy;
        switch (sort) {
            case "oldest":
                sortBy = Sort.by(Sort.Direction.ASC, "orderDate");
                break;
            case "highPrice":
                sortBy = Sort.by(Sort.Direction.DESC, "totalPaidPrice");
                break;
            case "lowPrice":
                sortBy = Sort.by(Sort.Direction.ASC, "totalPaidPrice");
                break;
            case "latest":
            default:
                sortBy = Sort.by(Sort.Direction.DESC, "orderDate");
                break;
        }
        
        Pageable pageable = PageRequest.of(page - 1, size, sortBy);
        
        // 검색 조건에 따른 주문 조회
        Page<Order> orders;
        
        try {
            if (hasSearchConditions(orderId, userId, minAmount, maxAmount, startDate, endDate, orderStatus)) {
                orders = searchOrdersWithConditions(orderId, userId, minAmount, maxAmount, 
                        startDate, endDate, orderStatus, pageable);
            } else {
                // 조건 없이 전체 조회
                orders = orderRepository.findAll(pageable);
            }
        } catch (Exception e) {
            System.err.println("주문 조회 실패: " + e.getMessage());
            e.printStackTrace();
            throw e;
        }
        
        // DTO 변환
        List<AdminOrderHistoryResponse> orderResponses = new ArrayList<>();
        for (Order order : orders.getContent()) {
            AdminOrderHistoryResponse response = convertToAdminOrderResponse(order);
            orderResponses.add(response);
        }
        
        AdminOrderPageResponse pageResponse = new AdminOrderPageResponse();
        pageResponse.setOrders(orderResponses);
        pageResponse.setTotalPages(orders.getTotalPages());
        pageResponse.setCurrentPage(page);
        pageResponse.setTotalElements(orders.getTotalElements());
        pageResponse.setPageSize(size);
        
        return pageResponse;
    }
    
    /**
     * 검색 조건이 있는지 확인
     */
    private boolean hasSearchConditions(String orderId, String userId, String minAmount, 
            String maxAmount, String startDate, String endDate, String orderStatus) {
        return (orderId != null && !orderId.trim().isEmpty()) ||
               (userId != null && !userId.trim().isEmpty()) ||
               (minAmount != null && !minAmount.trim().isEmpty()) ||
               (maxAmount != null && !maxAmount.trim().isEmpty()) ||
               (startDate != null && !startDate.trim().isEmpty()) ||
               (endDate != null && !endDate.trim().isEmpty()) ||
               (orderStatus != null && !orderStatus.trim().isEmpty());
    }
    
    /**
     * 검색 조건에 따른 주문 조회 (Repository에서 구현 필요)
     */
    private Page<Order> searchOrdersWithConditions(String orderId, String userId, 
            String minAmount, String maxAmount, String startDate, String endDate, 
            String orderStatus, Pageable pageable) {
        
        // 날짜 파싱
        LocalDateTime startDateTime = null;
        LocalDateTime endDateTime = null;
        
        if (startDate != null && !startDate.trim().isEmpty()) {
            try {
                startDateTime = LocalDate.parse(startDate).atStartOfDay();
            } catch (DateTimeParseException e) {
                // 잘못된 날짜 형식 무시
            }
        }
        
        if (endDate != null && !endDate.trim().isEmpty()) {
            try {
                endDateTime = LocalDate.parse(endDate).atTime(23, 59, 59);
            } catch (DateTimeParseException e) {
                // 잘못된 날짜 형식 무시
            }
        }
        
        // 금액 파싱
        Integer minAmountInt = null;
        Integer maxAmountInt = null;
        
        if (minAmount != null && !minAmount.trim().isEmpty()) {
            try {
                minAmountInt = Integer.parseInt(minAmount);
            } catch (NumberFormatException e) {
                // 잘못된 숫자 형식 무시
            }
        }
        
        if (maxAmount != null && !maxAmount.trim().isEmpty()) {
            try {
                maxAmountInt = Integer.parseInt(maxAmount);
            } catch (NumberFormatException e) {
                // 잘못된 숫자 형식 무시
            }
        }
        
        // 주문상태 파싱
        Order.OrderStatus status = null;
        if (orderStatus != null && !orderStatus.trim().isEmpty()) {
            try {
                status = Order.OrderStatus.valueOf(orderStatus);
            } catch (IllegalArgumentException e) {
                // 잘못된 상태값 무시
            }
        }
        
        // 사용자 ID로 검색할 경우 id_for_admin과 id_for_user 모두에서 검색
        List<String> userAdminIds = null;
        if (userId != null && !userId.trim().isEmpty()) {
            userAdminIds = new ArrayList<>();
            try {
                // id_for_admin으로 정확 일치 검색
                List<User> usersByAdmin = userRepository.findByIdForAdminExact(userId);
                for (User user : usersByAdmin) {
                    if (!userAdminIds.contains(user.getIdForAdmin())) {
                        userAdminIds.add(user.getIdForAdmin());
                    }
                }
                
                // id_for_user로 정확 일치 검색
                List<User> usersByUser = userRepository.findByIdForUserExact(userId);
                for (User user : usersByUser) {
                    if (!userAdminIds.contains(user.getIdForAdmin())) {
                        userAdminIds.add(user.getIdForAdmin());
                    }
                }
                
                // 검색 결과가 없으면 빈 결과를 반환하도록 특별 값 설정
                if (userAdminIds.isEmpty()) {
                    userAdminIds.add("NO_MATCHING_USER"); // 존재하지 않는 값으로 설정
                }
            } catch (Exception e) {
                System.err.println("사용자 검색 실패: " + e.getMessage());
                userAdminIds = null; // 검색 실패시 null로 설정해서 조건 무시
            }
        }
        
        // Repository에서 복합 검색 수행
        if (userAdminIds != null && !userAdminIds.isEmpty()) {
            return orderRepository.findOrdersWithUserSearch(orderId, userAdminIds, minAmountInt, 
                    maxAmountInt, startDateTime, endDateTime, status, pageable);
        } else {
            return orderRepository.findOrdersWithoutUserSearch(orderId, minAmountInt, 
                    maxAmountInt, startDateTime, endDateTime, status, pageable);
        }
    }
    
    /**
     * Order 엔티티를 AdminOrderHistoryResponse로 변환
     */
    private AdminOrderHistoryResponse convertToAdminOrderResponse(Order order) {
        AdminOrderHistoryResponse response = new AdminOrderHistoryResponse();
        response.setOrderId(order.getOrderId());
        response.setOrderDate(order.getOrderDate());
        response.setOrderStatus(order.getOrderStatus().toString());
        response.setTotalProductCategory(order.getTotalProductCategory());
        response.setTotalProductQuantity(order.getTotalProductQuantity());
        response.setTotalPaidPrice(order.getTotalPaidPrice());
        
        // 사용자 정보 조회
        Optional<User> userOpt = userRepository.findByIdForAdmin(order.getIdForAdmin());
        if (userOpt.isPresent()) {
            User user = userOpt.get();
            response.setUserIdForAdmin(user.getIdForAdmin());
            response.setUserIdForUser(user.getIdForUser());
        }
        
        // 주문 상세 정보 조회
        List<AdminOrderHistoryResponse.OrderDetailResponse> detailResponses = new ArrayList<>();
        var orderDetails = orderDetailRepository.findByOrderIdAndIdForAdmin(
                order.getOrderId(), order.getIdForAdmin());
        
        for (var detail : orderDetails) {
            AdminOrderHistoryResponse.OrderDetailResponse detailResponse = 
                    new AdminOrderHistoryResponse.OrderDetailResponse();
            detailResponse.setIsbn(detail.getIsbn());
            detailResponse.setOrderItemQuantity(detail.getOrderItemQuantity());
            detailResponse.setEachProductPrice(detail.getEachProductPrice());
            detailResponse.setTotalProductPrice(detail.getTotalProductPrice());
            
            // 상품 정보 조회
            Optional<Product> productOpt = productRepository.findById(detail.getIsbn());
            if (productOpt.isPresent()) {
                Product product = productOpt.get();
                detailResponse.setProductTitle(product.getProductName());
                detailResponse.setAuthor(product.getAuthor());
                detailResponse.setImg(product.getImg());
            }
            
            detailResponses.add(detailResponse);
        }
        
        response.setOrderDetails(detailResponses);
        return response;
    }
    
    /**
     * 주문 상태 변경
     */
    public void updateOrderStatus(String orderId, String idForAdmin, String status) {
        try {
            // OrderId 복합키로 주문 조회
            var orderOpt = orderRepository.findById(new OrderId(orderId, idForAdmin));
            
            if (orderOpt.isEmpty()) {
                throw new RuntimeException("주문을 찾을 수 없습니다.");
            }
            
            var order = orderOpt.get();
            Order.OrderStatus oldStatus = order.getOrderStatus();
            
            // 상태 변경
            Order.OrderStatus newStatus = Order.OrderStatus.valueOf(status);
            order.setOrderStatus(newStatus);
            order.setUpdateDate(java.time.LocalDateTime.now());
            
            // 저장
            orderRepository.save(order);
            
            // 상품준비중으로 변경된 경우 재고 차감 처리
            if (newStatus == Order.OrderStatus.PREPARING_PRODUCT && oldStatus != Order.OrderStatus.PREPARING_PRODUCT) {
                processStockOutbound(orderId, idForAdmin);
            }
            
        } catch (IllegalArgumentException e) {
            throw new RuntimeException("잘못된 주문 상태입니다: " + status);
        } catch (Exception e) {
            throw new RuntimeException("주문 상태 변경 실패: " + e.getMessage());
        }
    }
    
    /**
     * 상품준비중 상태 변경 시 재고 차감 처리
     */
    private void processStockOutbound(String orderId, String idForAdmin) {
        try {
            // 주문 상세 정보 조회
            var orderDetails = orderDetailRepository.findByOrderIdAndIdForAdmin(orderId, idForAdmin);
            
            for (var orderDetail : orderDetails) {
                String isbn = orderDetail.getIsbn();
                Integer orderQuantity = orderDetail.getOrderItemQuantity();
                
                // 해당 상품의 최신 재고량 조회
                List<Integer> stockList = stockRepository.findCurrentStockListByIsbn(isbn, org.springframework.data.domain.PageRequest.of(0, 1));
                Integer beforeQuantity = stockList.isEmpty() ? 0 : stockList.get(0);
                
                // 재고 부족 체크
                if (beforeQuantity < orderQuantity) {
                    throw new RuntimeException("상품 " + isbn + "의 재고가 부족합니다. (현재재고: " + beforeQuantity + ", 주문수량: " + orderQuantity + ")");
                }
                
                // 출고 후 재고량 계산
                Integer afterQuantity = beforeQuantity - orderQuantity;
                
                // Stock 엔티티 생성 및 저장
                Stock stock = new Stock();
                stock.setIsbn(isbn);
                stock.setInOutType(Stock.InOutType.OUTBOUND);
                stock.setInOutQuantity(orderQuantity);
                stock.setBeforeQuantity(beforeQuantity);
                stock.setAfterQuantity(afterQuantity);
                stock.setUpdateDate(java.time.LocalDateTime.now());
                
                stockRepository.save(stock);
            }
            
        } catch (Exception e) {
            throw new RuntimeException("재고 처리 실패: " + e.getMessage());
        }
    }
}
