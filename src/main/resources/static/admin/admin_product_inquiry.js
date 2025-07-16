// 관리자 상품조회 페이지 JavaScript (product_list.js + header.js 카테고리 로직)

document.addEventListener('DOMContentLoaded', function() {
    // 전역 변수
    let currentCategoryId = null;
    let currentCategoryPath = '상품목록';
    let currentPage = 1;
    let currentSize = 30;
    let currentSort = 'latest';
    let searchParams = {};
    let categoryData = null;

    // DOM 요소들
    const categoryTitle = document.getElementById('categoryTitle');
    const menuToggle = document.getElementById('menuToggle');
    const menuDropdown = document.getElementById('menuDropdown');
    const menuCloseBtn = document.getElementById('menuCloseBtn');
    const topCategoryContainer = document.getElementById('topCategoryContainer');
    const subCategoryContainer = document.getElementById('subCategoryContainer');
    const detailSearchForm = document.getElementById('detailSearchForm');
    const sortSelect = document.getElementById('sortSelect');
    const pageSizeSelect = document.getElementById('pageSizeSelect');
    const productList = document.getElementById('productList');
    const paginationBtns = document.getElementById('paginationBtns');

    // 초기화
    init();

    function init() {
        loadCategories();
        loadProducts();
        setupEventListeners();
    }

    function setupEventListeners() {
        // 전체메뉴 버튼 이벤트 (header.js와 동일)
        if (menuToggle) {
            menuToggle.addEventListener('click', function() {
                const isActive = menuDropdown.classList.contains('active');
                if (isActive) {
                    closeMenu();
                } else {
                    openMenu();
                }
            });
        }

        // 메뉴 닫기 버튼
        if (menuCloseBtn) {
            menuCloseBtn.addEventListener('click', closeMenu);
        }

        // 외부 클릭 시 메뉴 닫기
        document.addEventListener('click', function(event) {
            if (!menuToggle.contains(event.target) && !menuDropdown.contains(event.target)) {
                closeMenu();
            }
        });

        // 상세검색 폼 이벤트
        if (detailSearchForm) {
            detailSearchForm.addEventListener('submit', function(e) {
                e.preventDefault();
                handleSearch();
            });
        }

        // 초기화 버튼 이벤트
        const resetSearchBtn = document.getElementById('resetSearchBtn');
        if (resetSearchBtn) {
            resetSearchBtn.addEventListener('click', function(e) {
                e.preventDefault();
                resetSearchForm();
            });
        }

        // 정렬 변경
        if (sortSelect) {
            sortSelect.addEventListener('change', function() {
                currentSort = this.value;
                currentPage = 1;
                loadProducts();
            });
        }

        // 페이지 크기 변경
        if (pageSizeSelect) {
            pageSizeSelect.addEventListener('change', function() {
                currentSize = parseInt(this.value);
                currentPage = 1;
                loadProducts();
            });
        }
    }

    function openMenu() {
        menuDropdown.classList.add('active');
        menuToggle.setAttribute('aria-expanded', 'true');
        // 스크롤 방지 제거 - 관리자 페이지에서는 레이아웃에 영향을 주지 않도록
    }

    function closeMenu() {
        menuDropdown.classList.remove('active');
        menuToggle.setAttribute('aria-expanded', 'false');
        // 스크롤 복원 제거 - 관리자 페이지에서는 불필요
        
        // 모든 서브카테고리 숨기기
        document.querySelectorAll('.sub-category-content').forEach(content => {
            content.classList.remove('active');
        });
        document.querySelectorAll('.top-category-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelectorAll('.low-category-list').forEach(list => {
            list.classList.remove('active');
        });
        
        // 기본 메시지 표시
        const defaultMessage = document.querySelector('.default-message');
        if (defaultMessage) {
            defaultMessage.style.display = 'block';
        }
    }

    // 카테고리 트리 로드
    function loadCategories() {
        fetch('/admin/api/categories')
            .then(response => response.json())
            .then(data => {
                categoryData = data;
                renderCategoryTree(data);
                loadCategoryCounts(); // 카테고리별 책 개수 로드
            })
            .catch(error => {
                console.error('카테고리 로드 실패:', error);
            });
    }

    // 카테고리별 책 개수 로드
    function loadCategoryCounts() {
        // 모든 레벨의 카테고리별 책 개수 + 전체 상품 개수 로드
        Promise.all([
            fetch('/admin/api/category-counts/top').then(response => response.json()),
            fetch('/admin/api/category-counts/middle').then(response => response.json()),
            fetch('/admin/api/category-counts/low').then(response => response.json()),
            fetch('/admin/api/total-product-count').then(response => response.json())
        ])
        .then(([topCounts, middleCounts, lowCounts, totalCount]) => {
            console.log('카테고리 개수 데이터:', { topCounts, middleCounts, lowCounts, totalCount }); // 디버깅용
            updateCategoryCountsInUI({ topCounts, middleCounts, lowCounts, totalCount });
        })
        .catch(error => {
            console.error('카테고리 개수 로드 실패:', error);
        });
    }

    // UI에 카테고리 개수 업데이트
    function updateCategoryCountsInUI(counts) {
        // 잠시 대기하여 DOM이 완전히 렌더링된 후 업데이트
        setTimeout(() => {
            const { topCounts, middleCounts, lowCounts, totalCount } = counts;
            
            // 전체 상품 개수 업데이트
            const allProductsBtn = document.querySelector('.all-products-btn');
            if (allProductsBtn && totalCount > 0) {
                updateCategoryCount(allProductsBtn, totalCount);
            }
            
            // 대분류 수량 업데이트
            topCounts.forEach(count => {
                if (count.bookCount > 0) {
                    const categoryElement = document.querySelector(`[data-category-id="${count.topCategory}"]`);
                    if (categoryElement && categoryElement.classList.contains('top-category-button')) {
                        updateCategoryCount(categoryElement, count.bookCount);
                    }
                }
            });
            
            // 중분류 수량 업데이트
            middleCounts.forEach(count => {
                if (count.bookCount > 0) {
                    const categoryElement = document.querySelector(`[data-category-id="${count.midCategory}"]`);
                    if (categoryElement && categoryElement.classList.contains('middle-category-button')) {
                        // 중분류는 첫 번째 span에 추가 (화살표 span 이전)
                        updateCategoryCountForMiddle(categoryElement, count.bookCount);
                    }
                }
            });
            
            // 소분류 수량 업데이트
            lowCounts.forEach(count => {
                if (count.bookCount > 0) {
                    const categoryElement = document.querySelector(`[data-low-category-id="${count.lowCategory}"]`);
                    if (categoryElement) {
                        updateCategoryCount(categoryElement, count.bookCount);
                    }
                }
            });
        }, 100);
    }
    
    // 카테고리 수량 표시 헬퍼 함수
    function updateCategoryCount(element, bookCount) {
        // 기존 개수 표시 제거
        const existingCount = element.querySelector('.category-count');
        if (existingCount) {
            existingCount.remove();
        }
        
        // 새로운 개수 표시 추가 (수량이 0보다 클 때만)
        if (bookCount > 0) {
            const countSpan = document.createElement('span');
            countSpan.className = 'category-count';
            countSpan.textContent = ` (${bookCount})`;
            countSpan.style.color = '#999';
            countSpan.style.fontSize = '12px';
            element.appendChild(countSpan);
        }
    }
    
    // 중분류 카테고리 수량 표시 헬퍼 함수 (카테고리명 바로 뒤에 삽입)
    function updateCategoryCountForMiddle(element, bookCount) {
        // 기존 개수 표시 제거
        const existingCount = element.querySelector('.category-count');
        if (existingCount) {
            existingCount.remove();
        }
        
        // 새로운 개수 표시 추가 (수량이 0보다 클 때만)
        if (bookCount > 0) {
            const countSpan = document.createElement('span');
            countSpan.className = 'category-count';
            countSpan.textContent = ` (${bookCount})`;
            countSpan.style.color = '#999';
            countSpan.style.fontSize = '12px';
            
            // 카테고리명 span 바로 뒤에 삽입
            const categoryNameSpan = element.querySelector('span:first-child');
            if (categoryNameSpan) {
                categoryNameSpan.appendChild(countSpan);
            } else {
                element.appendChild(countSpan);
            }
        }
    }

    // 카테고리 트리 렌더링 (header.js와 동일한 로직)
    function renderCategoryTree(data) {
        if (!categoryData || !topCategoryContainer) return;

        const { topCategories, middleCategoriesMap, lowCategoriesMap } = data;
        
        // 대분류 목록 렌더링
        let topHtml = '';
        topCategories.forEach(topCategory => {
            topHtml += `
                <div class="top-category-item">
                    <button class="top-category-button" 
                            data-category-id="${topCategory.topCategory}"
                            data-category-name="${topCategory.topCategoryName}">
                        ${topCategory.topCategoryName}
                    </button>
                </div>
            `;
        });
        topCategoryContainer.innerHTML = topHtml;

        // 중분류/소분류 컨테이너 렌더링
        let subHtml = '';
        topCategories.forEach(topCategory => {
            const middleCategories = middleCategoriesMap[topCategory.topCategory] || [];
            
            subHtml += `
                <div class="sub-category-content" id="sub-${topCategory.topCategory}">
                    <h4>${topCategory.topCategoryName}</h4>
                    <div class="middle-category-list">
            `;
            
            middleCategories.forEach(middleCategory => {
                const lowCategories = lowCategoriesMap[middleCategory.midCategory] || [];
                const hasLowCategories = lowCategories.length > 0;
                
                subHtml += `
                    <div class="middle-category-item">
                        <button class="middle-category-button"
                                data-category-id="${middleCategory.midCategory}"
                                data-parent="${topCategory.topCategory}"
                                data-category-name="${middleCategory.midCategoryName}"
                                data-top-name="${topCategory.topCategoryName}">
                            <span>${middleCategory.midCategoryName}</span>
                        </button>
                `;
                
                if (hasLowCategories) {
                    subHtml += `
                        <div class="low-category-list" id="low-${middleCategory.midCategory}">
                    `;
                    
                    lowCategories.forEach(lowCategory => {
                        subHtml += `
                            <div class="low-category-item"
                                 data-low-category-id="${lowCategory.lowCategory}"
                                 data-category-id="${lowCategory.lowCategory}"
                                 data-parent="${middleCategory.midCategory}"
                                 data-category-name="${lowCategory.lowCategoryName}"
                                 data-middle-name="${middleCategory.midCategoryName}"
                                 data-top-name="${topCategory.topCategoryName}">
                                ${lowCategory.lowCategoryName}
                            </div>
                        `;
                    });
                    
                    subHtml += `</div>`;
                }
                
                subHtml += `</div>`;
            });
            
            subHtml += `
                    </div>
                </div>
            `;
        });
        subCategoryContainer.innerHTML = subHtml;

        // 이벤트 리스너 등록
        setupCategoryEventListeners();
    }

    function setupCategoryEventListeners() {
        // 대분류 클릭 이벤트
        document.querySelectorAll('.top-category-button').forEach(btn => {
            btn.addEventListener('click', function() {
                const categoryId = this.dataset.categoryId;
                
                // 다른 대분류 비활성화
                document.querySelectorAll('.top-category-button').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.sub-category-content').forEach(content => content.classList.remove('active'));
                
                // 현재 대분류 활성화
                this.classList.add('active');
                const subContent = document.getElementById(`sub-${categoryId}`);
                if (subContent) {
                    subContent.classList.add('active');
                }
                
                // 기본 메시지 숨기기
                const defaultMessage = document.querySelector('.default-message');
                if (defaultMessage) {
                    defaultMessage.style.display = 'none';
                }
            });
        });

        // 중분류 클릭 이벤트
        document.querySelectorAll('.middle-category-button').forEach(btn => {
            btn.addEventListener('click', function() {
                const categoryId = this.dataset.categoryId;
                const lowCategoryList = document.getElementById(`low-${categoryId}`);
                
                if (lowCategoryList) {
                    // 토글 방식으로 소분류 표시/숨김
                    const isActive = lowCategoryList.classList.contains('active');
                    
                    // 다른 소분류들 모두 숨김
                    document.querySelectorAll('.low-category-list').forEach(list => {
                        list.classList.remove('active');
                    });
                    
                    // 현재 소분류만 토글
                    if (!isActive) {
                        lowCategoryList.classList.add('active');
                    }
                }
            });
        });

        // 소분류 클릭 이벤트 (실제 카테고리 선택)
        document.querySelectorAll('.low-category-item').forEach(item => {
            item.addEventListener('click', function() {
                const categoryId = this.dataset.categoryId;
                const categoryName = this.dataset.categoryName;
                const middleName = this.dataset.middleName;
                const topName = this.dataset.topName;
                
                const path = `${topName} > ${middleName} > ${categoryName}`;
                selectCategory(categoryId, path);
                closeMenu();
            });
        });

        // 전체 상품 버튼 추가 (카테고리 상단에)
        const allProductsBtn = document.createElement('div');
        allProductsBtn.className = 'top-category-item';
        allProductsBtn.innerHTML = `
            <button class="top-category-button all-products-btn" 
                    data-category-id="" 
                    data-category-name="전체상품">
                전체 상품
            </button>
        `;
        topCategoryContainer.insertBefore(allProductsBtn, topCategoryContainer.firstChild);

        // 전체 상품 클릭 이벤트
        allProductsBtn.querySelector('button').addEventListener('click', function() {
            selectCategory(null, '상품목록');
            closeMenu();
        });
    }

    // 카테고리 선택
    function selectCategory(categoryId, categoryPath) {
        currentCategoryId = categoryId;
        currentCategoryPath = categoryPath;
        currentPage = 1;
        
        // 카테고리 변경시 검색조건 초기화
        searchParams = {};
        clearSearchForm();
        
        if (categoryTitle) {
            categoryTitle.textContent = categoryPath;
        }
        
        // 선택된 카테고리 표시
        document.querySelectorAll('.low-category-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        if (categoryId) {
            const selectedItem = document.querySelector(`[data-low-category-id="${categoryId}"]`);
            if (selectedItem) {
                selectedItem.classList.add('selected');
            }
        }
        
        loadProducts();
    }

    // 검색 폼 초기화 (카테고리 변경시)
    function clearSearchForm() {
        if (document.getElementById('searchTitle')) document.getElementById('searchTitle').value = '';
        if (document.getElementById('searchAuthor')) document.getElementById('searchAuthor').value = '';
        if (document.getElementById('searchPublisher')) document.getElementById('searchPublisher').value = '';
        if (document.getElementById('salesStatus')) document.getElementById('salesStatus').value = '';
        if (document.getElementById('startDate')) document.getElementById('startDate').value = '';
        if (document.getElementById('endDate')) document.getElementById('endDate').value = '';
        searchParams = {};
        currentPage = 1;
    }

    // 초기화 버튼 클릭시 검색 폼 초기화 및 재검색 (주문조회와 동일한 로직)
    function resetSearchForm() {
        if (detailSearchForm) {
            detailSearchForm.reset();
        }
        searchParams = {};
        currentPage = 1;
        loadProducts();
    }

    // 검색 처리
    function handleSearch() {
        searchParams = {
            title: document.getElementById('searchTitle')?.value || '',
            author: document.getElementById('searchAuthor')?.value || '',
            publisher: document.getElementById('searchPublisher')?.value || '',
            salesStatus: document.getElementById('salesStatus')?.value || '',
            startDate: document.getElementById('startDate')?.value || '',
            endDate: document.getElementById('endDate')?.value || ''
        };
        
        currentPage = 1;
        loadProducts();
    }

    // 상품 목록 로드
    function loadProducts() {
        let url;
        let params = new URLSearchParams({
            page: currentPage,
            size: currentSize,
            sort: currentSort
        });

        // 검색 파라미터 추가
        Object.entries(searchParams).forEach(([key, value]) => {
            if (value) params.append(key, value);
        });

        if (currentCategoryId) {
            url = `/admin/api/products/category/${currentCategoryId}?${params.toString()}`;
        } else {
            url = `/admin/api/products?${params.toString()}`;
        }

        fetch(url)
            .then(response => response.json())
            .then(data => {
                renderProducts(data.products);
                renderPagination(data);
            })
            .catch(error => {
                console.error('상품 로드 실패:', error);
                if (productList) {
                    productList.innerHTML = '<div class="error-message">상품을 불러오는데 실패했습니다.</div>';
                }
            });
    }

    // 상품 목록 렌더링 (product_list.js와 동일한 구조)
    function renderProducts(products) {
        if (!productList) return;

        if (!products || products.length === 0) {
            productList.innerHTML = '<div class="no-products">조회된 상품이 없습니다.</div>';
            return;
        }

        let html = '';
        products.forEach(product => {
            // 실제 재고 정보 사용
            const stock = product.currentStock || 0;
            let stockClass = 'stock-normal';
            let statusClass = getStatusClass(product.salesStatus);
            let displayStatus = getStatusText(product.salesStatus);

            if (stock === 0) {
                stockClass = 'stock-out';
                statusClass = 'status-out-of-stock';
                displayStatus = '일시품절';
            } else if (stock <= 10) {
                stockClass = 'stock-low';
            }

            html += `
                <div class="product-row">
                    <div class="col-info">
                        <img src="${product.img || '/layout/책크인_이미지.png'}" 
                             alt="${product.productName}" class="product-img">
                        <div class="product-info">
                            <div class="product-title">${product.productName}</div>
                            <div class="product-author">저자: ${product.author}</div>
                            <div class="product-publisher">출판사: ${product.publisher}</div>
                            <div class="product-rating">평점: ${product.rate ? product.rate.toFixed(1) : '0.0'}/10.0</div>
                        </div>
                    </div>
                    <div class="col-status">
                        <span class="${statusClass}">${displayStatus}</span>
                    </div>
                    <div class="col-stock">
                        <span class="stock-count ${stockClass}">${stock}</span>
                    </div>
                    <div class="col-price">${product.price.toLocaleString()}원</div>
                    <div class="col-action">
                        <button class="btn-edit" onclick="handleStockUpdate('${product.isbn}')">입고</button>
                        <button class="btn-status" onclick="handleStatusChange('${product.isbn}')">상태변경</button>
                        <button class="btn-info" onclick="handleProductEdit('${product.isbn}')">정보수정</button>
                    </div>
                </div>
            `;
        });

        productList.innerHTML = html;
    }

    // 판매상태 텍스트 변환
    function getStatusText(status) {
        switch (status) {
            case 'ON_SALE': return '판매중';
            case 'OUT_OF_PRINT': return '절판';
            case 'TEMPORARILY_OUT_OF_STOCK': return '일시품절';
            case 'EXPECTED_IN_STOCK': return '입고예정';
            default: return '판매중';
        }
    }

    // 판매상태 CSS 클래스 변환
    function getStatusClass(status) {
        switch (status) {
            case 'ON_SALE': return 'status-available';
            case 'OUT_OF_PRINT': return 'status-out-of-print';
            case 'TEMPORARILY_OUT_OF_STOCK': return 'status-out-of-stock';
            case 'EXPECTED_IN_STOCK': return 'status-expected';
            default: return 'status-available';
        }
    }

    // 페이징 렌더링 - 개선된 그룹화 페이지네이션
    function renderPagination(data) {
        if (!paginationBtns) return;

        const { currentPage: page, totalPages } = data;
        
        if (totalPages <= 1) {
            paginationBtns.innerHTML = '';
            return;
        }

        // 10개 이하면 기존 방식
        if (totalPages <= 10) {
            let html = '';
            for (let i = 1; i <= totalPages; i++) {
                if (i === page) {
                    html += `<button class="pagination-btn current">${i}</button>`;
                } else {
                    html += `<button class="pagination-btn" onclick="goToPage(${i})">${i}</button>`;
                }
            }
            paginationBtns.innerHTML = html;
            return;
        }

        // 10개 초과시 그룹화 방식
        const currentGroup = Math.ceil(page / 10);
        const startPage = (currentGroup - 1) * 10 + 1;
        const endPage = Math.min(currentGroup * 10, totalPages);
        
        let html = '';
        
        // 처음 버튼 (2그룹 이상일 때)
        if (currentGroup > 1) {
            html += `<button class="pagination-btn first-btn" onclick="goToPage(1)">처음</button>`;
        }
        
        // 이전 그룹 버튼 (2그룹 이상일 때)
        if (currentGroup > 1) {
            const prevGroupLastPage = startPage - 1;
            html += `<button class="pagination-btn prev-group-btn" onclick="goToPage(${prevGroupLastPage})">이전</button>`;
        }
        
        // 현재 그룹의 페이지 번호들
        for (let i = startPage; i <= endPage; i++) {
            if (i === page) {
                html += `<button class="pagination-btn current">${i}</button>`;
            } else {
                html += `<button class="pagination-btn" onclick="goToPage(${i})">${i}</button>`;
            }
        }
        
        // 다음 그룹 버튼 (마지막 그룹이 아닐 때)
        if (endPage < totalPages) {
            const nextGroupFirstPage = endPage + 1;
            html += `<button class="pagination-btn next-group-btn" onclick="goToPage(${nextGroupFirstPage})">다음</button>`;
        }
        
        // 끝 버튼 (마지막 그룹이 아닐 때)
        if (endPage < totalPages) {
            html += `<button class="pagination-btn last-btn" onclick="goToPage(${totalPages})">끝</button>`;
        }

        paginationBtns.innerHTML = html;
    }

    // 페이지 이동
    window.goToPage = function(page) {
        currentPage = page;
        // 맨 위로 즉시 이동
        window.scrollTo(0, 0);
        loadProducts();
    };

    // 입고 처리
    window.handleStockUpdate = function(isbn) {
        showStockUpdateModal(isbn);
    };

    // 상태 변경
    window.handleStatusChange = function(isbn) {
        showStatusChangeModal(isbn);
    };

    // 정보수정 모달
    window.handleProductEdit = function(isbn) {
        showProductEditModal(isbn);
    };

    // 입고 모달 표시
    function showStockUpdateModal(isbn) {
        // 기존 모달 제거
        removeExistingModals();

        const modalHtml = `
            <div id="stockUpdateModal" class="modal-overlay">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>상품 입고</h3>
                        <button class="modal-close" onclick="closeStockUpdateModal()">×</button>
                    </div>
                    <div class="modal-body">
                        <p><strong>ISBN:</strong> ${isbn}</p>
                        <div class="form-group">
                            <label for="stockQuantity">입고 수량:</label>
                            <input type="number" id="stockQuantity" min="1" value="1" class="form-input">
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-save" onclick="confirmStockUpdate('${isbn}')">입고 처리</button>
                        <button class="btn-cancel" onclick="closeStockUpdateModal()">취소</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        setupModalCloseEvents('stockUpdateModal', closeStockUpdateModal);
    }

    // 상태변경 모달 표시
    function showStatusChangeModal(isbn) {
        // 기존 모달 제거
        removeExistingModals();

        const modalHtml = `
            <div id="statusChangeModal" class="modal-overlay">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>상품 상태 변경</h3>
                        <button class="modal-close" onclick="closeStatusChangeModal()">×</button>
                    </div>
                    <div class="modal-body">
                        <p><strong>ISBN:</strong> ${isbn}</p>
                        <div class="form-group">
                            <label for="statusSelect">변경할 상태:</label>
                            <select id="statusSelect" class="form-select">
                                <option value="ON_SALE">판매중</option>
                                <option value="OUT_OF_PRINT">절판</option>
                                <option value="TEMPORARILY_OUT_OF_STOCK">일시품절</option>
                                <option value="EXPECTED_IN_STOCK">입고예정</option>
                            </select>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-save" onclick="confirmStatusChange('${isbn}')">상태 변경</button>
                        <button class="btn-cancel" onclick="closeStatusChangeModal()">취소</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        setupModalCloseEvents('statusChangeModal', closeStatusChangeModal);
    }

    // 상품 정보수정 모달 표시
    function showProductEditModal(isbn) {
        // 기존 모달 제거
        removeExistingModals();

        // 상품 정보 조회
        console.log('상품 상세 정보 조회 요청:', `/admin/api/products/${isbn}/detail`);
        fetch(`/admin/api/products/${isbn}/detail`)
            .then(response => {
                console.log('상품 상세 정보 응답:', response);
                console.log('상품 상세 정보 응답 상태:', response.status);
                console.log('상품 상세 정보 응답 상태 텍스트:', response.statusText);
                
                if (!response.ok) {
                    return response.text().then(text => {
                        console.log('오류 응답 내용:', text);
                        throw new Error(`HTTP error! status: ${response.status}, message: ${text}`);
                    });
                }
                return response.json();
            })
            .then(product => {
                console.log('상품 상세 정보:', product);
                console.log('상품의 lowCategory:', product.lowCategory);
                const modalHtml = `
                    <div id="productEditModal" class="modal-overlay">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h3>상품 정보 수정</h3>
                                <button class="modal-close" onclick="closeProductEditModal()">×</button>
                            </div>
                            <div class="modal-body">
                                <div class="form-group">
                                    <label for="editIsbn">ISBN <span class="required">*</span></label>
                                    <div class="isbn-input-container">
                                        <input type="text" id="editIsbn" value="${product.isbn}" maxlength="20" inputmode="numeric" pattern="[0-9]*" readonly>
                                    </div>
                                    <div class="validation-message" id="editIsbnValidation"></div>
                                </div>
                                
                                <div class="form-group">
                                    <label>카테고리 <span class="required">*</span></label>
                                    <div class="category-selects-horizontal">
                                        <select id="editTopCategory" required>
                                            <option value="">대분류 선택</option>
                                        </select>
                                        <select id="editMiddleCategory" required disabled>
                                            <option value="">중분류 선택</option>
                                        </select>
                                        <select id="editLowCategory" required disabled>
                                            <option value="">소분류 선택</option>
                                        </select>
                                    </div>
                                </div>
                                
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="editTitle">제목 <span class="required">*</span></label>
                                        <input type="text" id="editTitle" value="${product.productName}" maxlength="200">
                                    </div>
                                    <div class="form-group">
                                        <label for="editAuthor">저자명 <span class="required">*</span></label>
                                        <input type="text" id="editAuthor" value="${product.author}" maxlength="100">
                                    </div>
                                </div>
                                
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="editPublisher">출판사 <span class="required">*</span></label>
                                        <input type="text" id="editPublisher" value="${product.publisher}" maxlength="100">
                                    </div>
                                    <div class="form-group">
                                        <label for="editPrice">가격 <span class="required">*</span></label>
                                        <input type="number" id="editPrice" value="${product.price}" min="0" max="99999999">
                                    </div>
                                </div>
                                
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="editRate">평점 <span class="required">*</span></label>
                                        <input type="number" id="editRate" value="${product.rate}" min="0" max="10" step="0.1">
                                    </div>
                                    <div class="form-group">
                                        <label for="editImg">썸네일(URL) <span class="required">*</span></label>
                                        <input type="url" id="editImg" value="${product.img}" maxlength="1000">
                                    </div>
                                </div>
                                
                                <div class="form-group">
                                    <label for="editBriefDescription">약식설명</label>
                                    <textarea id="editBriefDescription" maxlength="2000" style="min-height: 100px;">${product.briefDescription || ''}</textarea>
                                </div>
                                
                                <div class="form-group">
                                    <label for="editDetailDescription">상세설명</label>
                                    <textarea id="editDetailDescription" maxlength="5000" style="min-height: 120px;">${product.detailDescription || ''}</textarea>
                                </div>
                                
                                <div class="form-row">
                                    <div class="form-group size-group">
                                        <label>사이즈정보 <span class="required">*</span></label>
                                        <div class="size-inputs">
                                            <input type="number" id="editWidth" value="${product.width}" placeholder="가로(mm)" min="0" max="9999">
                                            <input type="number" id="editHeight" value="${product.height}" placeholder="세로(mm)" min="0" max="9999">
                                            <input type="number" id="editPage" value="${product.page}" placeholder="페이지수" min="1" max="9999">
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <label for="editSalesStatus">판매상태 <span class="required">*</span></label>
                                        <select id="editSalesStatus">
                                            <option value="ON_SALE" ${product.salesStatus === 'ON_SALE' ? 'selected' : ''}>판매중</option>
                                            <option value="OUT_OF_PRINT" ${product.salesStatus === 'OUT_OF_PRINT' ? 'selected' : ''}>절판</option>
                                            <option value="TEMPORARILY_OUT_OF_STOCK" ${product.salesStatus === 'TEMPORARILY_OUT_OF_STOCK' ? 'selected' : ''}>일시품절</option>
                                            <option value="EXPECTED_IN_STOCK" ${product.salesStatus === 'EXPECTED_IN_STOCK' ? 'selected' : ''}>입고예정</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label for="editRegDate">출판일 <span class="required">*</span></label>
                                        <input type="date" id="editRegDate" value="${product.regDate ? product.regDate.split('T')[0] : ''}">
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button class="btn-save" onclick="confirmProductEdit('${isbn}')">수정</button>
                                <button class="btn-cancel" onclick="closeProductEditModal()">취소</button>
                            </div>
                        </div>
                    </div>
                `;

                document.body.insertAdjacentHTML('beforeend', modalHtml);
                setupModalCloseEvents('productEditModal', closeProductEditModal);
                
                // 모달 기능 초기화
                initializeEditModal(product);
            })
            .catch(error => {
                console.error('상품 정보 조회 실패:', error);
                console.error('Error details:', error.message);
                console.error('Error stack:', error.stack);
                alert('상품 정보를 불러오는데 실패했습니다. 콘솔을 확인해주세요.');
            });
    }

    // 편집 모달 기능 초기화
    function initializeEditModal(product) {
        // ISBN은 수정시 readonly이므로 중복확인 불필요
        window.editIsIsbnChecked = true; // 기존 ISBN은 이미 유효하다고 가정
        
        // 카테고리 기능 초기화
        initializeEditCategories(product.lowCategory);
    }

    // 편집 모달용 카테고리 초기화
    function initializeEditCategories(currentLowCategoryId) {
        console.log('카테고리 초기화 시작, 현재 소분류 ID:', currentLowCategoryId);
        
        const editTopCategory = document.getElementById('editTopCategory');
        const editMiddleCategory = document.getElementById('editMiddleCategory');
        const editLowCategory = document.getElementById('editLowCategory');
        
        // 대분류 불러오기
        fetch('/api/category/top')
            .then(res => res.json())
            .then(data => {
                console.log('대분류 데이터:', data);
                data.forEach(cat => {
                    const opt = document.createElement('option');
                    opt.value = cat.topCategory;
                    opt.textContent = cat.topCategoryName;
                    editTopCategory.appendChild(opt);
                });
                
                // 현재 상품의 카테고리 설정
                loadCurrentCategoryForEdit(currentLowCategoryId);
            })
            .catch(error => {
                console.error('대분류 로드 실패:', error);
            });
        
        // 대분류 변경 시 중분류 업데이트
        editTopCategory.addEventListener('change', function() {
            editMiddleCategory.innerHTML = '<option value="">중분류 선택</option>';
            editLowCategory.innerHTML = '<option value="">소분류 선택</option>';
            editMiddleCategory.disabled = true;
            editLowCategory.disabled = true;
            
            if (!this.value) return;
            
            fetch(`/api/category/middle?topCategory=${this.value}`)
                .then(res => res.json())
                .then(data => {
                    data.forEach(cat => {
                        const opt = document.createElement('option');
                        opt.value = cat.midCategory;
                        opt.textContent = cat.midCategoryName;
                        editMiddleCategory.appendChild(opt);
                    });
                    editMiddleCategory.disabled = false;
                });
        });
        
        // 중분류 변경 시 소분류 업데이트
        editMiddleCategory.addEventListener('change', function() {
            editLowCategory.innerHTML = '<option value="">소분류 선택</option>';
            editLowCategory.disabled = true;
            
            if (!this.value) return;
            
            fetch(`/api/category/low?midCategory=${this.value}`)
                .then(res => res.json())
                .then(data => {
                    data.forEach(cat => {
                        const opt = document.createElement('option');
                        opt.value = cat.lowCategory;
                        opt.textContent = cat.lowCategoryName;
                        editLowCategory.appendChild(opt);
                    });
                    editLowCategory.disabled = false;
                });
        });
    }

    // 현재 상품의 카테고리 경로 설정
    function loadCurrentCategoryForEdit(lowCategoryId) {
        console.log('현재 카테고리 경로 설정 시작, 소분류 ID:', lowCategoryId);
        
        fetch('/admin/api/categories')
            .then(response => response.json())
            .then(categoryResponse => {
                console.log('카테고리 응답:', categoryResponse);
                
                const editTopCategory = document.getElementById('editTopCategory');
                const editMiddleCategory = document.getElementById('editMiddleCategory');
                const editLowCategory = document.getElementById('editLowCategory');
                
                // CategoryTreeResponse 구조: topCategories, middleCategoriesMap, lowCategoriesMap
                const topCategories = categoryResponse.topCategories;
                const middleCategoriesMap = categoryResponse.middleCategoriesMap;
                const lowCategoriesMap = categoryResponse.lowCategoriesMap;
                
                // 현재 상품의 카테고리 경로 찾기
                let currentTop = null, currentMiddle = null, currentLow = null;
                
                // 소분류 ID로 카테고리 경로 찾기
                for (const [midCategoryId, lowCategories] of Object.entries(lowCategoriesMap)) {
                    const foundLow = lowCategories.find(low => low.lowCategory === lowCategoryId);
                    if (foundLow) {
                        currentLow = foundLow;
                        
                        // 중분류 찾기
                        for (const [topCategoryId, middleCategories] of Object.entries(middleCategoriesMap)) {
                            const foundMiddle = middleCategories.find(mid => mid.midCategory === parseInt(midCategoryId));
                            if (foundMiddle) {
                                currentMiddle = foundMiddle;
                                
                                // 대분류 찾기
                                currentTop = topCategories.find(top => top.topCategory === parseInt(topCategoryId));
                                break;
                            }
                        }
                        break;
                    }
                }
                
                console.log('찾은 카테고리:', { currentTop, currentMiddle, currentLow });
                
                if (currentTop && currentMiddle && currentLow) {
                    // 대분류 설정
                    editTopCategory.value = currentTop.topCategory;
                    console.log('대분류 설정:', currentTop.topCategory, currentTop.topCategoryName);
                    
                    // 중분류 로드 및 설정
                    fetch(`/api/category/middle?topCategory=${currentTop.topCategory}`)
                        .then(res => res.json())
                        .then(data => {
                            console.log('중분류 데이터:', data);
                            editMiddleCategory.innerHTML = '<option value="">중분류 선택</option>';
                            data.forEach(cat => {
                                const opt = document.createElement('option');
                                opt.value = cat.midCategory;
                                opt.textContent = cat.midCategoryName;
                                editMiddleCategory.appendChild(opt);
                            });
                            editMiddleCategory.disabled = false;
                            editMiddleCategory.value = currentMiddle.midCategory;
                            console.log('중분류 설정:', currentMiddle.midCategory, currentMiddle.midCategoryName);
                            
                            // 소분류 로드 및 설정
                            return fetch(`/api/category/low?midCategory=${currentMiddle.midCategory}`);
                        })
                        .then(res => res.json())
                        .then(data => {
                            console.log('소분류 데이터:', data);
                            editLowCategory.innerHTML = '<option value="">소분류 선택</option>';
                            data.forEach(cat => {
                                const opt = document.createElement('option');
                                opt.value = cat.lowCategory;
                                opt.textContent = cat.lowCategoryName;
                                editLowCategory.appendChild(opt);
                            });
                            editLowCategory.disabled = false;
                            editLowCategory.value = currentLow.lowCategory;
                            console.log('소분류 설정:', currentLow.lowCategory, currentLow.lowCategoryName);
                        });
                } else {
                    console.error('카테고리 경로를 찾을 수 없습니다. 소분류 ID:', lowCategoryId);
                }
            })
            .catch(error => {
                console.error('카테고리 정보 로드 실패:', error);
            });
    }


    // 기존 모달들 제거
    function removeExistingModals() {
        const modals = ['stockUpdateModal', 'statusChangeModal', 'productEditModal'];
        modals.forEach(modalId => {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.remove();
            }
        });
    }

    // 모달 외부 클릭 시 닫기 이벤트 설정
    function setupModalCloseEvents(modalId, closeFunction) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === this) {
                    closeFunction();
                }
            });
        }
    }

    // 입고 모달 닫기
    window.closeStockUpdateModal = function() {
        const modal = document.getElementById('stockUpdateModal');
        if (modal) {
            modal.remove();
        }
    };

    // 상태변경 모달 닫기
    window.closeStatusChangeModal = function() {
        const modal = document.getElementById('statusChangeModal');
        if (modal) {
            modal.remove();
        }
    };

    // 상품 정보수정 모달 닫기
    window.closeProductEditModal = function() {
        const modal = document.getElementById('productEditModal');
        if (modal) {
            modal.remove();
        }
    };

    // 입고 처리 확인
    window.confirmStockUpdate = function(isbn) {
        const quantity = document.getElementById('stockQuantity').value;
        if (!quantity || parseInt(quantity) <= 0) {
            alert('올바른 수량을 입력해주세요.');
            return;
        }
        
        // API 호출
        fetch(`/admin/api/products/${isbn}/stock-in?quantity=${quantity}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        })
        .then(response => response.text())
        .then(result => {
            alert(result);
            closeStockUpdateModal();
            // 검색 파라미터 초기화 후 목록 새로고침
            searchParams = {};
            clearSearchForm();
            loadProducts();
        })
        .catch(error => {
            console.error('입고 처리 실패:', error);
            alert('입고 처리 중 오류가 발생했습니다.');
        });
    };

    // 상태 변경 확인
    window.confirmStatusChange = function(isbn) {
        const status = document.getElementById('statusSelect').value;
        const statusText = getStatusText(status);
        
        // API 호출
        fetch(`/admin/api/products/${isbn}/status?status=${status}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        })
        .then(response => response.text())
        .then(result => {
            alert(result);
            closeStatusChangeModal();
            // 검색 파라미터 초기화 후 목록 새로고침
            searchParams = {};
            clearSearchForm();
            loadProducts();
        })
        .catch(error => {
            console.error('상태 변경 실패:', error);
            alert('상태 변경 중 오류가 발생했습니다.');
        });
    };

    // 상품 정보 수정 확인
    window.confirmProductEdit = function(originalIsbn) {
        // 필수 필드 수집 및 검증
        const newIsbn = document.getElementById('editIsbn').value.trim();
        const lowCategory = document.getElementById('editLowCategory').value;
        const title = document.getElementById('editTitle').value.trim();
        const author = document.getElementById('editAuthor').value.trim();
        const publisher = document.getElementById('editPublisher').value.trim();
        const price = document.getElementById('editPrice').value;
        const rate = document.getElementById('editRate').value;
        const img = document.getElementById('editImg').value.trim();
        const width = document.getElementById('editWidth').value;
        const height = document.getElementById('editHeight').value;
        const page = document.getElementById('editPage').value;
        const salesStatus = document.getElementById('editSalesStatus').value;
        const regDate = document.getElementById('editRegDate').value;
        
        if (!newIsbn || !lowCategory || !title || !author || !publisher || !price || !rate || !img || 
            !width || !height || !page || !salesStatus || !regDate) {
            alert('필수 항목을 모두 입력해주세요.');
            return;
        }
        
        if (parseInt(price) < 0 || parseFloat(rate) < 0 || parseFloat(rate) > 10) {
            alert('가격과 평점을 올바르게 입력해주세요.');
            return;
        }
        
        // 수정 데이터 수집
        const updateData = {
            newIsbn: newIsbn,
            lowCategory: parseInt(lowCategory),
            productName: title,
            author: author,
            publisher: publisher,
            price: parseInt(price),
            rate: parseFloat(rate),
            img: img,
            briefDescription: document.getElementById('editBriefDescription').value,
            detailDescription: document.getElementById('editDetailDescription').value,
            width: parseInt(width),
            height: parseInt(height),
            page: parseInt(page),
            salesStatus: salesStatus,
            regDate: regDate
        };
        
        console.log('상품 수정 데이터:', updateData);
        
        // API 호출
        fetch(`/admin/api/products/${originalIsbn}/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updateData)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success !== false) {
                alert('상품 정보가 수정되었습니다.');
                closeProductEditModal();
                // 검색 파라미터 초기화 후 목록 새로고침
                searchParams = {};
                clearSearchForm();
                loadProducts();
            } else {
                alert('수정 실패: ' + (result.message || '알 수 없는 오류가 발생했습니다.'));
            }
        })
        .catch(error => {
            console.error('상품 정보 수정 실패:', error);
            alert('상품 정보 수정에 실패했습니다.');
        });
    };
});