package bookstore_ai_project.controller;

import bookstore_ai_project.repository.LowCategoryRepository;
import bookstore_ai_project.repository.StockRepository;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.ui.Model;
import bookstore_ai_project.service.ProductService;
import bookstore_ai_project.service.CategoryService;
import bookstore_ai_project.entity.Product;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.http.ResponseEntity;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import bookstore_ai_project.entity.Stock;

@Controller
@RequestMapping("/product")
public class ProductController {

    private static final Logger logger = LoggerFactory.getLogger(ProductController.class);

    /** 상품 관리 비즈니스 로직 서비스 */
    @Autowired
    private ProductService productService;
    
    /** 카테고리 관리 비즈니스 로직 서비스 */
    @Autowired
    private CategoryService categoryService;
    
    /** 소분류 데이터 접근 리포지토리 */
    @Autowired
    private LowCategoryRepository lowCategoryRepository;

    /** 재고 데이터 접근 리포지토리 */
    @Autowired
    private StockRepository stockRepository;

    /**
     * 상품 상세 페이지 (PathVariable 방식)
     *
     * 비즈니스 로직: ISBN으로 상품 상세 정보를 조회하여 화면에 표시
     *
     * @param isbn 상품 ISBN
     * @param page 리뷰 페이지 번호
     * @param model 뷰 데이터 전달 모델
     * @return 상품 상세 뷰 이름
     */
    @GetMapping("/detail/{isbn}")
    public String productDetail(@PathVariable String isbn, @RequestParam(defaultValue = "0") int page, Model model) {
        productService.increaseSearchCount(isbn);

        // 실제 상품 정보 조회
        Product product = productService.getProductDetailByIsbn(isbn);
        if (product == null) {
            model.addAttribute("error", "상품을 찾을 수 없습니다.");
            return "product/product_detail";
        }

        // 카테고리명 조합 (대 > 중 > 소)
        String categoryPath = "";
        if (product.getLowCategoryEntity() != null) {
            var low = product.getLowCategoryEntity();
            if (low.getMiddleCategoryEntity() != null) {
                var mid = low.getMiddleCategoryEntity();
                if (mid.getTopCategoryEntity() != null) {
                    categoryPath = mid.getTopCategoryEntity().getTopCategoryName() + " > ";
                }
                categoryPath += mid.getMidCategoryName() + " > ";
            }
            categoryPath += low.getLowCategoryName();
        }
        model.addAttribute("categoryPath", categoryPath);

        // 상태값 한글 매핑
        String salesStatusKor = "";
        if (product.getSalesStatus() != null) {
            switch (product.getSalesStatus()) {
                case ON_SALE -> salesStatusKor = "판매중";
                case OUT_OF_PRINT -> salesStatusKor = "절판";
                case TEMPORARILY_OUT_OF_STOCK -> salesStatusKor = "일시품절";
                case EXPECTED_IN_STOCK -> salesStatusKor = "입고예정";
            }
        }
        model.addAttribute("salesStatusKor", salesStatusKor);

        // 리뷰 리스트 (최신순, soft delete 제외, 5개씩 페이지네이션, 닉네임 포함)
        int pageSize = 10;
        var reviewData = productService.getProductReviewsWithNicknameByIsbnPaged(isbn, page, pageSize);
        model.addAttribute("reviewsWithNickname", reviewData.get("reviews"));
        model.addAttribute("currentReviewPage", page);
        model.addAttribute("totalReviewPages", reviewData.get("totalPages"));
        model.addAttribute("totalReviewElements", reviewData.get("totalElements"));

        model.addAttribute("product", product);
        return "product/product_detail";
    }

    /**
     * 상품 상세 페이지 (QueryString 방식)
     *
     * 비즈니스 로직: 쿼리스트링으로 ISBN, page를 받아 상세 페이지로 이동
     *
     * @param isbn 상품 ISBN
     * @param page 리뷰 페이지 번호
     * @param model 뷰 데이터 전달 모델
     * @return 상품 상세 뷰 이름
     */
    @GetMapping("/detail")
    public String productDetailQuery(@RequestParam("isbn") String isbn,
                                     @RequestParam(value = "page", defaultValue = "0") int page,
                                     Model model) {
        return productDetail(isbn, page, model); // page 파라미터 반영
    }

