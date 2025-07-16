// 장바구니 페이지 JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const cartItemsList = document.getElementById('cartItemsList');
    const emptyCart = document.getElementById('emptyCart');
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    const subtotalPrice = document.getElementById('subtotalPrice');
    const shippingFee = document.getElementById('shippingFee');
    const totalPrice = document.getElementById('totalPrice');
    const orderSelectedBtn = document.getElementById('orderSelectedBtn');
    const orderAllBtn = document.getElementById('orderAllBtn');
    const deleteSelectedBtn = document.getElementById('deleteSelectedBtn');
    const deleteAllBtn = document.getElementById('deleteAllBtn');

    let cartData = [];
    let currentPage = 1;
    const itemsPerPage = 10;

    // 재고량 캐시 (ISBN별로 저장)
    let stockCache = new Map(); // ISBN -> {stock: number, lastUpdated: timestamp}

    // 재고량 캐시에서 가져오기
    function getCachedStock(isbn) {
        const cached = stockCache.get(isbn);
        if (cached && (Date.now() - cached.lastUpdated < 30000)) { // 30초 캐시
            return cached.stock;
        }
        return null;
    }

    // 재고량 캐시에 저장
    function setCachedStock(isbn, stock) {
        stockCache.set(isbn, {
            stock: stock,
            lastUpdated: Date.now()
        });
    }

    // 재고량 로드 (캐시 확인 후 필요시만 API 호출)
    function loadStock(isbn) {
        const cached = getCachedStock(isbn);
        if (cached !== null) {
            return Promise.resolve(cached);
        }

        return fetch(`/cart/api/stock/${isbn}`)
            .then(res => res.json())
            .then(data => {
                const stock = data.stock || 0;
                setCachedStock(isbn, stock);
                return stock;
            })
            .catch(error => {
                console.error('재고 조회 중 오류:', error);
                return 0;
            });
    }

    // 모든 장바구니 상품의 재고량 미리 로드
    function preloadAllStocks() {
        const isbns = cartData.map(item => item.isbn);
        const promises = isbns.map(isbn => loadStock(isbn));
        return Promise.all(promises);
    }

    // 1. 장바구니 목록 불러오기
    function fetchCartList() {
        fetch('/cart/list')
            .then(res => res.json())
            .then(data => {
                cartData = data;
                renderCartPage(currentPage);
                updateSummary();
                // 모든 상품의 재고량 미리 로드
                preloadAllStocks().then(() => {
                    console.log('모든 상품의 재고량 캐시 완료');
                });
            });
    }

    // 2. 장바구니 목록 렌더링 (페이징)
    function renderCartPage(page) {
        cartItemsList.innerHTML = '';
        const startIdx = (page - 1) * itemsPerPage;
        const endIdx = startIdx + itemsPerPage;
        const pageItems = cartData.slice(startIdx, endIdx);
        if (pageItems.length === 0) {
            emptyCart.style.display = 'block';
            return;
        } else {
            emptyCart.style.display = 'none';
        }
        pageItems.forEach(item => {
            const isOnSale = item.salesStatus === 'ON_SALE';
            const statusText = item.salesStatus === 'ON_SALE' ? '판매중' : (item.salesStatus === 'OUT_OF_PRINT' ? '절판' : (item.salesStatus === 'TEMPORARILY_OUT_OF_STOCK' ? '일시품절' : (item.salesStatus === 'EXPECTED_IN_STOCK' ? '입고예정' : (item.salesStatus || '정보없음'))));
            const statusColor = isOnSale ? '' : ' style="color:#e74c3c;font-weight:bold;"';
            const tr = document.createElement('tr');
            tr.className = 'cart-item-row';
            tr.innerHTML = `
                <td><input type="checkbox" class="item-checkbox" data-isbn="${item.isbn}" data-sales-status="${item.salesStatus}"></td>
                <td class="cart-info-cell">
                    <a href="/product/detail/${item.isbn}">
                      <img src="${item.img || '/default.png'}" alt="썸네일" class="cart-thumb">
                    </a>
                    <div class="cart-info-text">
                        <div class="cart-title"><a href="/product/detail/${item.isbn}">${item.productName || ''}</a></div>
                        <div class="cart-author">${item.author || ''}</div>
                    </div>
                </td>
                <td class="cart-status-cell"><span${statusColor}>${statusText}</span></td>
                <td>
                    <div class="cart-qty-col">
                        <div class="cart-qty-row">
                            <button class="qty-btn minus">-</button>
                            <input type="text" class="qty-input" value="${item.productQuantity}" data-isbn="${item.isbn}"/>
                            <button class="qty-btn plus">+</button>
                        </div>
                        <button class="qty-update-btn" data-isbn="${item.isbn}">수정</button>
                    </div>
                </td>
                <td class="cart-price">${formatPrice((item.price || 0) * item.productQuantity)}원</td>
            `;
            cartItemsList.appendChild(tr);
        });
        renderPaging();
        bindCartEvents();
    }

    // 상품목록과 동일한 페이지네이션 렌더링 함수
    function renderPaging() {
        let oldPaging = document.getElementById('cartPaging');
        if (oldPaging) oldPaging.remove();
        const totalItems = cartData.length;
        const totalPages = Math.ceil(totalItems / itemsPerPage);
        if (totalPages <= 1) return;
        const pagingDiv = document.createElement('div');
        pagingDiv.id = 'cartPaging';
        pagingDiv.className = 'pagination-container';
        const btnsDiv = document.createElement('div');
        btnsDiv.className = 'pagination-btns';
        // 그룹화 계산 (1~10, 11~20)
        const currentGroup = Math.ceil(currentPage / 10);
        const startPage = (currentGroup - 1) * 10 + 1;
        const endPage = Math.min(currentGroup * 10, totalPages);
        // 처음/이전 그룹
        if (currentGroup > 1) {
            const firstBtn = document.createElement('button');
            firstBtn.className = 'pagination-btn first-btn';
            firstBtn.textContent = '처음';
            firstBtn.onclick = () => { currentPage = 1; renderCartPage(currentPage); updateSummary(); };
            btnsDiv.appendChild(firstBtn);
            const prevBtn = document.createElement('button');
            prevBtn.className = 'pagination-btn prev-group-btn';
            prevBtn.textContent = '이전';
            prevBtn.onclick = () => { currentPage = startPage - 1; renderCartPage(currentPage); updateSummary(); };
            btnsDiv.appendChild(prevBtn);
        }
        // 페이지 번호
        for (let i = startPage; i <= endPage; i++) {
            const btn = document.createElement('button');
            btn.className = 'pagination-btn' + (i === currentPage ? ' current' : '');
            btn.textContent = i;
            btn.onclick = () => { currentPage = i; renderCartPage(currentPage); updateSummary(); };
            btnsDiv.appendChild(btn);
        }
        // 다음/끝 그룹
        if (endPage < totalPages) {
            const nextBtn = document.createElement('button');
            nextBtn.className = 'pagination-btn next-group-btn';
            nextBtn.textContent = '다음';
            nextBtn.onclick = () => { currentPage = endPage + 1; renderCartPage(currentPage); updateSummary(); };
            btnsDiv.appendChild(nextBtn);
            const lastBtn = document.createElement('button');
            lastBtn.className = 'pagination-btn last-btn';
            lastBtn.textContent = '끝';
            lastBtn.onclick = () => { currentPage = totalPages; renderCartPage(currentPage); updateSummary(); };
            btnsDiv.appendChild(lastBtn);
        }
        pagingDiv.appendChild(btnsDiv);
        // 테이블 섹션 하단에 붙이기
        const tableSection = document.querySelector('.cart-table-section');
        tableSection.appendChild(pagingDiv);
    }

    // 4. 이벤트 바인딩
    function bindCartEvents() {
        // 전체선택
        selectAllCheckbox.onclick = function() {
            document.querySelectorAll('.item-checkbox').forEach(cb => cb.checked = selectAllCheckbox.checked);
            updateSummary();
        };
        // 개별선택
        document.querySelectorAll('.item-checkbox').forEach(cb => {
            cb.onclick = function() {
                const all = document.querySelectorAll('.item-checkbox');
                const checked = document.querySelectorAll('.item-checkbox:checked');
                selectAllCheckbox.checked = all.length === checked.length;
                updateSummary();
            };
        });
        // 수량 +/-, 직접입력
        document.querySelectorAll('.qty-btn.minus').forEach(btn => {
            btn.onclick = function() {
                const input = this.parentNode.querySelector('.qty-input');
                let v = parseInt(input.value) || 1;
                if (v > 1) input.value = v - 1;
            };
        });
        document.querySelectorAll('.qty-btn.plus').forEach(btn => {
            btn.onclick = function() {
                const input = this.parentNode.querySelector('.qty-input');
                const isbn = input.dataset.isbn;
                let currentQty = parseInt(input.value) || 1;
                let newQty = currentQty + 1;

                // 캐시된 재고량으로 즉시 검증
                const cachedStock = getCachedStock(isbn);
                if (cachedStock !== null) {
                    if (newQty > cachedStock) {
                        alert(`재고가 부족합니다. 현재 재고: ${cachedStock}개`);
                        return;
                    }
                    input.value = newQty;
                } else {
                    // 캐시에 없으면 API 호출 (fallback)
                    loadStock(isbn).then(stock => {
                        if (newQty > stock) {
                            alert(`재고가 부족합니다. 현재 재고: ${stock}개`);
                            return;
                        }
                        input.value = newQty;
                    });
                }
            };
        });
        // 수량 직접입력 제한
        document.querySelectorAll('.qty-input').forEach(input => {
            input.oninput = function() {
                const isbn = this.dataset.isbn;
                let v = parseInt(this.value) || 1;
                if (v < 1) v = 1;

                // 캐시된 재고량으로 즉시 검증
                const cachedStock = getCachedStock(isbn);
                if (cachedStock !== null) {
                    if (v > cachedStock) {
                        alert(`재고가 부족합니다. 현재 재고: ${cachedStock}개`);
                        v = cachedStock;
                    }
                    this.value = v;
                } else {
                    // 캐시에 없으면 API 호출 (fallback)
                    loadStock(isbn).then(stock => {
                        if (v > stock) {
                            alert(`재고가 부족합니다. 현재 재고: ${stock}개`);
                            v = stock;
                        }
                        this.value = v;
                    });
                }
            };
        });
        // 수량 수정
        document.querySelectorAll('.qty-update-btn').forEach(btn => {
            btn.onclick = function() {
                const isbn = this.dataset.isbn;
                const input = document.querySelector(`.qty-input[data-isbn="${isbn}"]`);
                const qty = parseInt(input.value) || 1;

                // 캐시된 재고량으로 체크
                const cachedStock = getCachedStock(isbn);
                const checkStockAndUpdate = (stock) => {
                    if (qty > stock) {
                        alert('재고가 부족합니다. 최대 수량: ' + stock);
                        input.value = stock;
                        return;
                    }
                    // 재고 초과가 아니면 수정 요청
                    fetch('/cart/update', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: `isbn=${encodeURIComponent(isbn)}&quantity=${encodeURIComponent(qty)}`
                    })
                        .then(res => res.text())
                        .then(data => {
                            if (data === 'OK') {
                                alert('수정되었습니다.');
                                fetchCartList();
                            } else {
                                alert(data);
                            }
                        });
                };

                if (cachedStock !== null) {
                    checkStockAndUpdate(cachedStock);
                } else {
                    // 캐시에 없으면 API 호출
                    loadStock(isbn).then(checkStockAndUpdate);
                }
            };
        });
        // 삭제
        document.querySelectorAll('.cart-delete-btn').forEach(btn => {
            btn.onclick = function() {
                const isbn = this.dataset.isbn;
                if (!confirm('이 상품을 장바구니에서 삭제하시겠습니까?')) return;
                fetch('/cart/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `isbn=${encodeURIComponent(isbn)}`
                })
                    .then(res => res.text())
                    .then(data => {
                        if (data === 'OK') {
                            fetchCartList();
                        } else {
                            alert(data);
                        }
                    });
            };
        });
        // 선택삭제
        deleteSelectedBtn.onclick = function() {
            const selected = Array.from(document.querySelectorAll('.item-checkbox:checked')).map(cb => cb.dataset.isbn);
            if (selected.length === 0) return alert('삭제할 상품을 선택하세요.');
            if (!confirm('선택한 상품을 삭제하시겠습니까?')) return;
            Promise.all(selected.map(isbn => fetch('/cart/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `isbn=${encodeURIComponent(isbn)}`
            }).then(res => res.text()))).then(() => {
                alert('선택 상품이 삭제되었습니다.');
                location.reload();
            });
        };
        // 전체삭제
        deleteAllBtn.onclick = function() {
            if (!confirm('장바구니의 모든 상품을 삭제하시겠습니까?')) return;
            Promise.all(cartData.map(item => fetch('/cart/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `isbn=${encodeURIComponent(item.isbn)}`
            }).then(res => res.text()))).then(() => {
                alert('전체 상품이 삭제되었습니다.');
                location.reload();
            });
        };
        // 주문 버튼(선택/전체)
        orderSelectedBtn.onclick = function() {
            const selected = Array.from(document.querySelectorAll('.item-checkbox:checked'));
            if (selected.length === 0) return alert('주문할 상품을 선택하세요.');
            // 판매중이 아닌 상품 선택 시 구매불가
            const invalid = selected.find(cb => cb.dataset.salesStatus !== 'ON_SALE');
            if (invalid) {
                return alert('판매중이 아닌 상품이 포함되어 있습니다. 구매가 불가합니다.');
            }
            const isbns = selected.map(cb => cb.dataset.isbn);
            const quantities = isbns.map(isbn => {
                const item = cartData.find(i => i.isbn === isbn);
                return item ? item.productQuantity : 1;
            });
            postOrder(isbns, quantities);
        };
        orderAllBtn.onclick = function() {
            // 전체 상품 중 판매중 상품만 주문
            const onSaleItems = cartData.filter(i => i.salesStatus === 'ON_SALE');
            if (onSaleItems.length === 0) return alert('주문할 수 있는 상품이 없습니다.');
            const isbns = onSaleItems.map(i => i.isbn);
            const quantities = onSaleItems.map(i => i.productQuantity);
            postOrder(isbns, quantities);
        };
        // 주문 폼 POST 함수
        function postOrder(isbns, quantities) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/order';
            isbns.forEach((isbn, i) => {
                const isbnInput = document.createElement('input');
                isbnInput.type = 'hidden';
                isbnInput.name = 'isbns';
                isbnInput.value = isbn;
                form.appendChild(isbnInput);
                const qtyInput = document.createElement('input');
                qtyInput.type = 'hidden';
                qtyInput.name = 'quantities';
                qtyInput.value = quantities[i];
                form.appendChild(qtyInput);
            });
            document.body.appendChild(form);
            form.submit();
        }
    }

    // 5. 서머리(스티키) 실시간 갱신
    function updateSummary() {
        const selected = Array.from(document.querySelectorAll('.item-checkbox:checked'));
        let sum = 0;
        selected.forEach(cb => {
            const item = cartData.find(i => i.isbn === cb.dataset.isbn);
            if (item) sum += (item.price || 0) * item.productQuantity;
        });
        subtotalPrice.textContent = formatPrice(sum) + '원';
        let shipping = 0;
        let shippingText = '0원';
        if (selected.length > 0) {
            if (sum >= 20000) {
                shipping = 0;
                shippingText = '무료';
            } else {
                shipping = 3000;
                shippingText = formatPrice(shipping) + '원';
            }
        }
        shippingFee.textContent = shippingText;
        totalPrice.textContent = formatPrice(sum + shipping) + '원';
    }

    // 6. 가격 포맷
    function formatPrice(price) {
        return price.toLocaleString();
    }

    // 7. 스티키 서머리 (CSS에서 .price-summary에 position:sticky 적용 필요)

    // 8. 최초 로딩
    fetchCartList();


});
