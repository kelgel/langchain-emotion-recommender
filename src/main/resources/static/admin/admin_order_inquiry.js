// 관리자 주문조회 페이지 JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // 전역 변수
    let currentPage = 1;
    let currentSize = 30;
    let currentSort = 'latest';
    let searchParams = {};

    // DOM 요소들
    const detailSearchForm = document.getElementById('detailSearchForm');
    const sortSelect = document.getElementById('sortSelect');
    const pageSizeSelect = document.getElementById('pageSizeSelect');
    const orderList = document.getElementById('orderList');
    const paginationBtns = document.getElementById('paginationBtns');

    // 주문번호 입력 필드 (숫자만 입력 허용)
    const orderIdInput = document.getElementById('orderId');
    if (orderIdInput) {
        orderIdInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    }

    // 초기화
    init();

    function init() {
        // 먼저 간단한 테스트 API 호출
        testOrderData();
        loadOrders();
        setupEventListeners();
    }
    
    // Order 데이터 테스트
    function testOrderData() {
        console.log('Order 데이터 테스트 시작...');
        
        fetch('/admin/api/orders/test')
            .then(response => {
                console.log('테스트 API 응답 상태:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Order 테이블 데이터:', data);
                
                if (data.totalCount === 0) {
                    console.warn('Order 테이블에 데이터가 없습니다.');
                    orderList.innerHTML = '<div class="no-orders">주문 데이터가 없습니다. 먼저 주문을 생성해주세요.</div>';
                }
            })
            .catch(error => {
                console.error('Order 테스트 실패:', error);
            });
    }

    function setupEventListeners() {
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
                loadOrders();
            });
        }

        // 페이지 크기 변경
        if (pageSizeSelect) {
            pageSizeSelect.addEventListener('change', function() {
                currentSize = parseInt(this.value);
                currentPage = 1;
                loadOrders();
            });
        }
    }

    // 검색 처리
    function handleSearch() {
        const formData = new FormData(detailSearchForm);
        searchParams = {};

        // 주문번호 처리 (OD 접두사 추가)
        const orderId = formData.get('orderId')?.trim();
        if (orderId) {
            searchParams.orderId = 'OD' + orderId;
        }

        // 주문자ID
        const userId = formData.get('userId')?.trim();
        if (userId) {
            searchParams.userId = userId;
        }

        // 주문금액 범위
        const minAmount = formData.get('minAmount');
        const maxAmount = formData.get('maxAmount');
        if (minAmount) searchParams.minAmount = minAmount;
        if (maxAmount) searchParams.maxAmount = maxAmount;

        // 주문일 범위
        const startDate = formData.get('startDate');
        const endDate = formData.get('endDate');
        if (startDate) searchParams.startDate = startDate;
        if (endDate) searchParams.endDate = endDate;

        // 주문상태
        const orderStatus = formData.get('orderStatus');
        if (orderStatus) searchParams.orderStatus = orderStatus;

        currentPage = 1;
        loadOrders();
    }

    // 검색 폼 초기화
    function resetSearchForm() {
        if (detailSearchForm) {
            detailSearchForm.reset();
        }
        searchParams = {};
        currentPage = 1;
        loadOrders();
    }

    // 주문 목록 로드
    function loadOrders() {
        const params = new URLSearchParams({
            sort: currentSort,
            page: currentPage,
            size: currentSize,
            ...searchParams
        });

        fetch(`/admin/api/orders?${params}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                displayOrders(data.orders || []);
                updatePagination(data.totalPages || 0, data.currentPage || 1);
            })
            .catch(error => {
                console.error('주문 목록 로드 실패:', error);
                displayError('주문 목록을 불러오는데 실패했습니다.');
            });
    }

    // 주문 목록 표시
    function displayOrders(orders) {
        if (!orders || orders.length === 0) {
            orderList.innerHTML = '<div class="no-orders">조회된 주문이 없습니다.</div>';
            return;
        }

        const orderCards = orders.map(order => createOrderCard(order)).join('');
        orderList.innerHTML = orderCards;

        // 상태변경 버튼 이벤트 등록 (비활성화된 버튼 제외)
        document.querySelectorAll('.btn-status-change:not(.disabled)').forEach(btn => {
            btn.addEventListener('click', function() {
                const orderId = this.dataset.orderId;
                const currentStatus = this.dataset.currentStatus;
                const idForAdmin = this.dataset.idForAdmin;
                openStatusChangeModal(orderId, currentStatus, idForAdmin);
            });
        });
    }

    // 주문 카드 생성
    function createOrderCard(order) {
        const statusClass = getStatusClass(order.orderStatus);
        const statusText = getStatusText(order.orderStatus);
        
        const orderItems = order.orderDetails?.map(item => `
            <div class="order-item">
                <img src="${item.img || '/images/default-book.png'}" alt="${item.productTitle}" class="item-image">
                <div class="item-info">
                    <div class="item-title">${item.productTitle}</div>
                    <div class="item-author">${item.author}</div>
                </div>
                <div class="item-quantity">${item.orderItemQuantity}개</div>
                <div class="item-price">${formatPrice(item.totalProductPrice)}원</div>
            </div>
        `).join('') || '';

        // 상품들의 총 금액 계산
        const productTotalPrice = order.orderDetails?.reduce((sum, item) => sum + item.totalProductPrice, 0) || 0;

        // 취소된 주문, 실패한 주문, 주문요청 상태는 상태변경 불가
        const isDisabled = order.orderStatus === 'CANCEL_COMPLETED' || 
                          order.orderStatus === 'ORDER_FAILED' || 
                          order.orderStatus === 'ORDER_REQUESTED';
        const statusChangeButton = isDisabled ? 
            `<button class="btn-status-change disabled" disabled>상태변경</button>` :
            `<button class="btn-status-change" 
                     data-order-id="${order.orderId}" 
                     data-current-status="${order.orderStatus}"
                     data-id-for-admin="${order.userIdForAdmin}">
                상태변경
             </button>`;

        return `
            <div class="order-card">
                <div class="order-header">
                    <div class="order-header-top">
                        <div class="order-number">주문번호: ${order.orderId}</div>
                        <div class="order-actions">
                            ${statusChangeButton}
                        </div>
                    </div>
                    <div class="order-info">
                        <div class="order-date">주문일시: ${formatDate(order.orderDate)}</div>
                        <div class="user-info">주문자ID IFA: ${order.userIdForAdmin} / IFU: ${order.userIdForUser}</div>
                        <div class="order-status">주문상태: <span class="${statusClass}">${statusText}</span></div>
                        <div class="order-summary">
                            총 ${order.totalProductCategory}개의 상품 / 결제금액: ${getDisplayPriceFromProducts(productTotalPrice)}
                        </div>
                    </div>
                </div>
                <div class="order-items">
                    ${orderItems}
                </div>
            </div>
        `;
    }

    // 주문상태 클래스 반환
    function getStatusClass(status) {
        const statusMap = {
            'ORDER_COMPLETED': 'completed',
            'DELIVERED': 'delivered',
            'SHIPPING': 'shipping', 
            'PREPARING_PRODUCT': 'preparing',
            'ORDER_FAILED': 'failed',
            'CANCEL_COMPLETED': 'cancelled'
        };
        return statusMap[status] || '';
    }

    // 주문상태 한글 텍스트 반환
    function getStatusText(status) {
        const statusMap = {
            'ORDER_REQUESTED': '주문요청',
            'ORDER_FAILED': '주문실패',
            'ORDER_COMPLETED': '주문완료',
            'PREPARING_PRODUCT': '상품준비중',
            'SHIPPING': '배송중',
            'DELIVERED': '배송완료',
            'CANCEL_COMPLETED': '취소완료'
        };
        return statusMap[status] || status;
    }

    // 상태변경 모달 열기
    function openStatusChangeModal(orderId, currentStatus, idForAdmin) {
        const statusOptions = [
            'PREPARING_PRODUCT', 'SHIPPING', 'DELIVERED', 'CANCEL_COMPLETED'
        ].map(status => {
            const selected = status === currentStatus ? 'selected' : '';
            return `<option value="${status}" ${selected}>${getStatusText(status)}</option>`;
        }).join('');

        const modalHtml = `
            <div id="statusChangeModal" class="modal-overlay">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>주문상태 변경</h3>
                        <button class="modal-close" onclick="closeStatusChangeModal()">×</button>
                    </div>
                    <div class="modal-body">
                        <p><strong>주문번호:</strong> ${orderId}</p>
                        <p><strong>현재상태:</strong> ${getStatusText(currentStatus)}</p>
                        <br>
                        <label for="newStatus">새로운 상태:</label>
                        <select id="newStatus" style="width: 100%; padding: 8px; margin-top: 5px;">
                            ${statusOptions}
                        </select>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-save" onclick="confirmStatusChange('${orderId}', '${idForAdmin}')">변경</button>
                        <button class="btn-cancel" onclick="closeStatusChangeModal()">취소</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    // 상태변경 모달 닫기
    window.closeStatusChangeModal = function() {
        const modal = document.getElementById('statusChangeModal');
        if (modal) {
            modal.remove();
        }
    };

    // 상태변경 확인
    window.confirmStatusChange = function(orderId, idForAdmin) {
        const newStatus = document.getElementById('newStatus').value;
        
        fetch(`/admin/api/orders/${orderId}/status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `status=${newStatus}&idForAdmin=${idForAdmin}`
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(message => {
            alert('주문상태가 변경되었습니다.');
            closeStatusChangeModal();
            loadOrders(); // 목록 새로고침
        })
        .catch(error => {
            console.error('상태변경 실패:', error);
            alert('상태변경 중 오류가 발생했습니다.');
        });
    };

    // 페이지네이션 업데이트
    function updatePagination(totalPages, current) {
        if (totalPages <= 1) {
            paginationBtns.innerHTML = '';
            return;
        }
        let paginationHtml = '';
        const currentGroup = Math.ceil(current / 10);
        const startPage = (currentGroup - 1) * 10 + 1;
        const endPage = Math.min(currentGroup * 10, totalPages);
        // 처음/이전 그룹
        if (currentGroup > 1) {
            paginationHtml += `<button class="pagination-btn first-btn" onclick="changePage(1)">처음</button>`;
            paginationHtml += `<button class="pagination-btn prev-group-btn" onclick="changePage(${startPage - 1})">이전</button>`;
        }
        // 페이지 번호
        for (let i = startPage; i <= endPage; i++) {
            const activeClass = i === current ? 'current' : '';
            paginationHtml += `<button class="pagination-btn ${activeClass}" onclick="changePage(${i})">${i}</button>`;
        }
        // 다음/끝 그룹
        if (endPage < totalPages) {
            paginationHtml += `<button class="pagination-btn next-group-btn" onclick="changePage(${endPage + 1})">다음</button>`;
            paginationHtml += `<button class="pagination-btn last-btn" onclick="changePage(${totalPages})">끝</button>`;
        }
        paginationBtns.innerHTML = paginationHtml;
    }

    // 페이지 변경
    window.changePage = function(page) {
        if (page < 1) return;
        currentPage = page;
        loadOrders();
    };

    // 에러 표시
    function displayError(message) {
        orderList.innerHTML = `<div class="error-message">${message}</div>`;
    }

    // 가격 포맷
    function formatPrice(price) {
        return new Intl.NumberFormat('ko-KR').format(price);
    }
    
    // 상품 총액을 기준으로 배송비 포함 가격 계산
    function getDisplayPriceFromProducts(productTotalPrice) {
        const FREE_SHIPPING_THRESHOLD = 20000; // 2만원
        const SHIPPING_FEE = 3000; // 배송비 3천원
        
        if (productTotalPrice >= FREE_SHIPPING_THRESHOLD) {
            // 상품 총액이 2만원 이상이면 무료배송
            return `<span class="price-red">${formatPrice(productTotalPrice)}원</span>`;
        } else {
            // 상품 총액이 2만원 미만이면 배송비 추가
            const finalPrice = productTotalPrice + SHIPPING_FEE;
            return `<span class="price-red">${formatPrice(finalPrice)}원</span> <span class="shipping-info">(배송비 3,000원 포함)</span>`;
        }
    }

    // 날짜 포맷
    function formatDate(dateString) {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day} ${hours}:${minutes}`;
    }
});