    /**
     * 소분류별 상품 목록 페이지
     *
     * 비즈니스 로직: 소분류 카테고리별 상품 리스트 조회 및 화면 표시
     *
     * @param categoryId 소분류 카테고리 ID
     * @param page 페이지 번호
     * @param size 페이지 크기
     * @param sort 정렬 기준
     * @param title 검색어(제목)
     * @param author 검색어(저자)
     * @param publisher 검색어(출판사)
     * @param model 뷰 데이터 전달 모델
     * @return 상품 리스트 뷰 이름
     */
    @GetMapping("/category/low/{categoryId}")
    public String productList(@PathVariable Integer categoryId, 
                            @RequestParam(defaultValue = "1") int page,
                            @RequestParam(defaultValue = "30") int size,
                            @RequestParam(defaultValue = "latest") String sort,
                            @RequestParam(required = false) String title,
                            @RequestParam(required = false) String author,
                            @RequestParam(required = false) String publisher,
                            Model model) {
        
        // 카테고리 정보 조회
        var lowCategory = lowCategoryRepository.findById(categoryId).orElse(null);
        if (lowCategory == null) {
            model.addAttribute("error", "카테고리를 찾을 수 없습니다.");
            return "product/product_list";
        }
        
        // 카테고리 경로(대>중>소)
        String categoryPath = "";
        if (lowCategory.getMiddleCategoryEntity() != null) {
            var mid = lowCategory.getMiddleCategoryEntity();
            if (mid.getTopCategoryEntity() != null) {
                categoryPath = mid.getTopCategoryEntity().getTopCategoryName() + " > ";
            }
            categoryPath += mid.getMidCategoryName() + " > ";
        }
        categoryPath += lowCategory.getLowCategoryName();
        // 상품 목록 조회
        var productListResponse = productService.getProductsByLowCategory(categoryId, sort, page, size, title, author, publisher);
        productListResponse.setCategoryName(lowCategory.getLowCategoryName());
        
        model.addAttribute("categoryName", lowCategory.getLowCategoryName());
        model.addAttribute("categoryId", categoryId);
        model.addAttribute("categoryPath", categoryPath);
        model.addAttribute("products", productListResponse.getProducts());
        model.addAttribute("currentPage", productListResponse.getCurrentPage());
        model.addAttribute("totalPages", productListResponse.getTotalPages());
        model.addAttribute("totalItems", productListResponse.getTotalItems());
        model.addAttribute("pageSize", productListResponse.getPageSize());
        model.addAttribute("currentSort", sort);
        // 검색 파라미터 유지
        model.addAttribute("param", new java.util.HashMap<String, Object>() {{
            put("title", title);
            put("author", author);
            put("publisher", publisher);
        }});
        
        return "product/product_list";
    }

