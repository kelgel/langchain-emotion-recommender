# 🔧 책크인 트러블슈팅 가이드

프로젝트 개발 과정에서 발생한 주요 문제점들과 해결 방법을 정리한 문서입니다.

---

## 📋 목차

1. [데이터베이스 관련 문제](#데이터베이스-관련-문제)
2. [JPA/Hibernate 문제](#jpahibernate-문제)
3. [Spring Boot 설정 문제](#spring-boot-설정-문제)
4. [API 개발 문제](#api-개발-문제)
5. [프론트엔드 연동 문제](#프론트엔드-연동-문제)
6. [성능 최적화 문제](#성능-최적화-문제)
7. [결제 시스템 문제](#결제-시스템-문제)
8. [권한 관리 문제](#권한-관리-문제)

---

## 🗄 데이터베이스 관련 문제

### 1. MySQL 연결 실패 문제

**🚨 문제상황:**
```
Could not create connection to database server. Attempted to reconnect 3 times. Giving up.
```

**💡 해결방법:**
1. MySQL 서버 실행 상태 확인:
   ```bash
   sudo systemctl status mysql
   # 또는
   brew services list mysql
   ```

2. 포트 충돌 확인:
   ```bash
   netstat -tulpn | grep 3306
   ```

3. `application.properties` 설정 확인:
   ```properties
   spring.datasource.url=jdbc:mysql://your-rds-endpoint:3306/your_database?serverTimezone=Asia/Seoul
   spring.datasource.username=your_db_username
   spring.datasource.password=your_db_password
   ```

### 2. 문자 인코딩 문제

**🚨 문제상황:**
```
한글 데이터가 '???' 또는 깨진 문자로 저장됨
```

**💡 해결방법:**
1. 데이터베이스 생성 시 문자셋 지정:
   ```sql
   CREATE DATABASE bookstore_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. MySQL 설정 파일(`my.cnf`) 수정:
   ```ini
   [mysql]
   default-character-set=utf8mb4
   
   [mysqld]
   character-set-server=utf8mb4
   collation-server=utf8mb4_unicode_ci
   ```

### 3. 외래키 제약 조건 오류

**🚨 문제상황:**
```
Cannot add or update a child row: a foreign key constraint fails
```

**💡 해결방법:**
1. 데이터 삽입 순서 조정 (부모 테이블 → 자식 테이블)
2. 외래키 체크 임시 비활성화:
   ```sql
   SET FOREIGN_KEY_CHECKS = 0;
   -- 데이터 삽입 작업
   SET FOREIGN_KEY_CHECKS = 1;
   ```

---

## 🔧 JPA/Hibernate 문제

### 1. StockRepository 쿼리 문제

**🚨 문제상황:**
```java
// 기존 코드 - 실패
@Query("SELECT s.afterQuantity FROM Stock s WHERE s.isbn = :isbn ORDER BY s.updateDate DESC")
Integer findLatestStockByIsbn(@Param("isbn") String isbn);
```
- JPA 메서드명과 테이블/컬럼명 매핑 오류 발생

**💡 해결방법:**
```java
// 수정된 코드 - 성공
@Query(value = "SELECT after_quantity FROM stock WHERE isbn = :isbn ORDER BY update_date DESC LIMIT 1", nativeQuery = true)
Integer findLatestStockByIsbn(@Param("isbn") String isbn);
```
- Native SQL 쿼리 사용으로 직접 테이블/컬럼명 지정

### 2. 지연 로딩(Lazy Loading) 문제

**🚨 문제상황:**
```
LazyInitializationException: could not initialize proxy - no Session
```

**💡 해결방법:**
1. `@Transactional` 어노테이션 추가:
   ```java
   @Transactional(readOnly = true)
   public List<ProductResponse> getProducts() {
       // 메서드 내용
   }
   ```

2. 즉시 로딩으로 변경 (필요시):
   ```java
   @ManyToOne(fetch = FetchType.EAGER)
   private Category category;
   ```

### 3. N+1 쿼리 문제

**🚨 문제상황:**
- 연관 엔티티 조회 시 과도한 쿼리 실행

**💡 해결방법:**
1. `@EntityGraph` 사용:
   ```java
   @EntityGraph(attributePaths = {"category", "stock"})
   List<Product> findAllWithCategory();
   ```

2. Fetch Join 사용:
   ```java
   @Query("SELECT p FROM Product p JOIN FETCH p.category")
   List<Product> findAllWithCategory();
   ```

---

## ⚙️ Spring Boot 설정 문제

### 1. Thymeleaf 템플릿 경로 문제

**🚨 문제상황:**
```
TemplateInputException: Error resolving template [product/list]
```

**💡 해결방법:**
1. 경로 설정 확인:
   ```properties
   spring.thymeleaf.prefix=classpath:/templates/
   spring.thymeleaf.suffix=.html
   ```

2. 디렉토리 구조 확인:
   ```
   src/main/resources/templates/
   ├── layout/
   ├── product/
   ├── user/
   └── admin/
   ```

### 2. 정적 자원 매핑 문제

**🚨 문제상황:**
```
CSS, JS 파일이 404 오류로 로드되지 않음
```

**💡 해결방법:**
1. WebConfig 설정:
   ```java
   @Configuration
   public class WebConfig implements WebMvcConfigurer {
       @Override
       public void addResourceHandlers(ResourceHandlerRegistry registry) {
           registry.addResourceHandler("/static/**")
                   .addResourceLocations("classpath:/static/");
       }
   }
   ```

### 3. CORS 문제

**🚨 문제상황:**
```
Access to fetch at 'http://localhost:8080/api/...' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**💡 해결방법:**
```java
@CrossOrigin(origins = "*")
@RestController
public class ProductController {
    // 컨트롤러 내용
}
```

---

## 🌐 API 개발 문제

### 1. API 엔드포인트 404 오류

**🚨 문제상황:**
```javascript
// 실패한 요청
fetch('/api/products/9788932473901/stock')
```
- 404 Not Found 오류 발생

**💡 해결방법:**
```java
// Controller 매핑 확인
@RequestMapping("/product")  // 컨트롤러 레벨 매핑
@RestController
public class ProductController {
    
    @GetMapping("/api/stock/{isbn}")  // 메서드 레벨 매핑
    public ResponseEntity<Map<String, Integer>> getStock(@PathVariable String isbn) {
        // 실제 URL: /product/api/stock/{isbn}
    }
}
```

```javascript
// 수정된 요청
fetch('/product/api/stock/9788932473901')
```

### 2. JSON 응답 형식 문제

**🚨 문제상황:**
```java
// 문제가 있는 응답
return ResponseEntity.ok("재고: " + stock);
```

**💡 해결방법:**
```java
// 개선된 응답
Map<String, Integer> response = Map.of("stock", stock);
return ResponseEntity.ok(response);
```

### 3. 요청 파라미터 바인딩 문제

**🚨 문제상황:**
```java
// 실패: 파라미터명 불일치
@PostMapping("/cart/add")
public String addToCart(@RequestParam("productId") String isbn) {
}
```

**💡 해결방법:**
```java
// 성공: 정확한 파라미터명
@PostMapping("/cart/add")
public String addToCart(@RequestParam("isbn") String isbn) {
}
```

---

## 🎨 프론트엔드 연동 문제

### 1. JavaScript 전역 변수 문제

**🚨 문제상황:**
```javascript
// 문제: 전역 변수가 undefined
if (window.isAdmin) {
    // 실행되지 않음
}
```

**💡 해결방법:**
```html
<!-- header.html에서 전역 변수 설정 -->
<script th:inline="javascript">
    window.isAdmin = /*[[${session.isAdmin != null ? session.isAdmin : false}]]*/ false;
</script>
```

### 2. 이벤트 리스너 등록 문제

**🚨 문제상황:**
```javascript
// 문제: DOM 로드 전 실행
document.getElementById('cartBtn').addEventListener('click', function() {
    // 요소를 찾을 수 없음
});
```

**💡 해결방법:**
```javascript
// 해결: DOM 로드 후 실행
document.addEventListener('DOMContentLoaded', function() {
    const cartBtn = document.getElementById('cartBtn');
    if (cartBtn) {
        cartBtn.addEventListener('click', function() {
            // 정상 실행
        });
    }
});
```

### 3. 비동기 요청 처리 문제

**🚨 문제상황:**
```javascript
// 문제: 에러 처리 누락
fetch('/api/cart/add', {
    method: 'POST',
    body: formData
}).then(response => response.text());
```

**💡 해결방법:**
```javascript
// 해결: 완전한 에러 처리
fetch('/api/cart/add', {
    method: 'POST',
    body: formData
})
.then(response => {
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.text();
})
.then(data => {
    console.log('성공:', data);
})
.catch(error => {
    console.error('오류:', error);
    alert('요청 처리 중 오류가 발생했습니다.');
});
```

---

## ⚡ 성능 최적화 문제

### 1. API 호출 과부하 문제

**🚨 문제상황:**
- 수량 조절 버튼 클릭 시마다 재고 확인 API 호출
- 사용자가 빠르게 클릭할 때 서버 과부하 발생

**💡 해결방법:**
```javascript
// 클라이언트 사이드 캐싱 구현 (product_detail.js:315 참조)
let stockCache = new Map();
const CACHE_DURATION = 30000; // 30초

function getCachedStock(isbn) {
    const cached = stockCache.get(isbn);
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        return Promise.resolve(cached.stock);
    }
    
    return fetch(`/product/api/stock/${isbn}`)
        .then(response => response.json())
        .then(data => {
            stockCache.set(isbn, {
                stock: data.stock,
                timestamp: Date.now()
            });
            return data.stock;
        });
}
```

### 2. 페이지 로딩 속도 문제

**🚨 문제상황:**
- 상품 목록 페이지에서 모든 상품의 재고를 개별적으로 조회

**💡 해결방법:**
```javascript
// 페이지 로드 시 일괄 재고 조회
function loadInitialStocks() {
    const isbns = Array.from(document.querySelectorAll('[data-isbn]'))
                      .map(el => el.dataset.isbn);
    
    if (isbns.length > 0) {
        fetch('/api/stocks/batch', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({isbns: isbns})
        })
        .then(response => response.json())
        .then(stockData => {
            // 캐시에 저장
            Object.entries(stockData).forEach(([isbn, stock]) => {
                stockCache.set(isbn, {stock, timestamp: Date.now()});
            });
        });
    }
}
```

---

## 💳 결제 시스템 문제

### 1. KakaoPay API 연동 오류

**🚨 문제상황:**
```json
{
  "error": "Invalid request",
  "error_description": "Missing required parameter: cid"
}
```

**💡 해결방법:**
1. `application.properties` 설정 확인:
   ```properties
   kakaopay.admin-key=your_admin_key_here
   kakaopay.cid=your_cid_here
   ```

2. API 요청 헤더 확인:
   ```java
   HttpHeaders headers = new HttpHeaders();
   headers.set("Authorization", "KakaoAK " + adminKey);
   headers.set("Content-Type", "application/x-www-form-urlencoded;charset=utf-8");
   ```

### 2. 결제 취소 처리 문제

**🚨 문제상황:**
```
사용자가 결제 창을 닫았을 때 주문 데이터가 그대로 남아있음
```

**💡 해결방법:**
```java
@GetMapping("/payment/cancel")
public String paymentCancel(@RequestParam String paymentId) {
    // 주문 상태를 'CANCELLED'로 변경
    orderService.cancelOrder(paymentId);
    return "redirect:/cart?message=payment_cancelled";
}
```

---

## 🔐 권한 관리 문제

### 1. 관리자 접근 제어 누락

**🚨 문제상황:**
```
관리자가 일반 사용자 기능(장바구니, 마이페이지)에 접근 가능
```

**💡 해결방법:**
1. 서버 사이드 검증:
   ```java
   @GetMapping("/cart")
   public String cart(HttpSession session) {
       Boolean isAdmin = (Boolean) session.getAttribute("isAdmin");
       if (isAdmin != null && isAdmin) {
           return "redirect:/admin";
       }
       // 장바구니 로직
   }
   ```

2. 클라이언트 사이드 UI 제어:
   ```javascript
   if (window.isAdmin) {
       const cartLink = document.getElementById('headerCartLink');
       cartLink.style.opacity = '0.5';
       cartLink.style.cursor = 'not-allowed';
       cartLink.addEventListener('click', function(e) {
           e.preventDefault();
           alert('일반 사용자 전용 기능입니다.');
       });
   }
   ```

### 2. 세션 관리 문제

**🚨 문제상황:**
```
사용자 로그아웃 후에도 세션 정보가 남아있음
```

**💡 해결방법:**
```java
@PostMapping("/logout")
public String logout(HttpSession session) {
    session.invalidate(); // 전체 세션 무효화
    return "redirect:/main";
}
```

---

## 🛠 기타 개발 도구 문제

### 1. IntelliJ IDEA Hot Reload 문제

**🚨 문제상황:**
```
코드 변경 후 자동 재시작되지 않음
```

**💡 해결방법:**
1. `pom.xml`에 DevTools 의존성 추가:
   ```xml
   <dependency>
       <groupId>org.springframework.boot</groupId>
       <artifactId>spring-boot-devtools</artifactId>
       <scope>runtime</scope>
       <optional>true</optional>
   </dependency>
   ```

2. IntelliJ 설정:
   - Settings → Build → Compiler → Build project automatically 체크
   - Registry → compiler.automake.allow.when.app.running 체크

### 2. Maven 빌드 문제

**🚨 문제상황:**
```
Tests run: 1, Failures: 1, Errors: 0, Skipped: 0
```

**💡 해결방법:**
```xml
<!-- pom.xml에서 테스트 스킵 -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <configuration>
        <skipTests>true</skipTests>
    </configuration>
</plugin>
```

---

## 📊 모니터링 및 디버깅

### 1. SQL 쿼리 로깅

**💡 설정 방법:**
```properties
# application.properties
logging.level.org.hibernate.SQL=DEBUG
logging.level.org.hibernate.type.descriptor.sql.BasicBinder=TRACE
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
```

### 2. API 응답 시간 측정

**💡 구현 방법:**
```java
@Component
public class PerformanceInterceptor implements HandlerInterceptor {
    
    @Override
    public boolean preHandle(HttpServletRequest request, 
                           HttpServletResponse response, 
                           Object handler) throws Exception {
        long startTime = System.currentTimeMillis();
        request.setAttribute("startTime", startTime);
        return true;
    }
    
    @Override
    public void afterCompletion(HttpServletRequest request, 
                              HttpServletResponse response, 
                              Object handler, Exception ex) throws Exception {
        long startTime = (Long) request.getAttribute("startTime");
        long endTime = System.currentTimeMillis();
        long executeTime = endTime - startTime;
        
        if (executeTime > 1000) { // 1초 이상 걸린 요청 로깅
            System.out.println("Slow API: " + request.getRequestURI() + 
                             " took " + executeTime + "ms");
        }
    }
}
```

---

## 🔍 문제 해결 체크리스트

### 데이터베이스 문제 체크리스트
- [ ] MySQL 서버 실행 상태 확인
- [ ] 데이터베이스 연결 정보 정확성 확인
- [ ] 문자 인코딩 설정 확인
- [ ] 외래키 제약 조건 확인
- [ ] 테이블 구조와 엔티티 매핑 확인

### API 문제 체크리스트
- [ ] 컨트롤러 매핑 경로 확인
- [ ] 요청/응답 형식 확인
- [ ] HTTP 메서드 일치 확인
- [ ] 파라미터 바인딩 확인
- [ ] 예외 처리 구현 확인

### 프론트엔드 문제 체크리스트
- [ ] DOM 로드 순서 확인
- [ ] JavaScript 오류 콘솔 확인
- [ ] API 요청 URL 정확성 확인
- [ ] 이벤트 리스너 등록 확인
- [ ] 전역 변수 초기화 확인

---

## 📞 추가 지원

프로젝트 개발 중 해결되지 않는 문제가 있다면:

1. **로그 확인**: 먼저 애플리케이션 로그와 브라우저 개발자 도구를 확인
2. **단계별 디버깅**: 문제를 작은 단위로 나누어 단계별로 확인
3. **공식 문서 참조**: Spring Boot, JPA, MySQL 공식 문서 확인
4. **커뮤니티 활용**: Stack Overflow, Spring 커뮤니티 검색

---

**이 문서는 프로젝트 개발 과정에서 실제 발생한 문제들을 바탕으로 작성되었습니다.**