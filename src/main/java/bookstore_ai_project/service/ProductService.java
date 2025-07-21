package bookstore_ai_project.service;

import bookstore_ai_project.dto.response.ProductSimpleResponse;
import bookstore_ai_project.dto.response.ProductListResponse;
import bookstore_ai_project.dto.response.ProductListPageResponse;
import bookstore_ai_project.repository.ProductRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;

import bookstore_ai_project.entity.Product;
import bookstore_ai_project.repository.ProductReviewRepository;
import bookstore_ai_project.entity.ProductReview;
import bookstore_ai_project.repository.StockRepository;
import bookstore_ai_project.repository.ProductHistoryRepository;
import bookstore_ai_project.entity.Stock;
import bookstore_ai_project.entity.ProductHistory;
import org.springframework.data.jpa.domain.Specification;
import jakarta.persistence.criteria.Predicate;

/**
 * 상품 관리 비즈니스 로직 서비스
 *
 * 비즈니스 로직: 도서 검색, 상품 리스트 조회, 인기상품/신착/베스트셀러 조회, 상품 리뷰 관리 등
 */
@Service
public class ProductService {
    /** 상품 데이터 접근 리포지토리 */
    @Autowired
    private ProductRepository productRepository;

    /** 상품 리뷰 데이터 접근 리포지토리 */
    @Autowired
    private ProductReviewRepository productReviewRepository;

    /** 재고 데이터 접근 리포지토리 */
    @Autowired
    private StockRepository stockRepository;

    /** 상품 이력 데이터 접근 리포지토리 */
    @Autowired
    private ProductHistoryRepository productHistoryRepository;

    /**
     * 인기 상품 Top N 조회
     *
     * 비즈니스 로직: 검색 횟수 기준으로 인기 상품을 내림차순 정렬하여 상위 N개 반환
     *
     * @param limit 조회할 상품 개수
     * @return 인기 상품 리스트 (ISBN, 상품명, 이미지, 저자, 가격, 검색횟수 포함)
     */
    public List<ProductSimpleResponse> getPopularProducts(int limit) {
        return productRepository.findTopPopularProducts(PageRequest.of(0, limit)).stream()
                .map(arr -> new ProductSimpleResponse(
                        (String) arr[0], // isbn
                        (String) arr[1], // productName
                        (String) arr[2], // img
                        (String) arr[3], // author
                        (Integer) arr[5],// searchCount
                        null,            // regDate
                        null,            // productQuantity
                        (Integer) arr[4] // price
                )).collect(Collectors.toList());
    }

    /**
     * 신상품 Top N 조회
     *
     * 비즈니스 로직: 등록일 기준으로 최신 상품들을 내림차순 정렬하여 상위 N개 반환
     *
     * @param limit 조회할 상품 개수
     * @return 신상품 리스트 (ISBN, 상품명, 이미지, 저자, 가격, 등록일 포함)
     */
    public List<ProductSimpleResponse> getNewProducts(int limit) {
        return productRepository.findTopNewProducts(PageRequest.of(0, limit)).stream()
                .map(arr -> new ProductSimpleResponse(
                        (String) arr[0], // isbn
                        (String) arr[1], // productName
                        (String) arr[2], // img
                        (String) arr[3], // author
                        null,            // searchCount
                        (java.time.LocalDateTime) arr[5], // regDate
                        null,            // productQuantity
                        (Integer) arr[4] // price
                )).collect(Collectors.toList());
    }

    /**
     * 상품 검색 횟수 증가
     *
     * 비즈니스 로직: 상품 상세 페이지 진입 시 검색 횟수를 1 증가시켜 인기도 통계에 반영
     *
     * @param isbn 검색 횟수를 증가할 상품 ISBN
     */
    @Transactional
    public void increaseSearchCount(String isbn) {
        productRepository.increaseSearchCount(isbn);
    }

    /**
     * 기간별 베스트셀러 조회 (주간/월간/연간)
     *
     * 비즈니스 로직: 지정된 기간 내 주문 수량이 많은 상품들을 베스트셀러로 선정하여 반환
     *
     * @param startDate 조회 시작 날짜
     * @param endDate 조회 종료 날짜
     * @param limit 조회할 상품 개수
     * @return 베스트셀러 리스트 (ISBN, 상품명, 이미지, 저자, 가격, 주문수량 포함)
     */
    public java.util.List<ProductSimpleResponse> getBestsellerByPeriod(LocalDateTime startDate, LocalDateTime endDate, int limit) {
        java.util.List<Object[]> result = productRepository.findBestsellerByPeriod(startDate, endDate, PageRequest.of(0, limit));
        return result.stream().map(arr -> {
            String isbn = (String) arr[0];
            Long totalQuantity = ((Number) arr[1]).longValue();
            Product product = productRepository.findById(isbn).orElse(null);
            if (product == null) return null;
            return new ProductSimpleResponse(
                product.getIsbn(),
                product.getProductName(),
                product.getImg(),
                product.getAuthor(),
                totalQuantity.intValue(), // searchCount에 판매수량 임시 저장
                product.getRegDate(),
                null, // productQuantity
                product.getPrice() // price
            );
        }).filter(java.util.Objects::nonNull).toList();
    }

    /**
     * 상품 상세 정보 조회
     *
     * 비즈니스 로직: ISBN으로 상품의 상세 정보를 조회
     *
     * @param isbn 조회할 상품의 ISBN
     * @return 상품 엔티티
     */
    public Product getProductDetailByIsbn(String isbn) {
        return productRepository.findByIsbn(isbn);
    }

    /**
     * 상품 리뷰 리스트 조회
     *
     * 비즈니스 로직: ISBN으로 해당 상품의 모든 리뷰를 조회
     *
     * @param isbn 상품 ISBN
     * @return 상품 리뷰 리스트
     */
    public java.util.List<ProductReview> getProductReviewsByIsbn(String isbn) {
        return productReviewRepository.findAllByIsbn(isbn);
    }