    /**
     * 전체 상품 OR 검색(일반 검색)
     *
     * 비즈니스 로직: 검색어(q)로 전체 상품을 OR 조건으로 검색
     *
     * @param q 검색어
     * @param page 페이지 번호
     * @param size 페이지 크기
     * @param sort 정렬 기준
     * @param model 뷰 데이터 전달 모델
     * @return 상품 리스트 뷰 이름
     */
    @GetMapping("/search")
    public String searchProducts(
            @RequestParam(required = false) String q,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "30") int size,
            @RequestParam(defaultValue = "latest") String sort,
            Model model) {
        var productListResponse = productService.searchProductsOr(q, sort, page, size);
        model.addAttribute("categoryPath", "검색결과");
        model.addAttribute("products", productListResponse.getProducts());
        model.addAttribute("currentPage", productListResponse.getCurrentPage());
        model.addAttribute("totalPages", productListResponse.getTotalPages());
        model.addAttribute("totalItems", productListResponse.getTotalItems());
        model.addAttribute("pageSize", productListResponse.getPageSize());
        model.addAttribute("currentSort", sort);
        model.addAttribute("param", new java.util.HashMap<String, Object>() {{ put("q", q); }});
        return "product/product_list";
    }

    /**
     * 전체 상품 AND 검색(상세 검색)
     *
     * 비즈니스 로직: 여러 검색 조건을 AND로 결합하여 상품 검색
     *
     * @param q 검색어
     * @param bookTitle 제목
     * @param author 저자
     * @param publisher 출판사
     * @param page 페이지 번호
     * @param size 페이지 크기
     * @param sort 정렬 기준
     * @param model 뷰 데이터 전달 모델
     * @return 상품 리스트 뷰 이름
     */
    @GetMapping("/search-advanced")
    public String searchProductsAdvanced(
            @RequestParam(required = false) String q,
            @RequestParam(required = false) String bookTitle,
            @RequestParam(required = false) String author,
            @RequestParam(required = false) String publisher,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "30") int size,
            @RequestParam(defaultValue = "latest") String sort,
            Model model) {
        var productListResponse = productService.searchProductsAdvanced(q, bookTitle, author, publisher, sort, page, size);
        
        // 전체상품 클릭시에는 "상품목록", 실제 검색시에는 "검색결과"로 표시
        boolean hasSearchParams = (q != null && !q.trim().isEmpty()) || 
                                 (bookTitle != null && !bookTitle.trim().isEmpty()) || 
                                 (author != null && !author.trim().isEmpty()) || 
                                 (publisher != null && !publisher.trim().isEmpty());
        
        model.addAttribute("categoryPath", hasSearchParams ? "검색결과" : "상품목록");
        model.addAttribute("products", productListResponse.getProducts());
        model.addAttribute("currentPage", productListResponse.getCurrentPage());
        model.addAttribute("totalPages", productListResponse.getTotalPages());
        model.addAttribute("totalItems", productListResponse.getTotalItems());
        model.addAttribute("pageSize", productListResponse.getPageSize());
        model.addAttribute("currentSort", sort);
        // 좌측 상세검색에 현재 검색 조건 유지
        model.addAttribute("param", new java.util.HashMap<String, Object>() {{
            put("bookTitle", bookTitle != null ? bookTitle : ""); 
            put("author", author != null ? author : ""); 
            put("publisher", publisher != null ? publisher : ""); 
            put("q", q);
        }});
        return "product/product_list";
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
        logger.info("재고 조회 요청 - ISBN: {}", isbn);
        
        try {
            // 디버깅을 위해 해당 ISBN의 모든 Stock 데이터 조회
            List<Stock> allStocks = stockRepository.findAllByIsbnForDebug(isbn);
            logger.info("ISBN {} 관련 Stock 데이터 개수: {}", isbn, allStocks.size());
            
            if (!allStocks.isEmpty()) {
                logger.info("최신 Stock 데이터:");
                for (int i = 0; i < Math.min(3, allStocks.size()); i++) {
                    Stock stock = allStocks.get(i);
                    logger.info("  [{}] ID: {}, after_quantity: {}, update_date: {}, in_out_type: {}", 
                              i, stock.getStockId(), stock.getAfterQuantity(), 
                              stock.getUpdateDate(), stock.getInOutType());
                }
            } else {
                logger.warn("ISBN {}에 대한 Stock 데이터가 존재하지 않습니다.", isbn);
            }
            
            // 최신 재고 조회 - Native Query 방식
            logger.info("Native Query 방식으로 재고 조회 시도");
            Integer nativeStock = stockRepository.findCurrentStockByIsbnNative(isbn);
            logger.info("Native Query 결과: {}", nativeStock);
            
            // JPA Query 방식
            logger.info("JPA Query 방식으로 재고 조회 시도");
            List<Integer> stockList = stockRepository.findCurrentStockListByIsbn(isbn, org.springframework.data.domain.PageRequest.of(0, 1));
            logger.info("JPA Query 반환된 리스트 크기: {}", stockList.size());
            logger.info("JPA Query 반환된 데이터: {}", stockList);
            Integer jpaStock = stockList.isEmpty() ? 0 : stockList.get(0);
            logger.info("JPA Query 재고 결과: {}", jpaStock);
            
            // Native Query 결과를 우선 사용
            Integer stock = (nativeStock != null) ? nativeStock : 0;
            logger.info("최종 재고 결과 (Native 우선): {}", stock);
            
            return ResponseEntity.ok(java.util.Map.of("stock", stock));
            
        } catch (Exception e) {
            logger.error("재고 조회 중 오류 발생 - ISBN: {}, 오류: {}", isbn, e.getMessage(), e);
            return ResponseEntity.ok(java.util.Map.of("stock", 0));
        }
    }

    /**
     * 테스트용 간단한 재고 조회 API
     *
     * 비즈니스 로직: 하드코딩된 값과 DB에서 조회한 재고를 함께 반환
     *
     * @param isbn 상품 ISBN
     * @return 재고 정보(Map)
     */
    @GetMapping("/api/debug/stock/{isbn}")
    @ResponseBody
    public ResponseEntity<?> debugStock(@PathVariable String isbn) {
        try {
            // 단순히 하드코딩된 값 반환
            Map<String, Object> result = new HashMap<>();
            result.put("isbn", isbn);
            result.put("hardcoded_stock", 15);
            
            // DB에서 조회
            Integer dbStock = stockRepository.findCurrentStockByIsbnNative(isbn);
            result.put("db_stock", dbStock);
            
            // 모든 Stock 데이터
            List<Stock> allStocks = stockRepository.findAllByIsbnForDebug(isbn);
            result.put("total_records", allStocks.size());
            
            if (!allStocks.isEmpty()) {
                Stock latest = allStocks.get(0);
                Map<String, Object> latestData = new HashMap<>();
                latestData.put("stock_id", latest.getStockId());
                latestData.put("after_quantity", latest.getAfterQuantity());
                latestData.put("update_date", latest.getUpdateDate());
                latestData.put("in_out_type", latest.getInOutType());
                result.put("latest_record", latestData);
            }
            
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.ok(Map.of("error", e.getMessage()));
        }
    }

}
