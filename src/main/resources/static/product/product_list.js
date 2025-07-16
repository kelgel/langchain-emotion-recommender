// 상품목록 페이지 JavaScript

// 페이지네이션 개선 함수
function improvePagination() {
    const paginationContainer = document.querySelector('.pagination-container');
    if (!paginationContainer) return;
    
    const paginationBtns = paginationContainer.querySelector('.pagination-btns');
    if (!paginationBtns) return;
    
    const allBtns = Array.from(paginationBtns.querySelectorAll('.pagination-btn'));
    if (allBtns.length <= 10) return; // 10개 이하면 그룹화 불필요
    
    // 현재 페이지 찾기
    const currentBtn = allBtns.find(btn => btn.classList.contains('current'));
    if (!currentBtn) return;
    
    const currentPage = parseInt(currentBtn.getAttribute('data-page'));
    const totalPages = allBtns.length;
    
    // 현재 그룹 계산 (1~10, 11~20, ...)
    const currentGroup = Math.ceil(currentPage / 10);
    const startPage = (currentGroup - 1) * 10 + 1;
    const endPage = Math.min(currentGroup * 10, totalPages);
    
    // 새로운 HTML 구성
    let newHTML = '';
    
    // 처음 버튼 (2그룹 이상일 때)
    if (currentGroup > 1) {
        newHTML += `<button type="button" class="pagination-btn first-btn" data-page="1">처음</button>`;
    }
    
    // 이전 그룹 버튼 (2그룹 이상일 때)
    if (currentGroup > 1) {
        const prevGroupLastPage = startPage - 1;
        newHTML += `<button type="button" class="pagination-btn prev-group-btn" data-page="${prevGroupLastPage}">이전</button>`;
    }
    
    // 현재 그룹의 페이지 번호들
    for (let i = startPage; i <= endPage; i++) {
        const isActive = i === currentPage ? ' current' : '';
        newHTML += `<button type="button" class="pagination-btn${isActive}" data-page="${i}">${i}</button>`;
    }
    
    // 다음 그룹 버튼 (마지막 그룹이 아닐 때)
    if (endPage < totalPages) {
        const nextGroupFirstPage = endPage + 1;
        newHTML += `<button type="button" class="pagination-btn next-group-btn" data-page="${nextGroupFirstPage}">다음</button>`;
    }
    
    // 끝 버튼 (마지막 그룹이 아닐 때)
    if (endPage < totalPages) {
        newHTML += `<button type="button" class="pagination-btn last-btn" data-page="${totalPages}">끝</button>`;
    }
    
    // HTML 교체
    paginationBtns.innerHTML = newHTML;
}