    /**
     * 상품 리뷰 리스트 조회 (최신순, soft delete 제외, 페이지네이션, 닉네임 포함)
     *
     * 비즈니스 로직: ISBN으로 soft delete 제외, 최신순, 닉네임 포함, 페이지네이션된 리뷰 리스트 조회
     *
     * @param isbn 상품 ISBN
     * @param page 페이지 번호
     * @param size 페이지 크기
     * @return 리뷰+닉네임 리스트 및 페이징 정보(Map)
     */
    public java.util.Map<String, Object> getProductReviewsWithNicknameByIsbnPaged(String isbn, int page, int size) {
        if (size <= 0) size = 10;
        org.springframework.data.domain.Pageable pageable = org.springframework.data.domain.PageRequest.of(page, size);
        var reviewsWithNickname = productReviewRepository.findByIsbnWithUserNicknameAndDeleteDateIsNull(isbn, pageable);
        
        java.util.List<java.util.Map<String, Object>> reviewList = new java.util.ArrayList<>();
        
        for (Object[] objArray : reviewsWithNickname.getContent()) {
            ProductReview review = (ProductReview) objArray[0];
            String nickname = (String) objArray[1];
            
            java.util.Map<String, Object> reviewData = new java.util.HashMap<>();
            reviewData.put("review", review);
            reviewData.put("nickname", nickname);
            reviewList.add(reviewData);
        }
        
        java.util.Map<String, Object> result = new java.util.HashMap<>();
        result.put("reviews", reviewList);
        result.put("totalPages", reviewsWithNickname.getTotalPages());
        result.put("totalElements", reviewsWithNickname.getTotalElements());
        result.put("currentPage", page);
        
        return result;
    }
    
    /**
     * 기존 메서드 유지 (다른 곳에서 사용 중일 수 있음)
     *
     * 비즈니스 로직: ISBN으로 soft delete 제외, 최신순, 페이지네이션된 리뷰 리스트 조회
     *
     * @param isbn 상품 ISBN
     * @param page 페이지 번호
     * @param size 페이지 크기
     * @return 상품 리뷰 페이지 객체
     */
    public org.springframework.data.domain.Page<ProductReview> getProductReviewsByIsbnPaged(String isbn, int page, int size) {
        org.springframework.data.domain.Pageable pageable = org.springframework.data.domain.PageRequest.of(page, size, org.springframework.data.domain.Sort.by("regDate").descending());
        return productReviewRepository.findByIsbnAndDeleteDateIsNull(isbn, pageable);
    }

