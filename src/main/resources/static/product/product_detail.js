// 상품상세 페이지 JavaScript

// URL에서 상품 ID 추출 (전역 함수로 이동)
function getProductIdFromUrl() {
    // 1. 쿼리스트링에 isbn이 있으면 우선 사용
    const params = new URLSearchParams(window.location.search);
    if (params.has('isbn')) {
        return params.get('isbn');
    }
    // 2. /product/detail/9791140714575 형태면 마지막 segment
    const pathSegments = window.location.pathname.split('/');
    return pathSegments[pathSegments.length - 1];
}

// 리뷰 페이지네이션 개선 함수
function improveReviewPagination() {
    const paginationContainer = document.querySelector('.review-section .pagination-container');
    if (!paginationContainer) return;
    
    const paginationBtns = paginationContainer.querySelector('.pagination-btns');
    if (!paginationBtns) return;
    
    const allBtns = Array.from(paginationBtns.querySelectorAll('.pagination-btn'));
    if (allBtns.length <= 10) return; // 10개 이하면 그룹화 불필요
    
    // 현재 페이지 찾기 (0-based)
    const currentBtn = allBtns.find(btn => btn.classList.contains('current'));
    if (!currentBtn) return;
    
    const currentPageZeroBased = parseInt(currentBtn.getAttribute('data-page'));
    const currentPage = currentPageZeroBased + 1; // 1-based로 변환
    const totalPages = allBtns.length;
    
    // 현재 그룹 계산 (1~10, 11~20, ...)
    const currentGroup = Math.ceil(currentPage / 10);
    const startPage = (currentGroup - 1) * 10 + 1;
    const endPage = Math.min(currentGroup * 10, totalPages);
    
    // 새로운 HTML 구성
    let newHTML = '';
    
    // 처음 버튼 (2그룹 이상일 때)
    if (currentGroup > 1) {
        newHTML += `<button type="button" class="pagination-btn first-btn" onclick="navigateToReviewPageDirect(0)">처음</button>`;
    }
    
    // 이전 그룹 버튼 (2그룹 이상일 때)
    if (currentGroup > 1) {
        const prevGroupLastPage = startPage - 2; // 0-based로 변환
        newHTML += `<button type="button" class="pagination-btn prev-group-btn" onclick="navigateToReviewPageDirect(${prevGroupLastPage})">이전</button>`;
    }
    
    // 현재 그룹의 페이지 번호들
    for (let i = startPage; i <= endPage; i++) {
        const zeroBased = i - 1; // 0-based로 변환
        const isActive = i === currentPage ? ' current' : '';
        newHTML += `<button type="button" class="pagination-btn${isActive}" data-page="${zeroBased}" onclick="navigateToReviewPageDirect(${zeroBased})">${i}</button>`;
    }
    
    // 다음 그룹 버튼 (마지막 그룹이 아닐 때)
    if (endPage < totalPages) {
        const nextGroupFirstPage = endPage; // 0-based로 변환
        newHTML += `<button type="button" class="pagination-btn next-group-btn" onclick="navigateToReviewPageDirect(${nextGroupFirstPage})">다음</button>`;
    }
    
    // 끝 버튼 (마지막 그룹이 아닐 때)
    if (endPage < totalPages) {
        const lastPageZeroBased = totalPages - 1; // 0-based로 변환
        newHTML += `<button type="button" class="pagination-btn last-btn" onclick="navigateToReviewPageDirect(${lastPageZeroBased})">끝</button>`;
    }
    
    // HTML 교체
    paginationBtns.innerHTML = newHTML;
}

// 리뷰 페이지 이동 함수
function navigateToReviewPageDirect(page) {
    const currentScrollY = window.scrollY;
    sessionStorage.setItem('reviewScrollPosition', currentScrollY.toString());
    const currentUrl = new URL(window.location);
    currentUrl.searchParams.set('page', page);
    window.location.href = currentUrl.toString();
}