document.addEventListener('DOMContentLoaded', function() {
    // 체크박스 전체선택/해제
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    const rowCheckboxes = document.querySelectorAll('.row-checkbox');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            rowCheckboxes.forEach(cb => cb.checked = selectAllCheckbox.checked);
        });
    }
    rowCheckboxes.forEach(cb => {
        cb.addEventListener('change', function() {
            if (!this.checked) selectAllCheckbox.checked = false;
            else if ([...rowCheckboxes].every(c => c.checked)) selectAllCheckbox.checked = true;
        });
    });

    // 선택상품 장바구니 버튼
    const addToCartBtn = document.getElementById('addToCartBtn');
    if (addToCartBtn) {
        // 1. 페이지네이션 그룹화 처리
        improvePagination();
        
        // 2. 페이지네이션 버튼 클릭 시 이동
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('pagination-btn')) {
                const page = e.target.getAttribute('data-page');
                if (page) {
                    const currentUrl = new URL(window.location);
                    currentUrl.searchParams.set('page', page);
                    window.location.href = currentUrl.toString();
                }
            }
        });

        // 로그인 체크 함수 (상세/목록 공통)
        function isLoggedIn() {
            return window.isUserLoggedIn === true;
        }
        
        // 관리자일 경우 장바구니 관련 버튼들 비활성화
        function disableCartButtonsForAdmin() {
            if (window.isAdmin) {
                // 선택상품 장바구니 버튼
                if (addToCartBtn) {
                    addToCartBtn.style.opacity = '0.5';
                    addToCartBtn.style.cursor = 'not-allowed';
                    addToCartBtn.style.backgroundColor = '#ccc';
                }
                
                // 개별 장바구니 버튼들
                document.querySelectorAll('.cart-btn').forEach(btn => {
                    btn.style.opacity = '0.5';
                    btn.style.cursor = 'not-allowed';
                    btn.style.backgroundColor = '#ccc';
                });
                
                // 개별 구매 버튼들
                document.querySelectorAll('.buy-btn').forEach(btn => {
                    btn.style.opacity = '0.5';
                    btn.style.cursor = 'not-allowed';
                    btn.style.backgroundColor = '#ccc';
                });
            }
        }
        
        // 관리자 버튼 비활성화 적용
        disableCartButtonsForAdmin();

        // 2. 선택상품 장바구니 버튼 동작
        addToCartBtn.addEventListener('click', async function() {
            // 관리자 접근 차단
            if (window.isAdmin) {
                alert('일반 사용자 전용 기능입니다.');
                return;
            }
            
            if (!isLoggedIn()) {
                alert('로그인이 필요한 기능입니다. 로그인 후 이용해 주세요.');
                window.location.href = '/login?redirectUrl=' + encodeURIComponent(window.location.pathname + window.location.search);
                return;
            }
            const selected = [...rowCheckboxes].filter(cb => cb.checked).map(cb => cb.value);
            if (selected.length === 0) {
                alert('선택된 상품이 없습니다.');
                return;
            }
            // 이미 담긴 상품 조회 (서버에 확인)
            const res = await fetch('/cart/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ isbns: selected })
            });
            const data = await res.json();
            const alreadyInCart = data.alreadyInCart || [];
            const toAdd = selected.filter(isbn => !alreadyInCart.includes(isbn));
            if (toAdd.length === 0) {
                alert('이미 담겨있는 상품입니다.');
                return;
            }
            // 실제 장바구니 담기
            const addRes = await fetch('/cart/add-bulk', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ isbns: toAdd })
            });
            if (alreadyInCart.length > 0) {
                alert('이미 담겨 있는 상품을 제외하고 장바구니에 담았습니다.');
            } else {
                alert('장바구니에 담았습니다.');
            }
        });
    }

    // 상세검색 submit 시 page=1로 이동
    const detailSearchForm = document.getElementById('detailSearchForm');
    if (detailSearchForm) {
        detailSearchForm.addEventListener('submit', function(e) {
            // page 파라미터를 1로 강제
            let pageInput = detailSearchForm.querySelector('input[name="page"]');
            if (!pageInput) {
                pageInput = document.createElement('input');
                pageInput.type = 'hidden';
                pageInput.name = 'page';
                detailSearchForm.appendChild(pageInput);
            }
            pageInput.value = 1;
        });
    }

    // 필터 셀렉트 동작 (기존과 동일)
    const sortSelect = document.getElementById('sortSelect');
    const pageSizeSelect = document.getElementById('pageSizeSelect');
    function updateProductList(page = null) {
        const currentUrl = new URL(window.location);
        const currentPage = page || currentUrl.searchParams.get('page') || 1;
        const currentSize = pageSizeSelect ? pageSizeSelect.value : 30;
        const currentSort = sortSelect ? sortSelect.value : 'latest';
        currentUrl.searchParams.set('page', currentPage);
        currentUrl.searchParams.set('size', currentSize);
        currentUrl.searchParams.set('sort', currentSort);
        window.location.href = currentUrl.toString();
    }
    if (sortSelect) sortSelect.addEventListener('change', () => updateProductList());
    if (pageSizeSelect) pageSizeSelect.addEventListener('change', () => updateProductList(1));

    // 상품 이미지 에러 처리
    const productImages = document.querySelectorAll('.book-image');
    productImages.forEach(function(img) {
        img.addEventListener('error', function() {
            this.src = '/layout/책크인_이미지.png';
            this.alt = '이미지를 불러올 수 없습니다';
        });
    });

    // 상품 행 클릭 이벤트 (이미지/상품명)
    const productRows = document.querySelectorAll('.product-row');
    productRows.forEach(function(row) {
        const productLink = row.querySelector('.product-name a');
        const productImage = row.querySelector('.book-image');
        if (productLink) {
            productLink.addEventListener('click', function(e) { e.stopPropagation(); });
        }
        if (productImage) {
            productImage.addEventListener('click', function(e) {
                e.preventDefault();
                if (productLink) window.location.href = productLink.href;
            });
            productImage.style.cursor = 'pointer';
        }
    });

    // 페이지네이션 로딩 효과
    const paginationLinks = document.querySelectorAll('.pagination a');
    paginationLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const container = document.querySelector('.product-list-layout');
            if (container) {
                container.style.opacity = '0.7';
                container.style.pointerEvents = 'none';
            }
        });
    });

    // 반응형 테이블 스크롤
    const tableContainer = document.querySelector('.product-table-container');
    if (tableContainer && window.innerWidth <= 768) {
        tableContainer.style.overflowX = 'auto';
        tableContainer.style.webkitOverflowScrolling = 'touch';
    }
    window.addEventListener('resize', function() {
        if (tableContainer) {
            if (window.innerWidth <= 768) tableContainer.style.overflowX = 'auto';
            else tableContainer.style.overflowX = 'visible';
        }
    });

    // 상품 없을 때 메시지
    const productTable = document.querySelector('.product-table tbody');
    if (productTable && productTable.children.length === 0) {
        const noProductMessage = document.createElement('tr');
        noProductMessage.innerHTML = `
            <td colspan="5" style="text-align: center; padding: 40px; color: #666;">
                <p>해당 카테고리에 상품이 없습니다.</p>
            </td>
        `;
        productTable.appendChild(noProductMessage);
    }

    // 로딩 상태 관리
    window.addEventListener('beforeunload', function() {
        const container = document.querySelector('.product-list-layout');
        if (container) container.style.opacity = '0.7';
    });
    window.addEventListener('load', function() {
        const container = document.querySelector('.product-list-layout');
        if (container) {
            container.style.opacity = '1';
            container.style.pointerEvents = 'auto';
        }
    });

    // 3. 개별 장바구니 버튼 동작
    document.querySelectorAll('.cart-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            // 관리자 접근 차단
            if (window.isAdmin) {
                alert('일반 사용자 전용 기능입니다.');
                return;
            }
            
            if (!isLoggedIn()) {
                alert('로그인이 필요한 기능입니다. 로그인 후 이용해 주세요.');
                window.location.href = '/login?redirectUrl=' + encodeURIComponent(window.location.pathname + window.location.search);
                return;
            }
            const isbn = this.getAttribute('data-isbn');
            // 이미 담긴 상품인지 서버에 확인
            const res = await fetch('/cart/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ isbns: [isbn] })
            });
            const data = await res.json();
            if (data.alreadyInCart && data.alreadyInCart.includes(isbn)) {
                alert('이미 담겨있는 상품입니다.');
                return;
            }
            // 실제 장바구니 담기
            await fetch('/cart/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `isbn=${encodeURIComponent(isbn)}&quantity=1`
            });
            alert('장바구니에 담았습니다.');
        });
    });

    // 4. 개별 바로구매 버튼 동작
    document.querySelectorAll('.buy-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // 관리자 접근 차단
            if (window.isAdmin) {
                alert('일반 사용자 전용 기능입니다.');
                return;
            }
            
            if (!isLoggedIn()) {
                alert('로그인이 필요한 기능입니다. 로그인 후 이용해 주세요.');
                window.location.href = '/login?redirectUrl=' + encodeURIComponent(window.location.pathname + window.location.search);
                return;
            }
            const isbn = this.getAttribute('data-isbn');
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/order';
            form.style.display = 'none';
            const isbnInput = document.createElement('input');
            isbnInput.type = 'hidden';
            isbnInput.name = 'isbns';
            isbnInput.value = isbn;
            form.appendChild(isbnInput);
            const qtyInput = document.createElement('input');
            qtyInput.type = 'hidden';
            qtyInput.name = 'quantities';
            qtyInput.value = 1;
            form.appendChild(qtyInput);
            document.body.appendChild(form);
            form.submit();
        });
    });
});
