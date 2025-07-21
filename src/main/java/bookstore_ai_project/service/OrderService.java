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

/**
 * 주문 관리 비즈니스 로직 서비스
 *
 * 비즈니스 로직: 주문 생성, 주문 상품 리스트 조회, 관리자용 주문 내역 관리 등
 */
@Service
public class OrderService {
    /** 상품 데이터 접근 리포지토리 */
    @Autowired
    private ProductRepository productRepository;
    
    /** 주문 데이터 접근 리포지토리 */
    @Autowired
    private OrderRepository orderRepository;
    
    /** 주문 상세 데이터 접근 리포지토리 */
    @Autowired
    private OrderDetailRepository orderDetailRepository;
    
    /** 사용자 데이터 접근 리포지토리 */
    @Autowired
    private UserRepository userRepository;
    
    /** 재고 데이터 접근 리포지토리 */
    @Autowired
    private StockRepository stockRepository;

    /**
     * 주문 상품 리스트 조회
     *
     * 비즈니스 로직: 주문할 상품들의 상세 정보와 수량, 총 가격을 계산하여 주문 페이지에서 표시
     *
     * @param isbns 주문할 상품들의 ISBN 리스트
     * @param quantities 각 상품의 주문 수량 리스트
     * @param session HTTP 세션 (로그인 사용자 정보 확인용)
     * @return 주문 상품 리스트 (ProductSimpleResponse)
     */
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
     *
     * 비즈니스 로직: 관리자 페이지에서 페이징, 정렬, 검색 조건에 따라 주문 내역을 조회
     *
     * @param sort 정렬 기준
     * @param page 페이지 번호
     * @param size 페이지 크기
     * @param orderId 주문번호 검색어
     * @param userId 사용자 ID 검색어
     * @param minAmount 최소 주문 금액
     * @param maxAmount 최대 주문 금액
     * @param startDate 조회 시작 날짜
     * @param endDate 조회 종료 날짜
     * @param orderStatus 주문 상태
     * @return 주문 내역 페이지 응답 DTO
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
     *
     * 비즈니스 로직: 주문 검색 조건(주문번호, 사용자ID, 금액, 날짜, 상태 등) 입력 여부 확인
     *
     * @param orderId 주문번호
     * @param userId 사용자 ID
     * @param minAmount 최소 금액
     * @param maxAmount 최대 금액
     * @param startDate 시작 날짜
     * @param endDate 종료 날짜
     * @param orderStatus 주문 상태
     * @return 검색 조건 존재 여부
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
     *
     * 비즈니스 로직: 입력된 검색 조건에 따라 주문을 복합적으로 조회
     *
     * @param orderId 주문번호
     * @param userId 사용자 ID
     * @param minAmount 최소 금액
     * @param maxAmount 최대 금액
     * @param startDate 시작 날짜
     * @param endDate 종료 날짜
     * @param orderStatus 주문 상태
     * @param pageable 페이징 정보
     * @return 주문 페이지 객체
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
     *
     * 비즈니스 로직: 주문 엔티티를 관리자용 주문 내역 응답 DTO로 변환
     *
     * @param order 변환할 주문 엔티티
     * @return 관리자 주문 내역 응답 DTO
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
     *
     * 비즈니스 로직: 주문의 상태를 변경하고, 상품준비중으로 변경 시 재고 차감 처리
     *
     * @param orderId 주문 ID
     * @param idForAdmin 관리자용 사용자 ID
     * @param status 변경할 주문 상태
     * @return 없음
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
     *
     * 비즈니스 로직: 주문이 상품준비중 상태로 변경될 때 주문 상세 내역에 따라 재고를 차감
     *
     * @param orderId 주문 ID
     * @param idForAdmin 관리자용 사용자 ID
     * @return 없음
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