document.addEventListener('DOMContentLoaded', function() {
    const productId = getProductIdFromUrl();
    
    // 리뷰 페이지네이션 개선
    improveReviewPagination();
    
    // 로그인 체크 함수
    function isLoggedIn() {
        // 서버에서 로그인 여부를 window.isUserLoggedIn 등으로 내려주거나, 세션 쿠키/로컬스토리지 등으로 체크
        // 여기서는 window.isUserLoggedIn 전역변수 사용 가정(템플릿에서 <script>window.isUserLoggedIn = ...</script>로 세팅)
        return window.isUserLoggedIn === true;
    }

    // 모달 생성 함수
    function showCartModal(type) {
        // type: 'OK' | 'ALREADY'
        // 기존 모달 제거
        const oldModal = document.getElementById('cartModal');
        if (oldModal) oldModal.remove();
        // 모달 HTML
        const modal = document.createElement('div');
        modal.id = 'cartModal';
        modal.style.position = 'fixed';
        modal.style.top = '50%';
        modal.style.left = '50%';
        modal.style.transform = 'translate(-50%, -50%)';
        modal.style.zIndex = '9999';
        modal.style.background = '#fff';
        modal.style.border = '1.5px solid #ddd';
        modal.style.borderRadius = '12px';
        modal.style.boxShadow = '0 4px 24px rgba(0,0,0,0.13)';
        modal.style.width = '340px';
        modal.style.padding = '32px 24px 24px 24px';
        modal.style.display = 'flex';
        modal.style.flexDirection = 'column';
        modal.style.alignItems = 'center';
        modal.style.animation = 'fadeIn 0.2s';
        modal.innerHTML = `
            <button id="cartModalClose" style="position:absolute;top:12px;right:16px;background:none;border:none;font-size:1.3em;cursor:pointer;">&times;</button>
            <div style="margin-bottom:18px;font-size:1.13em;font-weight:bold;text-align:center;">
                ${type === 'OK' ? '장바구니에 상품이 담겼습니다.' : '<span style="font-weight:bold;"><span style="color:#e74c3c;font-weight:bold;">이미</span> 장바구니에 담겨있는 상품입니다.</span>'}
            </div>
            <div style="margin-bottom:24px;font-size:1em;text-align:center;">지금 확인 하시겠습니까?</div>
            <div style="display:flex;gap:16px;justify-content:center;width:100%;">
                <button id="cartModalConfirm" style="flex:1;padding:10px 0;background:#222;color:#fff;border:none;border-radius:6px;font-weight:bold;cursor:pointer;">확인</button>
                <button id="cartModalCancel" style="flex:1;padding:10px 0;background:#eee;color:#333;border:none;border-radius:6px;font-weight:bold;cursor:pointer;">취소</button>
            </div>
        `;
        document.body.appendChild(modal);
        // 이벤트
        document.getElementById('cartModalClose').onclick = () => modal.remove();
        document.getElementById('cartModalCancel').onclick = () => modal.remove();
        document.getElementById('cartModalConfirm').onclick = () => { window.location.href = '/cart'; };
    }

    // 장바구니 담기 기능
    window.addToCart = function() {
        // 관리자 접근 차단
        if (window.isAdmin) {
            alert('일반 사용자 전용 기능입니다.');
            return;
        }
        
        if (!isLoggedIn()) {
            alert('로그인이 필요합니다. 로그인 후 이용해 주세요.');
            window.location.href = '/login?redirectUrl=' + encodeURIComponent(window.location.pathname + window.location.search);
            return;
        }
        // 상품 상태 확인
        const expectedInStockBadge = document.querySelector('.status-badge.expected');
        if (expectedInStockBadge) {
            alert('입고 예정 상품은 장바구니에 담을 수 없습니다.');
            return;
        }
        // 수량 읽기
        const qtyInput = document.getElementById('qtyInput');
        const quantity = qtyInput ? parseInt(qtyInput.value, 10) || 1 : 1;
        fetch('/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `isbn=${encodeURIComponent(productId)}&quantity=${encodeURIComponent(quantity)}`
        })
        .then(response => response.text())
        .then(data => {
            if (data === 'OK') {
                showCartModal('OK');
            } else if (data === 'ALREADY') {
                showCartModal('ALREADY');
            } else {
                alert(data);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('장바구니 담기에 실패했습니다.');
        });
    };

    // 구매하기 기능
    window.buyNow = function() {
        // 관리자 접근 차단
        if (window.isAdmin) {
            alert('일반 사용자 전용 기능입니다.');
            return;
        }
        
        if (!isLoggedIn()) {
            alert('로그인이 필요합니다. 로그인 후 이용해 주세요.');
            window.location.href = '/login?redirectUrl=' + encodeURIComponent(window.location.pathname + window.location.search);
            return;
        }
        // 상품 상태 확인
        const expectedInStockBadge = document.querySelector('.status-badge.expected');
        if (expectedInStockBadge) {
            alert('입고 예정 상품은 구매할 수 없습니다.');
            return;
        }
        // 수량 읽기
        const qtyInput = document.getElementById('qtyInput');
        const quantity = qtyInput ? parseInt(qtyInput.value, 10) || 1 : 1;
        fetch('/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `isbn=${encodeURIComponent(productId)}&quantity=${encodeURIComponent(quantity)}`
        })
        .then(response => response.text())
        .then(data => {
            if (data === 'OK' || data === 'ALREADY') {
                // POST 방식으로 주문페이지 이동 (url에 정보 노출X)
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/order';
                const isbnInput = document.createElement('input');
                isbnInput.type = 'hidden';
                isbnInput.name = 'isbns';
                isbnInput.value = productId;
                form.appendChild(isbnInput);
                const qtyInput = document.createElement('input');
                qtyInput.type = 'hidden';
                qtyInput.name = 'quantities';
                qtyInput.value = quantity;
                form.appendChild(qtyInput);
                document.body.appendChild(form);
                form.submit();
            } else {
                alert(data);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('구매 처리에 실패했습니다.');
        });
    };


    // CSRF 토큰 가져오기
    function getCsrfToken() {
        const token = document.querySelector('meta[name="_csrf"]');
        return token ? token.getAttribute('content') : '';
    }

    // 리뷰 평점 표시
    const ratingStars = document.querySelectorAll('.rating-stars .star');
    ratingStars.forEach((star, index) => {
        star.addEventListener('click', function() {
            // 리뷰 작성 시 평점 선택 기능 (필요시 구현)
            console.log('Selected rating:', index + 1);
        });
    });

    // 상품 이미지 클릭 시 확대 보기 (선택사항)
    const productImage = document.querySelector('.product-image img');
    if (productImage) {
        productImage.addEventListener('click', function() {
            // 이미지 확대 보기 모달 구현 (필요시)
            console.log('Image clicked');
        });
    }

    // 수량조절 및 금액 업데이트
    const qtyInput = document.getElementById('qtyInput');
    const minusBtn = document.getElementById('qtyMinus');
    const plusBtn = document.getElementById('qtyPlus');
    const priceSpan = document.getElementById('totalPrice');

    // --- 캐시된 재고량으로 즉시 검증 ---
    let cachedStock = 0; // 캐시된 재고량
    let stockLastUpdated = 0; // 마지막 업데이트 시간

    // 페이지 로드 시 재고량 한 번만 가져오기
    function loadInitialStock() {
        fetch(`/product/api/stock/${productId}`)
            .then(res => res.json())
            .then(data => {
                cachedStock = data.stock || 0;
                stockLastUpdated = Date.now();
                console.log(`재고량 캐시됨: ${cachedStock}개`);
            })
            .catch(error => {
                console.error('초기 재고 조회 중 오류:', error);
                cachedStock = 0;
            });
    }

    // 재고량 새로고침 (필요시에만 호출)
    function refreshStock() {
        return fetch(`/product/api/stock/${productId}`)
            .then(res => res.json())
            .then(data => {
                cachedStock = data.stock || 0;
                stockLastUpdated = Date.now();
                return cachedStock;
            });
    }

    if (qtyInput && minusBtn && plusBtn && priceSpan) {
        const unitPrice = parseInt(priceSpan.getAttribute('data-unit-price'), 10);
        
        function updatePrice() {
            const qty = Math.max(1, parseInt(qtyInput.value, 10) || 1);
            priceSpan.textContent = (unitPrice * qty).toLocaleString() + '원';
        }
        
        minusBtn.addEventListener('click', function() {
            let qty = Math.max(1, parseInt(qtyInput.value, 10) - 1);
            qtyInput.value = qty;
            updatePrice();
        });
        
        plusBtn.addEventListener('click', function() {
            let currentQty = Math.max(1, parseInt(qtyInput.value, 10));
            let newQty = currentQty + 1;
            
            // 캐시된 재고량으로 즉시 검증
            if (newQty > cachedStock) {
                alert(`재고가 부족합니다. 현재 재고: ${cachedStock}개`);
                return;
            }
            
            qtyInput.value = newQty;
            updatePrice();
        });
        
        qtyInput.addEventListener('input', function() {
            let qty = Math.max(1, parseInt(qtyInput.value, 10) || 1);
            
            // 캐시된 재고량으로 즉시 검증
            if (qty > cachedStock) {
                alert(`재고가 부족합니다. 현재 재고: ${cachedStock}개`);
                qty = cachedStock;
                qtyInput.value = qty;
            }
            updatePrice();
        });
        
        // 초기 재고량 로드
        loadInitialStock();
        updatePrice();
    }

    // 관리자일 경우 장바구니 관련 버튼 비활성화
    function disableCartButtonsForAdmin() {
        if (window.isAdmin) {
            const cartBtn = document.querySelector('.cart-btn');
            const buyBtn = document.querySelector('.buy-btn');
            
            if (cartBtn) {
                cartBtn.style.opacity = '0.5';
                cartBtn.style.cursor = 'not-allowed';
                cartBtn.style.backgroundColor = '#ccc';
            }
            
            if (buyBtn) {
                buyBtn.style.opacity = '0.5';
                buyBtn.style.cursor = 'not-allowed';
                buyBtn.style.backgroundColor = '#ccc';
            }
        }
    }
    
    // 관리자 버튼 비활성화 적용
    disableCartButtonsForAdmin();

    // 최근조회(aside) - 로그인한 유저만 동작, 상품상세 진입 시 썸네일만 추가
    function addRecentBookIfLoggedIn() {
        if (!isLoggedIn()) return;
        const userId = window.userId || 'guest';
        // 상품 정보 추출
        const isbn = productId;
        const title = document.querySelector('h1')?.textContent || '';
        const image = document.querySelector('.product-thumbnail img')?.src || '';
        // 최근조회 목록 userId별로 저장
        let recentBooks = JSON.parse(localStorage.getItem('recentBooks_' + userId) || '[]');
        // 이미 있으면 중복 제거
        recentBooks = recentBooks.filter(book => book.isbn !== isbn);
        // 맨 앞에 추가
        recentBooks.unshift({ isbn, title, image });
        // 최대 10개 제한
        if (recentBooks.length > 10) recentBooks = recentBooks.slice(0, 10);
        localStorage.setItem('recentBooks_' + userId, JSON.stringify(recentBooks));
        // aside에 바로 반영(함수 있으면 호출)
        if (typeof window.updateRecentBooksDisplay === 'function') {
            window.updateRecentBooksDisplay();
        } else {
            window.addEventListener('DOMContentLoaded', function() {
                if (typeof window.updateRecentBooksDisplay === 'function') {
                    window.updateRecentBooksDisplay();
                }
            });
        }
    }
    addRecentBookIfLoggedIn();
});

// 리뷰 페이지네이션 함수 (스크롤 위치 유지)
function navigateToReviewPage(btn) {
    const pageNum = btn.getAttribute('data-page');
    const isbn = getProductIdFromUrl();
    const currentScrollY = window.scrollY;
    
    // 스크롤 위치를 세션스토리지에 저장
    sessionStorage.setItem('reviewScrollPosition', currentScrollY.toString());
    
    // 페이지 이동
    window.location.href = `/product/detail/${isbn}?page=${pageNum}`;
}

// 페이지 로드 시 스크롤 위치 복원
document.addEventListener('DOMContentLoaded', function() {
    const savedScrollY = sessionStorage.getItem('reviewScrollPosition');
    if (savedScrollY) {
        window.scrollTo(0, parseInt(savedScrollY));
        sessionStorage.removeItem('reviewScrollPosition');
    }
});

function toggleReview(btn) {
  const row = btn.closest('tr');
  const next = row.nextElementSibling;
  if (next && next.classList.contains('review-content-row')) {
    next.style.display = next.style.display === 'table-row' ? 'none' : 'table-row';
    btn.textContent = btn.textContent === '▼' ? '▲' : '▼';
  }
}