    /**
     * 소분류별 상품 목록 조회 (페이지네이션, 정렬 포함)
     *
     * 비즈니스 로직: 소분류 카테고리별로 정렬, 페이지네이션 조건에 따라 상품 목록 조회
     *
     * @param lowCategoryId 소분류 카테고리 ID
     * @param sort 정렬 기준
     * @param page 페이지 번호
     * @param size 페이지 크기
     * @param title 제목 검색어
     * @param author 저자 검색어
     * @param publisher 출판사 검색어
     * @return 상품 리스트 페이지 응답 DTO
     */
    public ProductListPageResponse getProductsByLowCategory(Integer lowCategoryId, String sort, int page, int size, String title, String author, String publisher) {
        org.springframework.data.domain.PageRequest pageRequest;
        if (sort.equals("price_low")) {
            pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("price").ascending());
        } else if (sort.equals("price_high")) {
            pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("price").descending());
        } else if (sort.equals("rating")) {
            pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("rate").descending());
        } else if (sort.equals("latest")) {
            pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("regDate").descending());
        } else if (sort.equals("oldest")) {
            pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("regDate").ascending());
        } else if (sort.equals("title_asc")) {
            pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("productName").ascending());
        } else if (sort.equals("title_desc")) {
            pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("productName").descending());
        } else {
            // 판매량순만 별도 처리
            if (sort.equals("sales")) {
                // 판매량순은 기존 쿼리 사용, 검색조건 미지원
                pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size);
                List<ProductListResponse> products = productRepository.findProductsByLowCategoryOrderBySalesDesc(lowCategoryId, pageRequest)
                    .stream().map(this::convertToProductListResponseFromObjectArray).collect(Collectors.toList());
                long totalItems = productRepository.countByLowCategory(lowCategoryId);
                int totalPages = (int) Math.ceil((double) totalItems / size);
                return new ProductListPageResponse(products, page, totalPages, totalItems, size, null, lowCategoryId);
            } else {
                pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size);
            }
        }

        // Specification 동적 검색
        Specification<Product> spec = (root, query, cb) -> {
            Predicate p = cb.equal(root.get("lowCategory"), lowCategoryId);
            if (title != null && !title.isBlank()) {
                p = cb.and(p, cb.like(root.get("productName"), "%" + title + "%"));
            }
            if (author != null && !author.isBlank()) {
                p = cb.and(p, cb.like(root.get("author"), "%" + author + "%"));
            }
            if (publisher != null && !publisher.isBlank()) {
                p = cb.and(p, cb.like(root.get("publisher"), "%" + publisher + "%"));
            }
            return p;
        };
        List<ProductListResponse> products = productRepository.findAll(spec, pageRequest)
            .stream().map(this::convertToProductListResponse).collect(Collectors.toList());
        long totalItems = productRepository.count(spec);
        int totalPages = (int) Math.ceil((double) totalItems / size);
        return new ProductListPageResponse(products, page, totalPages, totalItems, size, null, lowCategoryId);
    }
    
    /**
     * 전체 상품 OR 검색 (제목/저자/출판사/ISBN 중 하나라도 포함)
     *
     * 비즈니스 로직: 검색어가 제목, 저자, 출판사, ISBN 중 하나라도 포함되면 해당 상품 반환
     *
     * @param q 검색어
     * @param sort 정렬 기준
     * @param page 페이지 번호
     * @param size 페이지 크기
     * @return 상품 리스트 페이지 응답 DTO
     */
    public ProductListPageResponse searchProductsOr(String q, String sort, int page, int size) {
        org.springframework.data.domain.PageRequest pageRequest = getPageRequest(sort, page, size);
        Specification<Product> spec = (root, query, cb) -> {
            if (q == null || q.isBlank()) return cb.conjunction();
            String likeQ = "%" + q + "%";
            return cb.or(
                cb.like(root.get("productName"), likeQ),
                cb.like(root.get("author"), likeQ),
                cb.like(root.get("publisher"), likeQ),
                cb.like(root.get("isbn"), likeQ)
            );
        };
        List<ProductListResponse> products = productRepository.findAll(spec, pageRequest)
            .stream().map(this::convertToProductListResponse).collect(java.util.stream.Collectors.toList());
        long totalItems = productRepository.count(spec);
        int totalPages = (int) Math.ceil((double) totalItems / size);
        return new ProductListPageResponse(products, page, totalPages, totalItems, size, null, null);
    }

    /**
     * 전체 상품 AND 검색 (제목+저자+출판사 모두 만족)
     *
     * 비즈니스 로직: 제목, 저자, 출판사 모두 일치하는 상품만 반환
     *
     * @param bookTitle 제목
     * @param author 저자
     * @param publisher 출판사
     * @param sort 정렬 기준
     * @param page 페이지 번호
     * @param size 페이지 크기
     * @return 상품 리스트 페이지 응답 DTO
     */
    public ProductListPageResponse searchProductsAnd(String bookTitle, String author, String publisher, String sort, int page, int size) {
        org.springframework.data.domain.PageRequest pageRequest = getPageRequest(sort, page, size);
        Specification<Product> spec = (root, query, cb) -> {
            var p = cb.conjunction();
            if (bookTitle != null && !bookTitle.isBlank()) {
                p = cb.and(p, cb.like(root.get("productName"), "%" + bookTitle + "%"));
            }
            if (author != null && !author.isBlank()) {
                p = cb.and(p, cb.like(root.get("author"), "%" + author + "%"));
            }
            if (publisher != null && !publisher.isBlank()) {
                p = cb.and(p, cb.like(root.get("publisher"), "%" + publisher + "%"));
            }
            return p;
        };
        List<ProductListResponse> products = productRepository.findAll(spec, pageRequest)
            .stream().map(this::convertToProductListResponse).collect(java.util.stream.Collectors.toList());
        long totalItems = productRepository.count(spec);
        int totalPages = (int) Math.ceil((double) totalItems / size);
        return new ProductListPageResponse(products, page, totalPages, totalItems, size, null, null);
    }

    /**
     * 일반검색 결과에서 추가 필터링 (q + bookTitle/author/publisher)
     *
     * 비즈니스 로직: 일반검색 결과에서 추가적으로 제목, 저자, 출판사로 필터링
     *
     * @param q 검색어
     * @param bookTitle 제목
     * @param author 저자
     * @param publisher 출판사
     * @param sort 정렬 기준
     * @param page 페이지 번호
     * @param size 페이지 크기
     * @return 상품 리스트 페이지 응답 DTO
     */
    public ProductListPageResponse searchProductsAdvanced(String q, String bookTitle, String author, String publisher, String sort, int page, int size) {
        // 판매량순인 경우 별도 처리
        if ("sales".equals(sort)) {
            org.springframework.data.domain.PageRequest pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size);
            List<ProductListResponse> products;
            
            // 검색 조건이 있는 경우와 없는 경우 구분
            if ((bookTitle != null && !bookTitle.isBlank()) || (author != null && !author.isBlank()) || (publisher != null && !publisher.isBlank())) {
                products = productRepository.findAllProductsOrderBySalesDescWithSearch(
                    (bookTitle != null && !bookTitle.isBlank()) ? bookTitle : null,
                    (author != null && !author.isBlank()) ? author : null,
                    (publisher != null && !publisher.isBlank()) ? publisher : null,
                    pageRequest
                ).stream().map(this::convertToProductListResponseFromObjectArray).collect(java.util.stream.Collectors.toList());
            } else {
                products = productRepository.findAllProductsOrderBySalesDesc(pageRequest)
                    .stream().map(this::convertToProductListResponseFromObjectArray).collect(java.util.stream.Collectors.toList());
            }
            
            long totalItems = productRepository.count();
            int totalPages = (int) Math.ceil((double) totalItems / size);
            return new ProductListPageResponse(products, page, totalPages, totalItems, size, null, null);
        }
        
        // 다른 정렬의 경우 기존 로직
        org.springframework.data.domain.PageRequest pageRequest = getPageRequest(sort, page, size);
        Specification<Product> spec = (root, query, cb) -> {
            var p = cb.conjunction();
            
            // 먼저 일반검색 조건 적용 (q가 있으면)
            if (q != null && !q.isBlank()) {
                String likeQ = "%" + q + "%";
                p = cb.and(p, cb.or(
                    cb.like(root.get("productName"), likeQ),
                    cb.like(root.get("author"), likeQ),
                    cb.like(root.get("publisher"), likeQ),
                    cb.like(root.get("isbn"), likeQ)
                ));
            }
            
            // 추가 필터링 조건들
            if (bookTitle != null && !bookTitle.isBlank()) {
                p = cb.and(p, cb.like(root.get("productName"), "%" + bookTitle + "%"));
            }
            if (author != null && !author.isBlank()) {
                p = cb.and(p, cb.like(root.get("author"), "%" + author + "%"));
            }
            if (publisher != null && !publisher.isBlank()) {
                p = cb.and(p, cb.like(root.get("publisher"), "%" + publisher + "%"));
            }
            return p;
        };
        List<ProductListResponse> products = productRepository.findAll(spec, pageRequest)
            .stream().map(this::convertToProductListResponse).collect(java.util.stream.Collectors.toList());
        long totalItems = productRepository.count(spec);
        int totalPages = (int) Math.ceil((double) totalItems / size);
        return new ProductListPageResponse(products, page, totalPages, totalItems, size, null, null);
    }

    /**
     * 정렬/페이지네이션 공통 처리
     *
     * 비즈니스 로직: 정렬 기준과 페이지 정보를 PageRequest로 변환
     *
     * @param sort 정렬 기준
     * @param page 페이지 번호
     * @param size 페이지 크기
     * @return PageRequest 객체
     */
    private org.springframework.data.domain.PageRequest getPageRequest(String sort, int page, int size) {
        if (sort.equals("price_low")) {
            return org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("price").ascending());
        } else if (sort.equals("price_high")) {
            return org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("price").descending());
        } else if (sort.equals("rating")) {
            return org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("rate").descending());
        } else if (sort.equals("latest")) {
            return org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("regDate").descending());
        } else if (sort.equals("oldest")) {
            return org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("regDate").ascending());
        } else if (sort.equals("title_asc")) {
            return org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("productName").ascending());
        } else if (sort.equals("title_desc")) {
            return org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("productName").descending());
        } else {
            return org.springframework.data.domain.PageRequest.of(page - 1, size);
        }
    }

    /**
     * Product 엔티티를 ProductListResponse로 변환
     *
     * 비즈니스 로직: Product 엔티티를 상품 리스트 응답 DTO로 변환
     *
     * @param product 변환할 상품 엔티티
     * @return 상품 리스트 응답 DTO
     */
    private ProductListResponse convertToProductListResponse(Product product) {
        // 현재 재고량 조회
        List<Integer> stockList = stockRepository.findCurrentStockListByIsbn(product.getIsbn(), org.springframework.data.domain.PageRequest.of(0, 1));
        Integer currentStock = stockList.isEmpty() ? 0 : stockList.get(0);
        
        System.out.println("상품 변환: " + product.getIsbn() + " - " + product.getProductName() + " - 재고: " + currentStock);
        
        return new ProductListResponse(
            product.getIsbn(),
            product.getProductName(),
            product.getAuthor(),
            product.getPublisher(),
            product.getPrice(),
            product.getRate(),
            product.getImg(),
            product.getRegDate(),
            0L, // salesCount는 기본값 0
            product.getSalesStatus() != null ? product.getSalesStatus().name() : null, // salesStatus
            currentStock // 현재 재고량
        );
    }
    
    /**
     * Object[] 배열을 ProductListResponse로 변환 (판매량순 조회용)
     *
     * 비즈니스 로직: 판매량순 native 쿼리 결과(Object[])를 상품 리스트 응답 DTO로 변환
     *
     * @param arr 변환할 Object[]
     * @return 상품 리스트 응답 DTO
     */
    private ProductListResponse convertToProductListResponseFromObjectArray(Object[] arr) {
        // arr[9]에 salesStatus가 있음
        
        // Timestamp를 LocalDateTime으로 변환
        java.time.LocalDateTime regDate = null;
        if (arr[7] != null) {
            if (arr[7] instanceof java.sql.Timestamp) {
                regDate = ((java.sql.Timestamp) arr[7]).toLocalDateTime();
            } else if (arr[7] instanceof java.time.LocalDateTime) {
                regDate = (java.time.LocalDateTime) arr[7];
            }
        }
        
        // 현재 재고량 조회
        String isbn = (String) arr[0];
        List<Integer> stockList = stockRepository.findCurrentStockListByIsbn(isbn, org.springframework.data.domain.PageRequest.of(0, 1));
        Integer currentStock = stockList.isEmpty() ? 0 : stockList.get(0);
        
        return new ProductListResponse(
            isbn, // isbn
            (String) arr[1], // productName
            (String) arr[2], // author
            (String) arr[3], // publisher
            (Integer) arr[4], // price
            (java.math.BigDecimal) arr[5], // rate
            (String) arr[6], // img
            regDate, // regDate
            ((Number) arr[8]).longValue(), // salesCount
            arr[9] != null ? arr[9].toString() : null, // salesStatus
            currentStock // 현재 재고량
        );
    }

    /**
     * 전체 상품 개수 조회
     *
     * 비즈니스 로직: 전체 상품의 개수를 반환
     *
     * @return 전체 상품 개수(Long)
     */
    public long getTotalProductCount() {
        return productRepository.count();
    }

    /**
     * 관리자용 상세검색 (판매상태, 날짜 범위 포함)
     *
     * 비즈니스 로직: 관리자 페이지에서 판매상태, 날짜 범위 등 다양한 조건으로 상품을 상세 검색
     *
     * @param q 통합 검색어
     * @param title 제목 검색어
     * @param author 저자 검색어
     * @param publisher 출판사 검색어
     * @param sort 정렬 기준
     * @param page 페이지 번호
     * @param size 페이지 크기
     * @param salesStatus 판매 상태
     * @param startDate 시작 날짜
     * @param endDate 종료 날짜
     * @return 상품 리스트 페이지 응답 DTO
     */
    public ProductListPageResponse searchProductsAdvanced(String q, String title, String author, String publisher, 
                                                         String sort, int page, int size, String salesStatus, 
                                                         String startDate, String endDate) {
        
        System.out.println("=== 전체상품 조회 시작 ===");
        System.out.println("상품 검색 파라미터: q=" + q + ", title=" + title + ", author=" + author + 
                          ", publisher=" + publisher + ", salesStatus=" + salesStatus + 
                          ", startDate=" + startDate + ", endDate=" + endDate);
        System.out.println("정렬: " + sort + ", 페이지: " + page + ", 크기: " + size);
        // 판매량순인 경우에는 필터링이 복잡하므로 Specification으로 처리
        if ("sales".equals(sort)) {
            // 판매량순은 native query를 사용해야 하지만, 필터링이 있으면 Specification 사용
            if ((salesStatus != null && !salesStatus.isBlank()) || 
                (startDate != null && !startDate.isBlank()) || 
                (endDate != null && !endDate.isBlank())) {
                // 필터링이 있으면 기본 정렬로 처리
                org.springframework.data.domain.PageRequest pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("regDate").descending());
                
                Specification<Product> spec = (root, queryObj, cb) -> {
                    var p = cb.conjunction();
                    
                    // 일반검색 조건 적용
                    if (q != null && !q.isBlank()) {
                        String likeQ = "%" + q + "%";
                        p = cb.and(p, cb.or(
                            cb.like(root.get("productName"), likeQ),
                            cb.like(root.get("author"), likeQ),
                            cb.like(root.get("publisher"), likeQ),
                            cb.like(root.get("isbn"), likeQ)
                        ));
                    }
                    
                    // 추가 필터링 조건들
                    if (title != null && !title.isBlank()) {
                        p = cb.and(p, cb.like(root.get("productName"), "%" + title + "%"));
                    }
                    if (author != null && !author.isBlank()) {
                        p = cb.and(p, cb.like(root.get("author"), "%" + author + "%"));
                    }
                    if (publisher != null && !publisher.isBlank()) {
                        p = cb.and(p, cb.like(root.get("publisher"), "%" + publisher + "%"));
                    }
                    
                    // 판매상태 필터링
                    if (salesStatus != null && !salesStatus.isBlank()) {
                        Product.SalesStatus enumStatus = convertKoreanToSalesStatus(salesStatus);
                        if (enumStatus != null) {
                            p = cb.and(p, cb.equal(root.get("salesStatus"), enumStatus));
                        }
                    }
                    
                    // 날짜 범위 필터링
                    if (startDate != null && !startDate.isBlank()) {
                        try {
                            LocalDateTime startDateTime = LocalDateTime.parse(startDate + "T00:00:00");
                            p = cb.and(p, cb.greaterThanOrEqualTo(root.get("regDate"), startDateTime));
                        } catch (Exception e) {
                            // 날짜 파싱 오류 무시
                        }
                    }
                    if (endDate != null && !endDate.isBlank()) {
                        try {
                            LocalDateTime endDateTime = LocalDateTime.parse(endDate + "T23:59:59");
                            p = cb.and(p, cb.lessThanOrEqualTo(root.get("regDate"), endDateTime));
                        } catch (Exception e) {
                            // 날짜 파싱 오류 무시
                        }
                    }
                    
                    return p;
                };
                
                List<ProductListResponse> products = productRepository.findAll(spec, pageRequest)
                    .stream().map(this::convertToProductListResponse).collect(java.util.stream.Collectors.toList());
                long totalItems = productRepository.count(spec);
                int totalPages = (int) Math.ceil((double) totalItems / size);
                return new ProductListPageResponse(products, page, totalPages, totalItems, size, null, null);
            } else {
                // 필터링이 없으면 native query 사용
                org.springframework.data.domain.PageRequest pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size);
                List<ProductListResponse> products;
                
                if ((title != null && !title.isBlank()) || (author != null && !author.isBlank()) || (publisher != null && !publisher.isBlank())) {
                    products = productRepository.findAllProductsOrderBySalesDescWithSearch(
                        (title != null && !title.isBlank()) ? title : null,
                        (author != null && !author.isBlank()) ? author : null,
                        (publisher != null && !publisher.isBlank()) ? publisher : null,
                        pageRequest
                    ).stream().map(this::convertToProductListResponseFromObjectArray).collect(java.util.stream.Collectors.toList());
                    
                    // 검색 조건이 있으면 전체 개수를 다시 계산해야 함
                    long totalItems = productRepository.countAllProductsWithSearch(
                        (title != null && !title.isBlank()) ? title : null,
                        (author != null && !author.isBlank()) ? author : null,
                        (publisher != null && !publisher.isBlank()) ? publisher : null
                    );
                    int totalPages = (int) Math.ceil((double) totalItems / size);
                    return new ProductListPageResponse(products, page, totalPages, totalItems, size, null, null);
                } else {
                    products = productRepository.findAllProductsOrderBySalesDesc(pageRequest)
                        .stream().map(this::convertToProductListResponseFromObjectArray).collect(java.util.stream.Collectors.toList());
                    
                    long totalItems = productRepository.count();
                    int totalPages = (int) Math.ceil((double) totalItems / size);
                    return new ProductListPageResponse(products, page, totalPages, totalItems, size, null, null);
                }
            }
        }
            
        // 전체상품 조건 분기: 모든 검색 조건이 비어있으면 전체 상품 반환
        if ((q == null || q.isBlank()) && (title == null || title.isBlank()) && 
            (author == null || author.isBlank()) && (publisher == null || publisher.isBlank()) &&
            (salesStatus == null || salesStatus.isBlank()) && 
            (startDate == null || startDate.isBlank()) && (endDate == null || endDate.isBlank())) {
            org.springframework.data.domain.PageRequest pageRequest = getPageRequest(sort, page, size);
            org.springframework.data.domain.Page<Product> pageResult = productRepository.findAll(pageRequest);
            java.util.List<ProductListResponse> products = pageResult.getContent().stream()
                .map(this::convertToProductListResponse)
                .collect(java.util.stream.Collectors.toList());
            long totalItems = pageResult.getTotalElements();
            int totalPages = pageResult.getTotalPages();
            return new ProductListPageResponse(products, page, totalPages, totalItems, size, null, null);
        }

        // 다른 정렬의 경우 Specification 사용
        org.springframework.data.domain.PageRequest pageRequest = getPageRequest(sort, page, size);
        Specification<Product> spec = (root, query, cb) -> {
            var p = cb.conjunction();
            
            // 먼저 일반검색 조건 적용 (q가 있으면)
            if (q != null && !q.isBlank()) {
                String likeQ = "%" + q + "%";
                p = cb.and(p, cb.or(
                    cb.like(root.get("productName"), likeQ),
                    cb.like(root.get("author"), likeQ),
                    cb.like(root.get("publisher"), likeQ),
                    cb.like(root.get("isbn"), likeQ)
                ));
            }
            
            // 추가 필터링 조건들
            if (title != null && !title.isBlank()) {
                p = cb.and(p, cb.like(root.get("productName"), "%" + title + "%"));
            }
            if (author != null && !author.isBlank()) {
                p = cb.and(p, cb.like(root.get("author"), "%" + author + "%"));
            }
            if (publisher != null && !publisher.isBlank()) {
                p = cb.and(p, cb.like(root.get("publisher"), "%" + publisher + "%"));
            }
            
            // 판매상태 필터링
            if (salesStatus != null && !salesStatus.isBlank()) {
                Product.SalesStatus enumStatus = convertKoreanToSalesStatus(salesStatus);
                if (enumStatus != null) {
                    p = cb.and(p, cb.equal(root.get("salesStatus"), enumStatus));
                }
            }
            
            // 날짜 범위 필터링
            if (startDate != null && !startDate.isBlank()) {
                try {
                    LocalDateTime startDateTime = LocalDateTime.parse(startDate + "T00:00:00");
                    p = cb.and(p, cb.greaterThanOrEqualTo(root.get("regDate"), startDateTime));
                } catch (Exception e) {
                    // 날짜 파싱 오류 무시
                }
            }
            if (endDate != null && !endDate.isBlank()) {
                try {
                    LocalDateTime endDateTime = LocalDateTime.parse(endDate + "T23:59:59");
                    p = cb.and(p, cb.lessThanOrEqualTo(root.get("regDate"), endDateTime));
                } catch (Exception e) {
                    // 날짜 파싱 오류 무시
                }
            }
            
            return p;
        };
        
        List<ProductListResponse> products = productRepository.findAll(spec, pageRequest)
            .stream().map(this::convertToProductListResponse).collect(java.util.stream.Collectors.toList());
        long totalItems = productRepository.count(spec);
        int totalPages = (int) Math.ceil((double) totalItems / size);
        return new ProductListPageResponse(products, page, totalPages, totalItems, size, null, null);
    }

    /**
     * 관리자용 카테고리별 상세검색 (판매상태, 날짜 범위 포함)
     *
     * 비즈니스 로직: 관리자 페이지에서 소분류별로 판매상태, 날짜 범위 등 다양한 조건으로 상품을 상세 검색
     *
     * @param lowCategoryId 소분류 카테고리 ID
     * @param sort 정렬 기준
     * @param page 페이지 번호
     * @param size 페이지 크기
     * @param title 제목 검색어
     * @param author 저자 검색어
     * @param publisher 출판사 검색어
     * @param salesStatus 판매 상태
     * @param startDate 시작 날짜
     * @param endDate 종료 날짜
     * @return 상품 리스트 페이지 응답 DTO
     */
    public ProductListPageResponse getProductsByLowCategoryAdvanced(Integer lowCategoryId, String sort, int page, int size,
                                                                   String title, String author, String publisher,
                                                                   String salesStatus, String startDate, String endDate) {
        org.springframework.data.domain.PageRequest pageRequest;
        if (sort.equals("price_low")) {
            pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("price").ascending());
        } else if (sort.equals("price_high")) {
            pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("price").descending());
        } else if (sort.equals("rating")) {
            pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("rate").descending());
        } else if (sort.equals("latest")) {
            pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("regDate").descending());
        } else if (sort.equals("oldest")) {
            pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("regDate").ascending());
        } else if (sort.equals("title_asc")) {
            pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("productName").ascending());
        } else if (sort.equals("title_desc")) {
            pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("productName").descending());
        } else {
            // 판매량순만 별도 처리
            if (sort.equals("sales")) {
                // 필터링이 있으면 Specification 사용
                if ((salesStatus != null && !salesStatus.isBlank()) || 
                    (startDate != null && !startDate.isBlank()) || 
                    (endDate != null && !endDate.isBlank())) {
                    pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size, org.springframework.data.domain.Sort.by("regDate").descending());
                } else {
                    // 필터링이 없으면 native query 사용
                    pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size);
                    List<ProductListResponse> products = productRepository.findProductsByLowCategoryOrderBySalesDesc(lowCategoryId, pageRequest)
                        .stream().map(this::convertToProductListResponseFromObjectArray).collect(Collectors.toList());
                    
                    long totalItems = productRepository.countByLowCategory(lowCategoryId);
                    int totalPages = (int) Math.ceil((double) totalItems / size);
                    return new ProductListPageResponse(products, page, totalPages, totalItems, size, null, lowCategoryId);
                }
            } else {
                pageRequest = org.springframework.data.domain.PageRequest.of(page - 1, size);
            }
        }

        // Specification 동적 검색
        Specification<Product> spec = (root, query, cb) -> {
            Predicate p = cb.equal(root.get("lowCategory"), lowCategoryId);
            if (title != null && !title.isBlank()) {
                p = cb.and(p, cb.like(root.get("productName"), "%" + title + "%"));
            }
            if (author != null && !author.isBlank()) {
                p = cb.and(p, cb.like(root.get("author"), "%" + author + "%"));
            }
            if (publisher != null && !publisher.isBlank()) {
                p = cb.and(p, cb.like(root.get("publisher"), "%" + publisher + "%"));
            }
            
            // 판매상태 필터링
            if (salesStatus != null && !salesStatus.isBlank()) {
                Product.SalesStatus enumStatus = convertKoreanToSalesStatus(salesStatus);
                if (enumStatus != null) {
                    p = cb.and(p, cb.equal(root.get("salesStatus"), enumStatus));
                }
            }
            
            // 날짜 범위 필터링
            if (startDate != null && !startDate.isBlank()) {
                try {
                    LocalDateTime startDateTime = LocalDateTime.parse(startDate + "T00:00:00");
                    p = cb.and(p, cb.greaterThanOrEqualTo(root.get("regDate"), startDateTime));
                } catch (Exception e) {
                    // 날짜 파싱 오류 무시
                }
            }
            if (endDate != null && !endDate.isBlank()) {
                try {
                    LocalDateTime endDateTime = LocalDateTime.parse(endDate + "T23:59:59");
                    p = cb.and(p, cb.lessThanOrEqualTo(root.get("regDate"), endDateTime));
                } catch (Exception e) {
                    // 날짜 파싱 오류 무시
                }
            }
            
            return p;
        };
        List<ProductListResponse> products = productRepository.findAll(spec, pageRequest)
            .stream().map(this::convertToProductListResponse).collect(Collectors.toList());
        long totalItems = productRepository.count(spec);
        int totalPages = (int) Math.ceil((double) totalItems / size);
        return new ProductListPageResponse(products, page, totalPages, totalItems, size, null, lowCategoryId);
    }
    
    /**
     * 관리자 필터링 적용 (판매량순에서 사용)
     *
     * 비즈니스 로직: 판매량순 native 쿼리 결과에 관리자용 필터(상태, 날짜 등) 적용
     *
     * @param products 상품 리스트
     * @param salesStatus 판매 상태
     * @param startDate 시작 날짜
     * @param endDate 종료 날짜
     * @return 필터링된 상품 리스트
     */
    private List<ProductListResponse> applyAdminFilters(List<ProductListResponse> products, String salesStatus, String startDate, String endDate) {
        return products.stream().filter(product -> {
            // 판매상태 필터링
            if (salesStatus != null && !salesStatus.isBlank()) {
                Product.SalesStatus enumStatus = convertKoreanToSalesStatus(salesStatus);
                if (enumStatus != null) {
                    if (!enumStatus.name().equals(product.getSalesStatus())) {
                        return false;
                    }
                }
            }
            
            // 날짜 범위 필터링
            if (startDate != null && !startDate.isBlank()) {
                try {
                    LocalDateTime startDateTime = LocalDateTime.parse(startDate + "T00:00:00");
                    if (product.getRegDate() != null && product.getRegDate().isBefore(startDateTime)) {
                        return false;
                    }
                } catch (Exception e) {
                    // 날짜 파싱 오류 무시
                }
            }
            if (endDate != null && !endDate.isBlank()) {
                try {
                    LocalDateTime endDateTime = LocalDateTime.parse(endDate + "T23:59:59");
                    if (product.getRegDate() != null && product.getRegDate().isAfter(endDateTime)) {
                        return false;
                    }
                } catch (Exception e) {
                    // 날짜 파싱 오류 무시
                }
            }
            
            return true;
        }).collect(Collectors.toList());
    }
    
    /**
     * 영문 판매상태를 enum으로 변환
     *
     * 비즈니스 로직: 영문 판매상태 문자열을 SalesStatus enum으로 변환
     *
     * @param status 영문 판매상태 문자열
     * @return SalesStatus enum 또는 null
     */
    private Product.SalesStatus convertKoreanToSalesStatus(String status) {
        if (status == null || status.isBlank()) {
            return null;
        }
        
        try {
            return Product.SalesStatus.valueOf(status);
        } catch (IllegalArgumentException e) {
            return null;
        }
    }

    /**
     * 상품 입고 처리
     *
     * 비즈니스 로직: 상품의 재고를 입고 수량만큼 증가
     *
     * @param isbn 입고할 상품의 ISBN
     * @param quantity 입고 수량
     * @return 없음
     */
    @Transactional
    public void stockIn(String isbn, int quantity) {
        // 상품 존재 확인
        Product product = productRepository.findByIsbn(isbn);
        if (product == null) {
            throw new RuntimeException("상품을 찾을 수 없습니다: " + isbn);
        }

        // 현재 재고량 조회 (최신 after_quantity)
        List<Integer> stockList = stockRepository.findCurrentStockListByIsbn(isbn, org.springframework.data.domain.PageRequest.of(0, 1));
        Integer currentStock = stockList.isEmpty() ? 0 : stockList.get(0);
        
        // Stock 테이블에 입고 기록 추가
        Stock stock = new Stock();
        stock.setIsbn(isbn);
        stock.setInOutType(Stock.InOutType.INBOUND);
        stock.setInOutQuantity(quantity);
        stock.setBeforeQuantity(currentStock);
        stock.setAfterQuantity(currentStock + quantity);
        stock.setUpdateDate(LocalDateTime.now());
        
        stockRepository.save(stock);
    }

    /**
     * 상품 상태 변경
     *
     * 비즈니스 로직: 상품의 판매 상태를 변경하고 이력을 저장
     *
     * @param isbn 상태를 변경할 상품의 ISBN
     * @param newStatus 새로운 판매 상태
     * @return 없음
     */
    @Transactional
    public void changeProductStatus(String isbn, String newStatus) {
        // 상품 존재 확인
        Product product = productRepository.findByIsbn(isbn);
        if (product == null) {
            throw new RuntimeException("상품을 찾을 수 없습니다: " + isbn);
        }

        // 상태 enum 변환
        Product.SalesStatus statusEnum;
        try {
            statusEnum = Product.SalesStatus.valueOf(newStatus);
        } catch (IllegalArgumentException e) {
            throw new RuntimeException("유효하지 않은 상태입니다: " + newStatus);
        }

        // 이전 상태 저장
        Product.SalesStatus oldStatus = product.getSalesStatus();
        
        System.out.println("상태 변경 전: " + isbn + " - " + oldStatus + " -> " + statusEnum);
        
        // Product 테이블 업데이트
        product.setSalesStatus(statusEnum);
        productRepository.save(product);

        // ProductHistory 테이블에 이력 추가
        ProductHistory history = new ProductHistory();
        history.setIsbn(isbn);
        history.setStatusModifiedHistory(ProductHistory.StatusModifiedHistory.valueOf(newStatus));
        history.setPriceModifiedHistory(product.getPrice()); // 현재 가격 그대로 저장
        history.setUpdateDate(LocalDateTime.now());
        
        productHistoryRepository.save(history);
        
        System.out.println("상태 변경 완료: " + isbn + " - " + statusEnum);
    }

    /**
     * 상품 정보 수정 (가격 변경)
     *
     * 비즈니스 로직: 상품의 가격을 변경하고 이력을 저장
     *
     * @param isbn 가격을 변경할 상품의 ISBN
     * @param newPrice 새로운 가격
     * @return 없음
     */
    @Transactional
    public void editProduct(String isbn, Integer newPrice) {
        // 상품 존재 확인
        Product product = productRepository.findByIsbn(isbn);
        if (product == null) {
            throw new RuntimeException("상품을 찾을 수 없습니다: " + isbn);
        }

        // 가격 유효성 검사
        if (newPrice == null || newPrice < 0) {
            throw new RuntimeException("유효하지 않은 가격입니다: " + newPrice);
        }

        // 이전 가격 저장
        Integer oldPrice = product.getPrice();
        
        // Product 테이블 업데이트
        product.setPrice(newPrice);
        productRepository.save(product);

        // ProductHistory 테이블에 이력 추가
        ProductHistory history = new ProductHistory();
        history.setIsbn(isbn);
        history.setStatusModifiedHistory(ProductHistory.StatusModifiedHistory.valueOf(product.getSalesStatus().name()));
        history.setPriceModifiedHistory(newPrice); // 변경된 새 가격 저장
        history.setUpdateDate(LocalDateTime.now());
        
        productHistoryRepository.save(history);
    }

    /**
     * ISBN 존재 여부 확인
     *
     * 비즈니스 로직: 해당 ISBN이 상품 테이블에 존재하는지 확인
     *
     * @param isbn 확인할 ISBN
     * @return 존재 여부(boolean)
     */
    public boolean existsById(String isbn) {
        return productRepository.existsByIsbn(isbn);
    }

    /**
     * 상품 등록 처리
     *
     * 비즈니스 로직: 전달받은 정보로 신규 상품을 등록
     *
     * @param body 등록할 상품 정보(Map)
     * @return 없음
     */
    @Transactional
    public void registerProduct(java.util.Map<String, Object> body) {
        // 필수값 검증
        String isbn = (String) body.get("isbn");
        if (isbn == null || isbn.isBlank()) throw new IllegalArgumentException("ISBN은 필수입니다.");
        if (productRepository.existsByIsbn(isbn)) throw new IllegalArgumentException("이미 등록된 ISBN입니다.");
        Integer lowCategory = body.get("lowCategory") != null ? Integer.parseInt(body.get("lowCategory").toString()) : null;
        String productName = (String) body.get("title");
        String author = (String) body.get("author");
        String publisher = (String) body.get("publisher");
        Integer price = body.get("price") != null ? Integer.parseInt(body.get("price").toString()) : null;
        java.math.BigDecimal rate = body.get("rate") != null ? new java.math.BigDecimal(body.get("rate").toString()) : null;
        String briefDescription = (String) body.get("briefDescription");
        String detailDescription = (String) body.get("detailDescription");
        String img = (String) body.get("img");
        Integer width = body.get("width") != null ? Integer.parseInt(body.get("width").toString()) : null;
        Integer height = body.get("height") != null ? Integer.parseInt(body.get("height").toString()) : null;
        Integer page = body.get("page") != null ? Integer.parseInt(body.get("page").toString()) : null;
        String salesStatusStr = (String) body.get("salesStatus");
        Product.SalesStatus salesStatus = salesStatusStr != null ? Product.SalesStatus.valueOf(salesStatusStr) : null;
        String regDateStr = (String) body.get("regDate");
        java.time.LocalDateTime regDate = regDateStr != null ? java.time.LocalDate.parse(regDateStr).atStartOfDay() : java.time.LocalDateTime.now();

        // 엔티티 생성 및 저장
        Product product = new Product();
        product.setIsbn(isbn);
        product.setLowCategory(lowCategory);
        product.setProductName(productName);
        product.setAuthor(author);
        product.setPublisher(publisher);
        product.setPrice(price);
        product.setRate(rate);
        product.setBriefDescription(briefDescription);
        product.setDetailDescription(detailDescription);
        product.setImg(img);
        product.setWidth(width);
        product.setHeight(height);
        product.setPage(page);
        product.setSalesStatus(salesStatus);
        product.setRegDate(regDate);
        productRepository.save(product);
    }

    /**
     * 상품 전체 정보 수정 처리
     *
     * 비즈니스 로직: 전달받은 정보로 상품의 전체 정보를 수정
     *
     * @param originalIsbn 기존 ISBN
     * @param body 수정할 정보(Map)
     * @return 없음
     */
    @Transactional
    public void updateProductAll(String originalIsbn, java.util.Map<String, Object> body) {
        // 상품 존재 확인
        Product product = productRepository.findByIsbn(originalIsbn);
        if (product == null) {
            throw new RuntimeException("상품을 찾을 수 없습니다: " + originalIsbn);
        }

        // 기존 정보 저장 (히스토리용)
        Product.SalesStatus oldStatus = product.getSalesStatus();
        Integer oldPrice = product.getPrice();
        
        // ISBN 변경 처리
        String newIsbn = (String) body.get("newIsbn");
        boolean isbnChanged = false;
        if (newIsbn != null && !newIsbn.equals(originalIsbn)) {
            // 새 ISBN 중복 확인
            if (productRepository.existsByIsbn(newIsbn)) {
                throw new RuntimeException("이미 존재하는 ISBN입니다: " + newIsbn);
            }
            isbnChanged = true;
        }

        // 필드별 업데이트
        if (body.get("lowCategory") != null) {
            product.setLowCategory((Integer) body.get("lowCategory"));
        }
        if (body.get("productName") != null) {
            product.setProductName((String) body.get("productName"));
        }
        if (body.get("author") != null) {
            product.setAuthor((String) body.get("author"));
        }
        if (body.get("publisher") != null) {
            product.setPublisher((String) body.get("publisher"));
        }
        if (body.get("price") != null) {
            product.setPrice((Integer) body.get("price"));
        }
        if (body.get("rate") != null) {
            if (body.get("rate") instanceof Double) {
                product.setRate(java.math.BigDecimal.valueOf((Double) body.get("rate")));
            } else if (body.get("rate") instanceof Integer) {
                product.setRate(java.math.BigDecimal.valueOf((Integer) body.get("rate")));
            }
        }
        if (body.get("img") != null) {
            product.setImg((String) body.get("img"));
        }
        if (body.get("briefDescription") != null) {
            product.setBriefDescription((String) body.get("briefDescription"));
        }
        if (body.get("detailDescription") != null) {
            product.setDetailDescription((String) body.get("detailDescription"));
        }
        if (body.get("width") != null) {
            product.setWidth((Integer) body.get("width"));
        }
        if (body.get("height") != null) {
            product.setHeight((Integer) body.get("height"));
        }
        if (body.get("page") != null) {
            product.setPage((Integer) body.get("page"));
        }
        if (body.get("salesStatus") != null) {
            Product.SalesStatus newStatus = Product.SalesStatus.valueOf((String) body.get("salesStatus"));
            product.setSalesStatus(newStatus);
        }
        if (body.get("regDate") != null) {
            String regDateStr = (String) body.get("regDate");
            java.time.LocalDateTime regDate = java.time.LocalDate.parse(regDateStr).atStartOfDay();
            product.setRegDate(regDate);
        }

        // ISBN이 변경된 경우 기존 레코드 삭제 후 새 레코드 생성
        if (isbnChanged) {
            // 기존 레코드 삭제
            productRepository.delete(product);
            
            // 새 ISBN으로 상품 생성
            product.setIsbn(newIsbn);
            productRepository.save(product);
            
            System.out.println("ISBN 변경: " + originalIsbn + " -> " + newIsbn);
        } else {
            // 기존 레코드 업데이트
            productRepository.save(product);
        }

        // 가격이나 판매상태가 변경된 경우에만 ProductHistory에 기록
        boolean priceChanged = !oldPrice.equals(product.getPrice());
        boolean statusChanged = !oldStatus.equals(product.getSalesStatus());
        
        if (priceChanged || statusChanged) {
            System.out.println("ProductHistory 기록: 가격변경=" + priceChanged + ", 상태변경=" + statusChanged);
            System.out.println("이전 가격: " + oldPrice + " -> 새 가격: " + product.getPrice());
            System.out.println("이전 상태: " + oldStatus + " -> 새 상태: " + product.getSalesStatus());
            
            ProductHistory history = new ProductHistory();
            history.setIsbn(product.getIsbn()); // 새 ISBN 사용
            history.setStatusModifiedHistory(ProductHistory.StatusModifiedHistory.valueOf(product.getSalesStatus().name()));
            history.setPriceModifiedHistory(product.getPrice());
            history.setUpdateDate(LocalDateTime.now());
            
            productHistoryRepository.save(history);
        }
    }
}
