# 토이 프로젝트 4 : 챗봇을 넘어 콜봇으로 based on AI (RAG + LLM)
### [프로젝트 개요]
- **프로젝트 명** : 챗봇을 넘어 콜봇으로 based on AI (RAG + LLM)
- **상세 내용 :** [프로젝트 RFP 노션 링크](https://www.notion.so/Toy-Project-4-22f9047c353d80fea377d6a4c4b23415?source=copy_link)
- **수행 및 결과물 제출 기한** : 7/14 (월) ~ 8/1 (금) 14:00
- **멘토진 코드리뷰 기한** : 8/4 (월) ~ 8/17 (일), 2주 간 진행


### [프로젝트 진행 및 제출 방법]
- 본 패스트캠퍼스 Github의 Repository를 각 조별의 Github Repository를 생성 후 Fork합니다.
    - 패스트캠퍼스 깃헙은 Private 형태 (Public 불가)
- 조별 레포의 최종 branch → 패스트캠퍼스 업스트림 Repository의 main branch의 **PR 상태**로 제출합니다.
    - **PR TITLE : N조 최종 제출**
    - Pull Request 링크를 LMS로도 제출해 주셔야 최종 제출 완료 됩니다. (제출자: 조별 대표자 1인)
    - LMS를 통한 과제 미제출 시 점수가 부여되지 않습니다.
- PR 제출 시 유의사항
    - 프로젝트 진행 결과 및 과업 수행 내용은 README.md에 상세히 작성 부탁 드립니다.
    - 멘토님들께서 어플리케이션 실행을 위해 확인해야 할 환경설정 값 등도 반드시 PR 부가 설명란 혹은 README.md에 작성 부탁 드립니다.
    - **Pull Request에서 제출 후 절대 병합(Merge)하지 않도록 주의하세요!**
    - 수행 및 제출 과정에서 문제가 발생한 경우, 바로 질의응답 멘토님이나 강사님에게 얘기하세요! (강사님께서 필요시 개별 힌트 제공)


# 📚 책크인 - AI 기반 온라인 서점 프로젝트

## 프로젝트 소개 Introduction
Spring Boot와 AI 기술을 융합한 지능형 온라인 서점 시스템으로, 사용자와 관리자를 위한 종합적인 도서 쇼핑몰 기능과 **AI 기반 도서 추천 챗봇**을 제공합니다.

### 주요 특징
- 🔐 **사용자/관리자 분리된 인증 시스템**
- 📖 **3단계 계층형 카테고리 구조**
- 🛒 **실시간 재고 연동 장바구니**
- 💳 **KakaoPay API 연동 결제 시스템**
- 📱 **반응형 웹 디자인**
- ⚡ **캐싱 기반 성능 최적화**
- 🤖 **AI 도서 추천 챗봇 시스템 (RAG + LLM)**
- 🧠 **감정 기반 개인화 추천**
- 🔍 **하이브리드 검색 엔진 (벡터 + 키워드)**

## 📋 목차
- [프로젝트 개요](#프로젝트-개요)
- [기술 스택](#기술-스택)
- [주요 기능](#주요-기능)
- [API 명세서](#api-명세서)
- [설치 및 실행](#설치-및-실행)
- [데이터베이스 설정](#데이터베이스-설정)
- [환경 설정](#환경-설정)
- [트러블슈팅](#트러블슈팅)

## 🎯 프로젝트 개요

### ERD (Entity Relationship Diagram)
![책크인 ERD](src/main/resources/static/layout/책크인_ERD.png)

### 아키텍처
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Presentation  │    │    Business     │    │      Data       │
│   (Controller)  │◄──►│   (Service)     │◄──►│  (Repository)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
│                                                                │
│  - @Controller        │  - @Service          │  - @Repository  │
│  - REST API           │  - 비즈니스 로직      │  - JPA/Hibernate│
│  - Thymeleaf          │  - 트랜잭션 관리      │  - MySQL 연동   │
└────────────────────────────────────────────────────────────────┘
```

## 🛠 기술 스택

### Backend (Java Spring Boot)
- **Java 17** - 최신 LTS 버전
- **Spring Boot 3.3.1** - 웹 애플리케이션 프레임워크
- **Spring Data JPA** - ORM 및 데이터 액세스
- **Spring Web** - RESTful API 개발
- **Hibernate** - ORM 구현체
- **MySQL 8.0** - 관계형 데이터베이스

### AI Service (Python FastAPI)
- **Python 3.11+** - AI 서비스 백엔드
- **FastAPI** - AI API 서버 프레임워크
- **LangChain** - LLM 오케스트레이션 프레임워크
- **OpenAI GPT-4** - 대화형 AI 모델
- **ChromaDB** - 벡터 데이터베이스
- **OpenAI Embeddings** - 문서 임베딩 생성

### Frontend
- **Thymeleaf** - 서버 사이드 템플릿 엔진
- **HTML5/CSS3** - 마크업 및 스타일링
- **JavaScript ES6+** - 클라이언트 사이드 로직
- **부트스트랩 스타일** - 반응형 디자인

### 외부 API & AI 서비스
- **KakaoPay API** - 결제 시스템
- **JavaMail API** - 이메일 발송 (아이디/비밀번호 찾기)
- **OpenAI API** - GPT-4 및 임베딩 서비스
- **Aladin API** - 도서 메타데이터 수집
- **Kakao Book API** - 추가 도서 정보 수집

### 개발 도구
- **IntelliJ IDEA** - 통합 개발 환경
- **Maven** - 의존성 관리 및 빌드 도구
- **Git & GitHub** - 버전 관리
- **MySQL** - 데이터베이스 관리
- **Docker & Docker Compose** - 컨테이너 기반 배포
- **VS Code** - Python AI 서비스 개발

## ✨ 주요 기능

### 👤 사용자 기능

#### 🔐 **회원 관리**
- ✅ 회원가입 (실명인증, 이메일 중복검사)
- ✅ 로그인/로그아웃 (30분 세션 관리)
- ✅ 아이디/비밀번호 찾기 (이메일 발송)
- ✅ 회원정보 수정
- ✅ 휴면계정 관리 (스케줄러 기반)

#### 📖 **상품 조회**
- ✅ 메인 페이지 (베스트셀러, 신상품, 인기검색어)
- ✅ 카테고리별 상품 브라우징 (대분류 > 중분류 > 소분류)
- ✅ 상품 검색 (일반검색, 상세검색)
- ✅ 상품 상세 정보 (재고, 리뷰, 평점)
- ✅ 최근 본 상품 (로컬 스토리지 기반)

#### 🛒 **장바구니**
- ✅ 상품 추가/수정/삭제
- ✅ 실시간 재고 확인 (API 캐싱)
- ✅ 수량 조절 (재고량 초과 방지)
- ✅ 선택 상품 주문
- ✅ 페이지네이션 (10개씩)

#### 💳 **주문/결제**
- ✅ 주문서 작성 (배송지, 수량 확인)
- ✅ KakaoPay 결제 연동
- ✅ 주문 상태 추적 (7단계)
- ✅ 주문 취소
- ✅ 주문 내역 조회

#### ⭐ **리뷰 시스템**
- ✅ 리뷰 작성/수정/삭제
- ✅ 평점 시스템 (1-5점)
- ✅ 리뷰 페이지네이션
- ✅ Soft Delete 지원

#### 🤖 **AI 챗봇 기능**
- ✅ 감정 기반 도서 추천
- ✅ 자연어 대화 인터페이스
- ✅ 개인화된 추천 시스템
- ✅ 세션 기반 대화 관리
- ✅ 의도 분류 및 쿼리 분석
- ✅ RAG (Retrieval-Augmented Generation) 기반 검색
- ✅ 하이브리드 검색 (벡터 + 키워드)
- ✅ 실시간 clarification 처리

### 👨‍💼 관리자 기능

#### 📦 **상품 관리**
- ✅ 상품 등록/수정/삭제
- ✅ 재고 관리 (입고/출고 이력)
- ✅ 상품 상태 변경 (판매중/품절/절판/입고예정)
- ✅ 카테고리 관리
- ✅ 상품 검색/필터링 (상세검색)

#### 📋 **주문 관리**
- ✅ 주문 내역 조회
- ✅ 주문 상태 변경
- ✅ 기간별 주문 검색
- ✅ 주문 상세 정보 확인

#### 👥 **회원 관리**
- ✅ 회원 정보 조회
- ✅ 회원 검색 (다중 조건)
- ✅ 회원별 주문 내역 확인
- ✅ 회원 상태 관리

#### 🔒 **관리자 권한 제어**
- ✅ 관리자 전용 페이지 접근 제한
- ✅ 일반 사용자 기능 차단 (장바구니, 마이페이지)
- ✅ URL 직접 접속 차단

### 🤖 AI 서비스 기능

#### 🧠 **추천 에이전트 (`recommend_agent.py`)**
- ✅ 감정, 장르, 키워드 기반 도서 추천
- ✅ MMR(Maximum Marginal Relevance) 기반 다양성 검색
- ✅ 벡터 데이터베이스 활용한 유사도 검색

#### 📚 **위키 검색 에이전트 (`wiki_search_agent.py`)**
- ✅ 작가 정보 검색 및 제공
- ✅ 도서 관련 정보 검색
- ✅ 구조화된 응답 생성

#### 🎯 **메인 에이전트 (`main_agent.py`)**
- ✅ 사용자 의도 분류 (`intent_classify_chain.py`)
- ✅ 쿼리 분석 (`query_analysis_chain.py`)
- ✅ 세션 관리 및 대화 히스토리 추적
- ✅ 에이전트 라우팅 (`intent_router.py`)

## 🌐 API 명세서

### 📋 **인증 관련 API**
| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/login` | 로그인 페이지 | - | HTML |
| POST | `/login` | 로그인 처리 | `LoginRequest` | Redirect |
| POST | `/logout` | 로그아웃 | - | Redirect |
| GET | `/register` | 회원가입 페이지 | - | HTML |
| POST | `/api/register` | 회원가입 처리 | `RegisterRequest` | `RegisterResponse` |
| POST | `/findId` | 아이디 찾기 | `name, email` | String |
| POST | `/findPassword` | 비밀번호 찾기 | `idForUser, email` | String |

### 📖 **상품 관련 API**
| Method | Endpoint | Description | Parameters | Response |
|--------|----------|-------------|------------|----------|
| GET | `/main` | 메인 페이지 | - | HTML + 베스트셀러/신상품 |
| GET | `/product/detail/{isbn}` | 상품 상세 | `isbn`, `page` | `Product` + 리뷰 |
| GET | `/product/category/low/{categoryId}` | 카테고리별 상품 | `categoryId`, `page`, `size`, `sort` | `ProductListPageResponse` |
| GET | `/product/search` | 일반 검색 | `q`, `page`, `size`, `sort` | `ProductListPageResponse` |
| GET | `/product/search-advanced` | 상세 검색 | `title`, `author`, `publisher` | `ProductListPageResponse` |
| GET | `/api/popular-keywords` | 인기 검색어 Top 10 | - | `List<ProductSimpleResponse>` |
| GET | `/api/bestseller` | 베스트셀러 | `period` (week/month/year) | `List<ProductSimpleResponse>` |
| GET | `/api/newproducts` | 신상품 Top 10 | - | `List<ProductSimpleResponse>` |

### 🛒 **장바구니 API**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/cart` | 장바구니 페이지 | - | HTML |
| POST | `/cart/add` | 상품 추가 | `isbn`, `quantity` | String |
| POST | `/cart/add-bulk` | 일괄 추가 | `List<String> isbns` | String |
| POST | `/cart/check` | 중복 상품 확인 | `List<String> isbns` | `Map<String, Object>` |
| POST | `/cart/update` | 수량 변경 | `isbn`, `quantity` | String |
| POST | `/cart/delete` | 상품 삭제 | `isbn` | String |
| GET | `/cart/list` | 장바구니 목록 | - | `List<CartItemResponse>` |
| GET | `/product/api/stock/{isbn}` | 재고 확인 | `isbn` | `Map<String, Integer>` |

### 🤖 **AI 채팅 API**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/api/chat/message` | 채팅 메시지 전송 | `{"message": "사용자 메시지"}` | `Map<String, Object>` |
| GET | `/health` | AI 서비스 상태 확인 | - | `{"status": "healthy"}` |
| POST | `/api/chat` | AI 챗봇 대화 (FastAPI) | `ChatRequest` | `{"response": "AI 응답", "success": true}` |

### 💳 **주문/결제 API**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/order` | 주문 페이지 | - | HTML |
| POST | `/api/order/create` | 주문 생성 | `OrderRequest` | `Map<String, Object>` |
| POST | `/api/payment/attempt` | 결제 시도 | `PaymentRequest` | KakaoPay Response |
| POST | `/api/payment/complete` | 결제 완료 | `paymentId`, `pgToken` | Redirect |
| POST | `/api/payment/fail` | 결제 실패 | `paymentId` | Redirect |
| GET | `/order/summary` | 주문 요약 | `orderId` | HTML |
| POST | `/api/orders/cancel` | 주문 취소 | `orderId`, `idForAdmin` | String |

### 👤 **마이페이지 API**
| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/mypage` | 마이페이지 | - | HTML + 사용자 정보 |
| POST | `/api/user/update` | 회원정보 수정 | `UserUpdateRequest` | String |
| GET | `/api/user/orders` | 주문 내역 | `page`, `size` | `List<OrderHistoryResponse>` |

### ⭐ **리뷰 API**
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/api/review/write` | 리뷰 작성 | `ReviewRequest` | String |
| POST | `/api/review/edit` | 리뷰 수정 | `ReviewRequest` | String |
| POST | `/api/review/delete` | 리뷰 삭제 | `reviewId` | String |

### 👨‍💼 **관리자 API**

#### 상품 관리
| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/admin/product-inquiry` | 상품 조회 페이지 | 필터 파라미터들 | HTML |
| POST | `/admin/api/products/{isbn}/stock-in` | 입고 처리 | `quantity` | String |
| POST | `/admin/api/products/{isbn}/status` | 상태 변경 | `status` | String |
| POST | `/admin/api/products/{isbn}/price` | 가격 변경 | `price` | String |
| POST | `/admin/api/product/register` | 상품 등록 | `ProductRequest` | String |
| GET | `/admin/api/categories` | 카테고리 목록 | - | `CategoryTreeResponse` |

#### 주문 관리
| Method | Endpoint | Description | Parameters | Response |
|--------|----------|-------------|------------|----------|
| GET | `/admin/order-inquiry` | 주문 조회 페이지 | 검색 조건들 | HTML |
| GET | `/admin/api/orders` | 주문 목록 API | `page`, 필터 조건들 | `AdminOrderPageResponse` |
| POST | `/admin/api/orders/{orderId}/status` | 주문 상태 변경 | `idForAdmin`, `status` | String |

#### 회원 관리
| Method | Endpoint | Description | Parameters | Response |
|--------|----------|-------------|------------|----------|
| GET | `/admin/user-inquiry` | 회원 조회 페이지 | 검색 조건들 | HTML |
| GET | `/admin/api/users` | 회원 목록 API | `page`, 필터 조건들 | `Page<User>` |
| GET | `/admin/api/users/{idForAdmin}/orders` | 특정 회원 주문 내역 | `idForAdmin` | `List<AdminOrderHistoryResponse>` |

## 🚀 설치 및 실행

### 사전 요구사항
- **Java 17** 이상
- **Python 3.11** 이상
- **Maven 3.6** 이상
- **MySQL 8.0** 이상
- **Docker & Docker Compose** (선택사항)
- **Git**
- **OpenAI API Key** (AI 기능 사용시 필수)

### 1. 프로젝트 클론
```bash
git clone https://github.com/your-username/KDT_BE12_Toy_Project4.git
cd KDT_BE12_Toy_Project4
```

### 2. 데이터베이스 설정

#### AWS RDS 사용 (현재 프로젝트 방식)
1. AWS RDS MySQL 인스턴스 생성
2. 보안 그룹에서 3306 포트 열기
3. `application.properties`에 RDS 엔드포인트 설정

#### 로컬 MySQL 사용 (개발용)
```sql
CREATE DATABASE tp4team5 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bookstore_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON tp4team5.* TO 'bookstore_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Docker MySQL 사용
```bash
docker run --name mysql-bookstore \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=tp4team5 \
  -e MYSQL_USER=bookstore_user \
  -e MYSQL_PASSWORD=your_password \
  -p 3306:3306 -d mysql:8.0
```

### 3. 애플리케이션 설정 파일 생성
`src/main/resources/application.properties` 파일을 생성하고 다음 내용을 입력하세요:

```properties
# 애플리케이션 이름
spring.application.name=KDT_BE12_Toy_Project4

# 데이터베이스 설정 (AWS RDS)
spring.datasource.url=jdbc:mysql://your-rds-endpoint:3306/your_database?serverTimezone=Asia/Seoul
spring.datasource.username=your_db_username
spring.datasource.password=your_db_password

# 데이터베이스 연결 풀 설정 (HikariCP)
spring.datasource.hikari.maximum-pool-size=5
spring.datasource.hikari.minimum-idle=2
spring.datasource.hikari.connection-timeout=20000
spring.datasource.hikari.idle-timeout=300000
spring.datasource.hikari.max-lifetime=1200000
spring.datasource.hikari.leak-detection-threshold=60000

# UTF-8 인코딩 설정 (강화)
server.servlet.encoding.charset=UTF-8
server.servlet.encoding.enabled=true
server.servlet.encoding.force=true
server.servlet.encoding.force-request=true
server.servlet.encoding.force-response=true

# Thymeleaf 설정
spring.thymeleaf.encoding=UTF-8
spring.thymeleaf.mode=HTML
spring.thymeleaf.cache=false
spring.thymeleaf.servlet.content-type=text/html; charset=UTF-8

# HTTP 메시지 컨버터 인코딩
spring.http.encoding.charset=UTF-8
spring.http.encoding.enabled=true
spring.http.encoding.force=true

# 추가 인코딩 설정
spring.messages.encoding=UTF-8
spring.banner.charset=UTF-8

# JPA 설정
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQLDialect
spring.jpa.properties.hibernate.format_sql=true
logging.level.org.hibernate.SQL=debug
logging.level.org.hibernate.type.descriptor.sql=trace
logging.level.org.hibernate.orm.jdbc.bind=trace
logging.level.org.hibernate.orm.jdbc=trace
logging.level.org.hibernate=debug
logging.level.org.hibernate.type=trace

# 이메일 설정 (Gmail SMTP)
spring.mail.host=smtp.gmail.com
spring.mail.port=587
spring.mail.username=your_email@gmail.com
spring.mail.password=your_app_password
spring.mail.properties.mail.smtp.auth=true
spring.mail.properties.mail.smtp.starttls.enable=true
spring.mail.default-encoding=UTF-8

# 발신자 정보
mail.sender.email=your_email@gmail.com
mail.sender.name=책크인 관리자

# KakaoPay 설정
kakaopay.admin-key=your_kakaopay_admin_key
kakaopay.cid=TC0ONETIME

# AI 서비스 설정 (토글 가능)
ai.service.enabled=true
ai.service.base-url=http://localhost:8000
ai.service.timeout=30000
ai.service.fallback-to-java=true

# OpenAI API 키 (Java에서 직접 사용)
openai.api.key=${OPENAI_API_KEY:}
openai.api.url=https://api.openai.com/v1/chat/completions
openai.model=gpt-3.5-turbo
openai.max-tokens=1000
openai.temperature=0.7
```

**⚠️ 중요 설정 안내:**

### 데이터베이스 설정
- **AWS RDS**: 실제 프로젝트는 AWS RDS MySQL을 사용
- **로컬 개발**: MySQL 로컬 설치 또는 Docker MySQL 컨테이너 사용

### AI 서비스 URL 설정
| 환경 | AI 서비스 URL | 설명 |
|------|------------|------|
| 로컬 개발 | `http://localhost:8000` | 개별 실행 시 |
| Docker Compose | `http://ai-service:8000` | 컨테이너 내부 통신 |
| AWS/원격 | `http://your-domain:8000` | 원격 서버 주소 |

### 환경변수 설정 필수
```bash
# 환경변수로 설정
export OPENAI_API_KEY=your_openai_api_key_here

# 또는 application.properties에 직접 입력
openai.api.key=your_openai_api_key_here
```

### 4. AI 서비스 설정 (Python)
`ai-service` 디렉토리로 이동하여 Python 환경 설정:
```bash
cd ai-service
python -m venv ai_venv
# Windows
ai_venv\Scripts\activate
# Linux/Mac
source ai_venv/bin/activate

pip install -r requirements.txt
```

### 5. AI 서비스 환경 변수 설정
`ai-service/.env` 파일 생성:
```env
# OpenAI API 설정
OPENAI_API_KEY=your_openai_api_key_here

# 벡터 데이터베이스 설정
CHROMA_DB_PATH=./data/chroma_db
COLLECTION_NAME=bookstore_collection

# 서비스 설정
FAST_API_HOST=0.0.0.0
FAST_API_PORT=8000
```

### 6. 벡터 데이터베이스 (ChromaDB) 설정

#### 초기 벡터DB 생성
```bash
cd ai-service
# 벡터DB 디렉토리 생성
mkdir -p data/chroma_db

# 벡터DB 상태 확인
python data/prompts/check_vector_db.py
```

#### 도서 데이터 임베딩 (선택사항)
```bash
# 전처리된 도서 데이터가 있는 경우
cd data/prompts/preprocessing
python product_extract.py  # 도서 정보 추출
python emotion_extract.py  # 감정 키워드 추출
python generate_reviews.py # 리뷰 데이터 생성
```

### 7. Docker 설정 (권장 방법)

#### Docker Compose 환경변수 설정
프로젝트 루트에 `.env` 파일 생성:
```env
# MySQL 설정
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=bookstore_db
MYSQL_USER=bookstore_user
MYSQL_PASSWORD=your_database_password

# AI 서비스 설정
OPENAI_API_KEY=your_openai_api_key_here
AI_SERVICE_BASE_URL=http://ai-service:8000
```

#### Docker Compose 실행
```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그 확인
docker-compose logs ai-service
docker-compose logs spring-app

# 서비스 중지
docker-compose down
```

#### Docker 개별 빌드 (필요시)
```bash
# AI 서비스 빌드
cd ai-service
docker build -t bookstore-ai .

# Spring Boot 앱 빌드
docker build -t bookstore-app .
```

### 8. 애플리케이션 실행

#### 방법 1: Docker Compose 사용 (권장)
```bash
# 전체 시스템 시작
docker-compose up -d

# 상태 확인
docker-compose ps
```

#### 방법 2: 개별 실행
**1단계: MySQL 시작 (로컬 설치 또는 Docker)**
```bash
# Docker로 MySQL만 실행
docker run --name mysql-bookstore \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=bookstore_db \
  -e MYSQL_USER=bookstore_user \
  -e MYSQL_PASSWORD=your_password \
  -p 3306:3306 -d mysql:8.0
```

**2단계: AI 서비스 시작**
```bash
cd ai-service
# 가상환경 활성화
ai_venv\Scripts\activate  # Windows
# source ai_venv/bin/activate  # Linux/Mac

# 서비스 시작
python main.py
```

**3단계: Spring Boot 서버 시작**
```bash
# 별도 터미널에서
mvn clean install
mvn spring-boot:run

# 또는 IDE에서 AIToyProjectApplication.java 실행
```

#### 방법 3: 스크립트 사용
```bash
# Windows
scripts\start.bat

# Linux/Mac
chmod +x scripts/start.sh
./scripts/start.sh
```

### 9. 접속 확인 및 테스트

#### 서비스 접속
- **메인 웹사이트**: `http://localhost:8080`
- **AI 서비스**: `http://localhost:8000`
- **AI 서비스 헬스체크**: `http://localhost:8000/health`

#### AI 챗봇 테스트
```bash
# AI 서비스 직접 테스트
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "우울할 때 읽을 책 추천해줘"}'
```

#### 벡터DB 상태 확인
```bash
cd ai-service
python data/prompts/check_vector_db.py
```

#### Docker 컨테이너 상태 확인
```bash
# 컨테이너 상태
docker-compose ps

# 네트워크 확인
docker network ls | grep bookstore

# 볼륨 확인
docker volume ls | grep bookstore
```

## 🗄 데이터베이스 설정

### 샘플 데이터 구성
프로젝트 실행 후 다음 순서로 데이터를 구성하세요:

1. **관리자 계정 생성**
```sql
INSERT INTO admin (admin_id, admin_pwd, admin_name, admin_status) 
VALUES ('admin', 'admin123', '시스템 관리자', 'ACTIVE');
```

2. **사용자 등급 설정**
```sql
INSERT INTO user_grade (user_grade_id, user_grade_name, grade_criteria_start_price, grade_criteria_end_price) VALUES
('BRONZE', '브론즈', 0, 99999),
('SILVER', '실버', 100000, 299999),
('GOLD', '골드', 300000, 499999),
('PLATINUM', '플래티넘', 500000, 999999);
```

3. **카테고리 구조 생성**
```sql
-- 대분류
INSERT INTO top_category (top_category_name) VALUES
('문학'), ('인문'), ('사회과학'), ('자연과학'), ('기술공학');

-- 중분류 (예시)
INSERT INTO middle_category (top_category, mid_category_name) VALUES
(1, '한국문학'), (1, '외국문학'), (2, '철학'), (2, '역사');

-- 소분류 (예시)  
INSERT INTO low_category (mid_category, low_category_name) VALUES
(1, '소설'), (1, '시'), (2, '소설'), (3, '동양철학');
```

4. **결제 방법 설정**
```sql
INSERT INTO payment_method (payment_method_id, payment_method_name, is_active) VALUES
('KAKAO_PAY', '카카오페이', true),
('BANK_TRANSFER', '계좌이체', true);
```

### 데이터베이스 백업/복원
프로젝트에는 데이터베이스 구조와 샘플 데이터를 포함한 SQL 파일이 제공됩니다:
- `RDB/full_export.sql` - 테이블 구조 및 샘플 데이터

#### 데이터베이스 복원 방법
```bash
  # 실제 운영 데이터로 복원 (추천)
  mysql -u bookstore_user -p bookstore_db < database/full_export.sql
```

## ⚙️ 환경 설정

### 필수 설정 항목

#### 1. KakaoPay API 설정
1. [Kakao Developers](https://developers.kakao.com) 에서 앱 생성
2. 결제 서비스 활성화
3. Admin Key 발급
4. `application.properties`에 설정

#### 2. 이메일 설정 (Gmail 기준)
1. Gmail 계정에서 앱 비밀번호 생성
2. `application.properties`에 이메일 정보 설정

#### 3. 보안 설정 (운영 환경)
```properties
# 운영 환경에서는 반드시 변경
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.show-sql=false
logging.level.org.hibernate.SQL=WARN
```

### 선택 설정 항목

#### 1. 이미지 업로드 경로
```properties
file.upload.path=/path/to/upload/directory
```

#### 2. 세션 설정
```properties
server.servlet.session.timeout=30m
server.servlet.session.cookie.max-age=1800
```

## 🚨 트러블슈팅

주요 트러블슈팅 내용은 별도 문서를 참조하세요:
- [📋 TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 상세 트러블슈팅 가이드

### 자주 발생하는 문제

#### 1. 데이터베이스 연결 실패
```
Could not create connection to database server
```
**해결방법:**
- MySQL 서버 실행 상태 확인
- 데이터베이스 계정 권한 확인
- 포트 번호 확인 (기본: 3306)

#### 2. KakaoPay API 오류
```
카카오페이 결제 준비 실패
```
**해결방법:**
- Admin Key 확인
- CID 확인
- 네트워크 연결 상태 확인

#### 3. 이메일 발송 실패
```
Failed to send email
```
**해결방법:**
- Gmail 앱 비밀번호 확인
- SMTP 포트 확인 (587)
- 방화벽 설정 확인

## 🧪 테스트 계정

### 관리자 계정
- **ID**: `admin_1`
- **Password**: `admin1!`

### 일반 사용자 계정 (샘플 데이터 로드 후)
- **ID**: `fastcampus`
- **Password**: `fast123!`

## 📂 프로젝트 구조
```
KDT_BE12_Toy_Project4/
├── src/main/java/bookstore_ai_project/       # Spring Boot 메인 애플리케이션
│   ├── config/                               # 설정 클래스 (SecurityConfig, WebConfig)
│   ├── controller/                           # 컨트롤러 (AIChatController, ProductController 등)
│   ├── dto/                                  # 데이터 전송 객체
│   ├── entity/                               # JPA 엔티티
│   ├── repository/                           # 데이터 액세스 레이어
│   ├── service/                              # 비즈니스 로직 (AIChatService 등)
│   └── scheduler/                            # 스케줄러 (DormantCheckScheduler)
├── ai-service/                               # Python AI 서비스
│   ├── app/
│   │   ├── agents/
│   │   │   ├── recommend_agent.py            # 도서 추천 에이전트
│   │   │   └── wiki_search_agent.py          # 위키 검색 에이전트
│   │   ├── chains/
│   │   │   ├── intent_classify_chain.py      # 의도 분류 체인
│   │   │   ├── query_analysis_chain.py       # 쿼리 분석 체인
│   │   │   ├── clarification_chain.py        # 명확화 체인
│   │   │   └── wiki_search_chain.py          # 위키 검색 체인
│   │   ├── main_agent/
│   │   │   ├── main_agent.py                 # 메인 에이전트
│   │   │   └── intent_router.py              # 의도 라우터
│   │   ├── config/
│   │   │   └── llm.py                        # LLM 설정
│   │   ├── prompts/                          # 프롬프트 템플릿
│   │   ├── utils/                            # 유틸리티 함수
│   │   └── models/                           # 데이터 모델
│   ├── data/
│   │   ├── chroma_db/                        # 벡터 데이터베이스
│   │   └── prompts/
│   │       ├── search_engine.py              # 하이브리드 검색 엔진
│   │       └── preprocessing/                # 데이터 전처리 스크립트
│   ├── main.py                               # FastAPI 서버
│   └── requirements.txt                      # Python 의존성
├── scripts/                                  # 운영 스크립트
│   ├── start.bat, start.sh                   # 서비스 시작 스크립트
│   ├── stop.bat, stop.sh                     # 서비스 중지 스크립트
│   └── chromadb_reset.bat                    # 벡터DB 초기화
├── docker-compose.yml                        # Docker Compose 설정
└── README.md, TROUBLESHOOTING.md             # 문서
```

## 🔧 성능 최적화

### 캐싱 전략
- 재고 조회 API 캐싱 (30초)
- 인기 검색어 캐싱 (1시간)
- 카테고리 구조 캐싱 (세션별)

### 데이터베이스 최적화
- 지연 로딩 (Lazy Loading) 전략
- 복합키 인덱스 활용
- 쿼리 최적화 (N+1 문제 해결)

### AI 서비스 최적화
- **MMR 기반 다양성 검색** (`k=3, fetch_k=10, lambda_mult=0.7`)
- **하이브리드 스코어링 시스템** (감정키워드 +4점, 제품키워드 +3점)
- **벡터 임베딩 캐싱** (ChromaDB 영구 저장)
- **세션 기반 대화 관리** (브라우저 종료까지 유지)
- **클라이언트 사이드 캐싱** (30초 TTL)

## 🚀 배포 정보

### 개발 환경
- **Java**: OpenJDK 17
- **Spring Boot**: 3.3.1
- **MySQL**: 8.0.33
- **Port**: 8080

### 운영 환경 고려사항
- SSL 인증서 적용 필요
- 데이터베이스 성능 튜닝
- 로드 밸런싱 구성
- 보안 강화 (비밀번호 암호화 등)

## 🤝 기여하기
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

---

**책크인** - Spring Boot로 구현한 종합 온라인 서점 시스템