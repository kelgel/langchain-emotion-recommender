// 관리자 회원조회 페이지 JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // 전역 변수
    let currentPage = 1;
    let currentSize = 30;
    let currentSort = 'idAdminAsc';
    let searchParams = {};

    // 모달 관련 변수
    let modalCurrentPage = 1;
    let modalCurrentSize = 30;
    let modalCurrentSort = 'latest';
    let modalUserId = '';
    let modalSearchParams = {};

    // DOM 요소들
    const detailSearchForm = document.getElementById('detailSearchForm');
    const sortSelect = document.getElementById('sortSelect');
    const pageSizeSelect = document.getElementById('pageSizeSelect');
    const userList = document.getElementById('userList');
    const paginationBtns = document.getElementById('paginationBtns');

    // 모달 DOM 요소들
    const userOrderModal = document.getElementById('userOrderModal');
    const modalSortSelect = document.getElementById('modalSortSelect');
    const modalPageSizeSelect = document.getElementById('modalPageSizeSelect');
    const modalOrderList = document.getElementById('modalOrderList');
    const modalPaginationBtns = document.getElementById('modalPaginationBtns');

    // 초기화
    init();

    function init() {
        loadUsers();
        setupEventListeners();
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
                loadUsers();
            });
        }

        // 페이지 크기 변경
        if (pageSizeSelect) {
            pageSizeSelect.addEventListener('change', function() {
                currentSize = parseInt(this.value);
                currentPage = 1;
                loadUsers();
            });
        }

        // 모달 이벤트 리스너
        if (modalSortSelect) {
            modalSortSelect.addEventListener('change', function() {
                modalCurrentSort = this.value;
                modalCurrentPage = 1;
                loadUserOrders();
            });
        }

        if (modalPageSizeSelect) {
            modalPageSizeSelect.addEventListener('change', function() {
                modalCurrentSize = parseInt(this.value);
                modalCurrentPage = 1;
                loadUserOrders();
            });
        }

        // 모달 내 상세검색 폼 이벤트
        const modalDetailSearchForm = document.getElementById('modalDetailSearchForm');
        if (modalDetailSearchForm) {
            modalDetailSearchForm.addEventListener('submit', function(e) {
                e.preventDefault();
                handleModalSearch();
            });
        }

        // 모달 내 주문번호 입력 필드 (숫자만 입력 허용)
        const modalOrderIdInput = document.getElementById('modalOrderId');
        if (modalOrderIdInput) {
            modalOrderIdInput.addEventListener('input', function() {
                this.value = this.value.replace(/[^0-9]/g, '');
            });
        }
    }

    // 검색 처리
    function handleSearch() {
        const formData = new FormData(detailSearchForm);
        searchParams = {};

        // 회원ID (IFA 또는 IFU)
        const userId = formData.get('userId')?.trim();
        if (userId) {
            searchParams.userId = userId;
        }

        // 회원명
        const userName = formData.get('userName')?.trim();
        if (userName) {
            searchParams.userName = userName;
        }

        // 회원등급
        const userGrade = formData.get('userGrade');
        if (userGrade) searchParams.userGrade = userGrade;

        // 가입일 범위
        const startDate = formData.get('startDate');
        const endDate = formData.get('endDate');
        if (startDate) searchParams.startDate = startDate;
        if (endDate) searchParams.endDate = endDate;

        // 회원상태
        const userStatus = formData.get('userStatus');
        if (userStatus) searchParams.userStatus = userStatus;

        currentPage = 1;
        loadUsers();
    }

    // 검색 폼 초기화
    function resetSearchForm() {
        if (detailSearchForm) {
            detailSearchForm.reset();
        }
        searchParams = {};
        currentPage = 1;
        loadUsers();
    }

    // 회원 목록 로드
    function loadUsers() {
        const params = new URLSearchParams({
            sort: currentSort,
            page: currentPage,
            size: currentSize,
            ...searchParams
        });

        fetch(`/admin/api/users?${params}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                displayUsers(data.users || []);
                updatePagination(data.totalPages || 0, data.currentPage || 1);
            })
            .catch(error => {
                console.error('회원 목록 로드 실패:', error);
                displayError('회원 목록을 불러오는데 실패했습니다.');
            });
    }

    // 회원 목록 표시
    function displayUsers(users) {
        if (!users || users.length === 0) {
            userList.innerHTML = '<div class="no-users">조회된 회원이 없습니다.</div>';
            return;
        }

        const userCards = users.map(user => createUserCard(user)).join('');
        userList.innerHTML = userCards;

        // 주문내역 버튼 이벤트 등록
        document.querySelectorAll('.btn-order-history').forEach(btn => {
            btn.addEventListener('click', function() {
                const userId = this.dataset.userId;
                const userName = this.dataset.userName;
                openUserOrderModal(userId, userName);
            });
        });
    }

    // 회원 카드 생성
    function createUserCard(user) {
        const gradeClass = getGradeClass(user.userGrade);
        const statusClass = getStatusClass(user.userStatus);
        const gradeText = getGradeText(user.userGrade);
        const statusText = getStatusText(user.userStatus);

        return `
            <div class="user-card">
                <div class="user-header">
                    <div class="user-main-info">
                        <div class="user-name-grade">
                            <span class="user-name">${user.userName}</span>
                            <span class="user-nickname">(${user.nickname || 'N/A'})</span>
                            <span class="${gradeClass}">${gradeText}</span>
                        </div>
                        <div class="user-ids">
                            회원ID IFA: ${user.idForAdmin} / IFU: ${user.idForUser}
                        </div>
                    </div>
                    <div class="user-actions">
                        <button class="btn-order-history" 
                                data-user-id="${user.idForAdmin}" 
                                data-user-name="${user.userName}">
                            주문내역
                        </button>
                        <div class="user-status-info">
                            상태: <span class="${statusClass}">${statusText}</span><br>
                            최근 로그인: ${user.lastLogin ? formatDate(user.lastLogin) : 'N/A'}
                        </div>
                    </div>
                </div>
                <div class="user-details">
                    <div class="user-detail-item">
                        <span class="user-detail-label">생년월일:</span> ${user.birthDate || 'N/A'} (${user.gender || 'N/A'})
                    </div>
                    <div class="user-detail-item">
                        <span class="user-detail-label">이메일:</span> ${user.email}
                    </div>
                    <div class="user-detail-item">
                        <span class="user-detail-label">전화번호:</span> ${user.phoneNumber || 'N/A'}
                    </div>
                    <div class="user-detail-item">
                        <span class="user-detail-label">주소:</span> ${user.address || 'N/A'}
                    </div>
                    <div class="user-detail-item">
                        <span class="user-detail-label">회원가입일:</span> ${formatDate(user.regDate)}
                    </div>
                    <div class="user-detail-item">
                        <span class="user-detail-label">정보수정일:</span> ${user.updateDate ? formatDate(user.updateDate) : 'N/A'}
                    </div>
                </div>
            </div>
        `;
    }

    // 회원등급 클래스 반환
    function getGradeClass(grade) {
        const gradeMap = {
            'BZ': 'grade-bz',
            'SV': 'grade-sv',
            'GD': 'grade-gd',
            'PL': 'grade-pl'
        };
        return gradeMap[grade] || '';
    }

    // 회원등급 한글 텍스트 반환
    function getGradeText(grade) {
        const gradeMap = {
            'BZ': 'BRONZE',
            'SV': 'SILVER',
            'GD': 'GOLD',
            'PL': 'PLATINUM'
        };
        return gradeMap[grade] || grade;
    }

    // 회원상태 클래스 반환
    function getStatusClass(status) {
        const statusMap = {
            'ACTIVE': 'status-active',
            'INACTIVE': 'status-inactive',
            'DORMANT': 'status-dormant',
            'WITHDRAWN': 'status-withdrawn'
        };
        return statusMap[status] || '';
    }

    // 회원상태 한글 텍스트 반환
    function getStatusText(status) {
        const statusMap = {
            'ACTIVE': '활성',
            'DORMANT': '휴면',
            'WITHDRAWN': '탈퇴'
        };
        return statusMap[status] || status;
    }

    // 회원 주문내역 모달 열기
    function openUserOrderModal(userId, userName) {
        modalUserId = userId;
        modalCurrentPage = 1;
        modalSearchParams = {};

        document.getElementById('userOrderModalTitle').textContent = `${userName} 님의 주문내역`;

        // 모달 내 상세검색 폼의 주문자ID 필드에 해당 회원 ID 자동 설정
        const modalUserIdInput = document.getElementById('modalUserId');
        if (modalUserIdInput) {
            modalUserIdInput.value = userId;
        }

        userOrderModal.style.display = 'flex';

        // 스크롤 최상단으로 이동
        const modalBody = userOrderModal.querySelector('.modal-body');
        if (modalBody) {
            modalBody.scrollTop = 0;
        }
        const embeddedOrderContainer = userOrderModal.querySelector('.embedded-order-container');
        if (embeddedOrderContainer) {
            embeddedOrderContainer.scrollTop = 0;
        }

        // 모달이 표시된 후 자동으로 검색 실행
        setTimeout(() => {
            handleModalSearch();
        }, 100);
    }

    // 회원 주문내역 모달 닫기
    window.closeUserOrderModal = function() {
        userOrderModal.style.display = 'none';
        modalUserId = '';
        modalCurrentPage = 1;
        modalSearchParams = {};
        
        // 모달 내 검색 폼 초기화
        const modalDetailSearchForm = document.getElementById('modalDetailSearchForm');
        if (modalDetailSearchForm) {
            modalDetailSearchForm.reset();
        }
    };

    // 모달 내 검색 처리
    function handleModalSearch() {
        const formData = new FormData(document.getElementById('modalDetailSearchForm'));
        modalSearchParams = {};

        // 주문번호 처리 (OD 접두사 추가)
        const orderId = formData.get('orderId')?.trim();
        if (orderId) {
            modalSearchParams.orderId = 'OD' + orderId;
        }

        // 주문자ID (이미 설정되어 있음)
        modalSearchParams.userId = modalUserId;

        // 주문금액 범위
        const minAmount = formData.get('minAmount');
        const maxAmount = formData.get('maxAmount');
        if (minAmount) modalSearchParams.minAmount = minAmount;
        if (maxAmount) modalSearchParams.maxAmount = maxAmount;

        // 주문일 범위
        const startDate = formData.get('startDate');
        const endDate = formData.get('endDate');
        if (startDate) modalSearchParams.startDate = startDate;
        if (endDate) modalSearchParams.endDate = endDate;

        // 주문상태
        const orderStatus = formData.get('orderStatus');
        if (orderStatus) modalSearchParams.orderStatus = orderStatus;

        modalCurrentPage = 1;
        loadUserOrders();
    }

    // 회원 주문내역 로드
    function loadUserOrders() {
        if (!modalUserId) return;

        const params = new URLSearchParams({
            sort: modalCurrentSort,
            page: modalCurrentPage,
            size: modalCurrentSize,
            ...modalSearchParams
        });

        fetch(`/admin/api/orders?${params}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                displayModalOrders(data.orders || []);
                updateModalPagination(data.totalPages || 0, data.currentPage || 1);
            })
            .catch(error => {
                console.error('회원 주문내역 로드 실패:', error);
                modalOrderList.innerHTML = '<div class="error-message">주문내역을 불러오는데 실패했습니다.</div>';
            });
    }

    // 모달 주문 목록 표시
    function displayModalOrders(orders) {
        if (!orders || orders.length === 0) {
            modalOrderList.innerHTML = '<div class="no-orders">해당 회원의 주문내역이 없습니다.</div>';
            return;
        }

        const orderCards = orders.map(order => createOrderCard(order)).join('');
        modalOrderList.innerHTML = orderCards;

        // 상태변경 버튼 이벤트 등록 (비활성화된 버튼 제외)
        modalOrderList.querySelectorAll('.btn-status-change:not(.disabled)').forEach(btn => {
            btn.addEventListener('click', function() {
                const orderId = this.dataset.orderId;
                const currentStatus = this.dataset.currentStatus;
                const idForAdmin = this.dataset.idForAdmin;
                openStatusChangeModal(orderId, currentStatus, idForAdmin);
            });
        });
    }

    // 주문 카드 생성 (주문조회에서 복사)
    function createOrderCard(order) {
        const statusClass = getOrderStatusClass(order.orderStatus);
        const statusText = getOrderStatusText(order.orderStatus);
        
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
    function getOrderStatusClass(status) {
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
    function getOrderStatusText(status) {
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

    // 상태변경 모달 열기 (주문조회에서 복사)
    function openStatusChangeModal(orderId, currentStatus, idForAdmin) {
        const statusOptions = [
            'PREPARING_PRODUCT', 'SHIPPING', 'DELIVERED', 'CANCEL_COMPLETED'
        ].map(status => {
            const selected = status === currentStatus ? 'selected' : '';
            return `<option value="${status}" ${selected}>${getOrderStatusText(status)}</option>`;
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
                        <p><strong>현재상태:</strong> ${getOrderStatusText(currentStatus)}</p>
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
            loadUserOrders(); // 모달 내 주문목록 새로고침
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

    // 모달 페이지네이션 업데이트
    function updateModalPagination(totalPages, current) {
        if (totalPages <= 1) {
            modalPaginationBtns.innerHTML = '';
            return;
        }
        let paginationHtml = '';
        const currentGroup = Math.ceil(current / 10);
        const startPage = (currentGroup - 1) * 10 + 1;
        const endPage = Math.min(currentGroup * 10, totalPages);
        // 처음/이전 그룹
        if (currentGroup > 1) {
            paginationHtml += `<button class="pagination-btn first-btn" onclick="changeModalPage(1)">처음</button>`;
            paginationHtml += `<button class="pagination-btn prev-group-btn" onclick="changeModalPage(${startPage - 1})">이전</button>`;
        }
        // 페이지 번호
        for (let i = startPage; i <= endPage; i++) {
            const activeClass = i === current ? 'current' : '';
            paginationHtml += `<button class="pagination-btn ${activeClass}" onclick="changeModalPage(${i})">${i}</button>`;
        }
        // 다음/끝 그룹
        if (endPage < totalPages) {
            paginationHtml += `<button class="pagination-btn next-group-btn" onclick="changeModalPage(${endPage + 1})">다음</button>`;
            paginationHtml += `<button class="pagination-btn last-btn" onclick="changeModalPage(${totalPages})">끝</button>`;
        }
        modalPaginationBtns.innerHTML = paginationHtml;
    }

    // 페이지 변경
    window.changePage = function(page) {
        if (page < 1) return;
        currentPage = page;
        loadUsers();
    };

    // 모달 페이지 변경
    window.changeModalPage = function(page) {
        if (page < 1) return;
        modalCurrentPage = page;
        loadUserOrders();
    };

    // 에러 표시
    function displayError(message) {
        userList.innerHTML = `<div class="error-message">${message}</div>`;
    }

    // 가격 포맷
    function formatPrice(price) {
        return new Intl.NumberFormat('ko-KR').format(price);
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

    // 모달 외부 클릭 시 닫기
    userOrderModal.addEventListener('click', function(e) {
        if (e.target === userOrderModal) {
            closeUserOrderModal();
        }
    });
});