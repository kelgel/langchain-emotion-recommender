document.addEventListener('DOMContentLoaded', function () {
    // 주문자 정보
    const orderMember = document.getElementById('order_member');
    const orderAddress = document.getElementById('address');
    const orderDetailAddress = document.getElementById('detail_address');
    const orderPhone = document.getElementById('phone_number');
    const orderEmail = document.getElementById('email');

    // 배송지 정보
    const receiver = document.getElementById('receiver');
    const receiverAddress = document.getElementById('receiver_address');
    const receiverDetailAddress = document.getElementById('receiver_detail_address');
    const receiverPhone = document.getElementById('receiver_phone_number');
    const addressSameRadio = document.getElementById('same_as_member_info');
    const addressCustomRadio = document.getElementById('custom_address');

    // 결제 관련
    const paymentKakaoRadio = document.getElementById('payment_by_kakao');
    const paymentAccountRadio = document.getElementById('payment_by_account');
    const orderSubmitBtn = document.getElementById('orderSubmitBtn');
    const orderAgree = document.getElementById('order_agree');

    // 팝업 참조 변수 추가
    let currentPaymentPopup = null;

    // 배송지 정보 복사 함수
    function copyOrdererToReceiver() {
        receiver.value = orderMember.value;
        receiverAddress.value = orderAddress.value;
        receiverDetailAddress.value = orderDetailAddress.value;
        receiverPhone.value = orderPhone.value;
        receiverAddress.readOnly = true;
    }

    // 배송지 정보 초기화 함수
    function clearReceiverFields() {
        receiver.value = '';
        receiverAddress.value = '';
        receiverDetailAddress.value = '';
        receiverPhone.value = '';
        receiverAddress.readOnly = false;
    }

    // 라디오 버튼 이벤트
    addressSameRadio.addEventListener('change', function () {
        if (this.checked) {
            copyOrdererToReceiver();
        }
    });
    addressCustomRadio.addEventListener('change', function () {
        if (this.checked) {
            clearReceiverFields();
        }
    });

    // 페이지 로드시 기본값 복사
    if (addressSameRadio.checked) {
        copyOrdererToReceiver();
    }

    // 주문자 정보 변경 시 배송지 자동 갱신
    [orderMember, orderAddress, orderDetailAddress, orderPhone].forEach(function (input) {
        input.addEventListener('input', function () {
            if (addressSameRadio.checked) {
                copyOrdererToReceiver();
            }
        });
    });

    // --- 주문상품 정보 summary 연동 ---
    function parsePrice(str) {
        return parseInt((str + "").replace(/[^0-9]/g, "")) || 0;
    }

    function updateOrderSummary() {
        const orderRows = document.querySelectorAll('#orderItemsList tr');
        let totalCount = 0;
        let totalPrice = 0;
        const productTypeCount = orderRows.length;
        orderRows.forEach(row => {
            const qtyCell = row.querySelector('td:nth-child(2)');
            const priceCell = row.querySelector('td:nth-child(3)');
            if (qtyCell && priceCell) {
                const qty = parsePrice(qtyCell.textContent);
                const price = parsePrice(priceCell.textContent);
                totalCount += qty;
                totalPrice += price;
            }
        });
        let shippingFee = totalPrice > 0 && totalPrice < 20000 ? 3000 : 0;
        document.getElementById('summaryProductCount').textContent = productTypeCount;
        document.getElementById('summaryProductPrice').textContent = totalPrice.toLocaleString() + '원';
        document.getElementById('summaryShippingFee').textContent = shippingFee === 0 ? '무료' : shippingFee.toLocaleString() + '원';
        document.getElementById('summaryTotalPrice').textContent = (totalPrice + shippingFee).toLocaleString() + '원';
        document.getElementById('orderTotalPrice').textContent = totalPrice.toLocaleString() + '원';
    }

    updateOrderSummary();

    // --- 다음 주소검색 API 연동 ---
    const addressSearchBtn = document.getElementById('addressSearchBtn');
    if (addressSearchBtn) {
        addressSearchBtn.addEventListener('click', function () {
            new daum.Postcode({
                oncomplete: function (data) {
                    receiverAddress.value = data.address;
                    receiverAddress.readOnly = false;
                    receiverAddress.focus();
                }
            }).open();
        });
    }

    // 필수 입력값 검증 함수
    function validateRequiredFields() {
        const fieldMap = [
            {el: orderMember, label: '주문하시는 분'},
            {el: orderAddress, label: '주소'},
            {el: orderPhone, label: '휴대폰 번호(주문자)'},
            {el: orderEmail, label: '이메일'},
            {el: receiver, label: '받으실 분'},
            {el: receiverAddress, label: '받으실 곳'},
            {el: receiverPhone, label: '휴대폰 번호(배송지)'}
        ];
        for (let f of fieldMap) {
            if (!f.el.value.trim()) {
                alert(`${f.label} 정보를 다시 확인해주세요.`);
                f.el.focus();
                return false;
            }
        }
        if (!orderAgree.checked) {
            alert('구매 동의에 체크해 주세요.');
            orderAgree.focus();
            return false;
        }
        return true;
    }

    // 팝업 중앙 정렬 함수
    function openCenteredPopup(url, name, width, height, htmlContent) {
        const dualScreenLeft = window.screenLeft !== undefined ? window.screenLeft : window.screenX;
        const dualScreenTop = window.screenTop !== undefined ? window.screenTop : window.screenY;
        const w = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
        const h = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;
        const left = ((w / 2) - (width / 2)) + dualScreenLeft;
        const top = ((h / 2) - (height / 2)) + dualScreenTop;
        const popup = window.open(url, name, `width=${width},height=${height},top=${top},left=${left}`);
        if (htmlContent) {
            popup.document.write(htmlContent);
        }
        popup.focus();
        return popup;
    }

    // === 주문/결제번호, 일시 생성 함수 ===
    function getDateTimeStrings() {
        const now = new Date();
        const pad = n => n.toString().padStart(2, '0');
        const y = now.getFullYear();
        const m = pad(now.getMonth() + 1);
        const d = pad(now.getDate());
        const h = pad(now.getHours());
        const min = pad(now.getMinutes());
        const s = pad(now.getSeconds());
        return {
            orderNo: `OD${y}${m}${d}${h}${min}${s}`,
            orderDate: `${y}-${m}-${d}`,
            payNo: `PM${y}${m}${d}${h}${min}${s}`
        };
    }

    // === 주문페이지 진입 시 항상 새로운 주문번호/일시 생성 ===
    (function () {
        const now = new Date();
        const pad = n => n.toString().padStart(2, '0');
        const y = now.getFullYear();
        const m = pad(now.getMonth() + 1);
        const d = pad(now.getDate());
        const h = pad(now.getHours());
        const min = pad(now.getMinutes());
        const s = pad(now.getSeconds());
        const orderNo = `OD${y}${m}${d}${h}${min}${s}`;
        const orderDate = `${y}-${m}-${d}T${h}:${min}:${s}`;
        sessionStorage.setItem('orderId', orderNo);
        sessionStorage.setItem('orderDate', orderDate);
        sessionStorage.removeItem('orderCompleted');
        sessionStorage.removeItem('paymentId');
        sessionStorage.removeItem('idForAdmin');
    })();

    // === 주문 생성 API 호출 ===
    function getOrderProductList() {
        const orderRows = document.querySelectorAll('#orderItemsList tr');
        return Array.from(orderRows).map(row => {
            const name = row.querySelector('.order-title')?.textContent || '';
            const author = row.querySelector('.order-author')?.textContent || '';
            const qty = row.querySelector('td:nth-child(2)')?.textContent.replace(/[^0-9]/g, '') || '1';
            const price = row.querySelector('td:nth-child(3)')?.textContent.replace(/[^0-9]/g, '') || '0';
            const img = row.querySelector('img.order-thumb')?.getAttribute('src') || '';
            const isbn = row.getAttribute('data-isbn') || '';
            return {
                productName: name,
                author: author,
                quantity: parseInt(qty),
                unitPrice: parseInt(price) / parseInt(qty),
                totalPrice: parseInt(price),
                img: img,
                isbn: isbn
            };
        });
    }

    function createOrderOnEntry() {
        const products = getOrderProductList();
        if (!products.length) return;
        const orderId = sessionStorage.getItem('orderId');
        const orderDate = sessionStorage.getItem('orderDate');
        fetch('/api/order/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({products, orderId, orderDate})
        })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.orderId && data.idForAdmin) {
                    sessionStorage.setItem('orderId', data.orderId);
                    sessionStorage.setItem('idForAdmin', data.idForAdmin);
                }
            });
    }

    createOrderOnEntry();

    // === 주문 요약 정보 생성 및 저장 ===
    function createOrderSummary() {
        const orderRows = document.querySelectorAll('#orderItemsList tr');
        const products = Array.from(orderRows).map(row => {
            const name = row.querySelector('.order-title')?.textContent || '';
            const author = row.querySelector('.order-author')?.textContent || '';
            const qty = row.querySelector('td:nth-child(2)')?.textContent.replace(/[^0-9]/g, '') || '1';
            const price = row.querySelector('td:nth-child(3)')?.textContent.replace(/[^0-9]/g, '') || '0';
            const img = row.querySelector('img.order-thumb')?.getAttribute('src') || '';
            const isbn = row.getAttribute('data-isbn') || '';
            return {
                productName: name,
                author: author,
                quantity: parseInt(qty),
                unitPrice: parseInt(price) / parseInt(qty),
                totalPrice: parseInt(price),
                img: img,
                isbn: isbn
            };
        });

        const totalProductPrice = products.reduce((sum, product) => sum + product.totalPrice, 0);
        const shippingFee = totalProductPrice >= 20000 ? 0 : 3000;
        const finalAmount = totalProductPrice + shippingFee;

        const orderSummary = {
            orderNumber: sessionStorage.getItem('orderId'),
            ordererName: orderMember.value,
            productList: products,
            totalProductPrice: totalProductPrice,
            shippingFee: shippingFee,
            finalAmount: finalAmount
        };

        sessionStorage.setItem('orderSummary', JSON.stringify(orderSummary));
        console.log('🔵 주문 요약 정보 저장:', orderSummary);
    }

    // 페이지 로드 시 주문 요약 정보 생성
    createOrderSummary();

    // === 결제 완료 처리 함수 (수정됨) ===
    async function onPaymentSuccess(afterSuccess) {
        const orderId = sessionStorage.getItem('orderId');
        const idForAdmin = sessionStorage.getItem('idForAdmin');

        if (orderId && idForAdmin) {
            try {
                // 1. 주문 상태를 ORDER_COMPLETED로 변경
                await fetch('/api/order/update-status', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        orderId: orderId,
                        idForAdmin: idForAdmin,
                        status: 'ORDER_COMPLETED'
                    })
                });

                // 2. 결제 상태를 PAYMENT_COMPLETED로 변경
                await fetch('/api/payment/complete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        orderId: orderId
                    })
                });

                sessionStorage.setItem('orderCompleted', 'true');
                window.orderFailSent = true;

                // === 이탈 이벤트 리스너 해제 ===
                window.removeEventListener('beforeunload', sendOrderFail);
                window.removeEventListener('unload', sendOrderFail);
                window.removeEventListener('popstate', sendOrderFail);
                document.querySelectorAll('a').forEach(a => {
                    a.removeEventListener('click', sendOrderFail);
                });
                document.querySelectorAll('form').forEach(f => {
                    f.removeEventListener('submit', sendOrderFail);
                });

                // 수정: summary 페이지로 이동 시 주문정보 파라미터 전달
                if (typeof afterSuccess === 'function') {
                    afterSuccess();
                } else {
                    // 기본 동작: 파라미터와 함께 summary 페이지로 이동
                    window.location.href = `/order/summary?orderId=${encodeURIComponent(orderId)}&idForAdmin=${encodeURIComponent(idForAdmin)}`;
                }
            } catch (error) {
                console.error('결제 완료 처리 중 오류:', error);
                if (typeof afterSuccess === 'function') {
                    afterSuccess();
                } else {
                    // 오류 발생 시에도 파라미터와 함께 이동
                    const orderId = sessionStorage.getItem('orderId');
                    const idForAdmin = sessionStorage.getItem('idForAdmin');
                    if (orderId && idForAdmin) {
                        window.location.href = `/order/summary?orderId=${encodeURIComponent(orderId)}&idForAdmin=${encodeURIComponent(idForAdmin)}`;
                    } else {
                        window.location.href = '/order/summary';
                    }
                }
            }
        } else {
            if (typeof afterSuccess === 'function') {
                afterSuccess();
            } else {
                window.location.href = '/order/summary';
            }
        }
    }

    // === 결제 실패 처리 함수 (새로 추가) ===
    async function onPaymentFail() {
        const orderId = sessionStorage.getItem('orderId');
        const idForAdmin = sessionStorage.getItem('idForAdmin');

        if (orderId && idForAdmin && !window.orderFailSent) {
            try {
                // 1. 주문 상태를 ORDER_FAILED로 변경
                await fetch('/api/order/update-status', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        orderId: orderId,
                        idForAdmin: idForAdmin,
                        status: 'ORDER_FAILED'
                    })
                });

                // 2. 결제 상태를 PAYMENT_FAILED로 변경
                await fetch('/api/payment/fail', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        orderId: orderId
                    })
                });

                window.orderFailSent = true;
            } catch (error) {
                console.error('결제 실패 처리 중 오류:', error);
            }
        }
    }

    // === 결제 버튼 클릭 시 paymentId 생성 및 payment 테이블 insert (강화된 디버깅) ===
    // order.js - 결제 버튼 클릭 시 Payment ID와 Date를 동일 시각에 생성

    orderSubmitBtn.addEventListener('click', function (e) {
        e.preventDefault();
        console.log('🔵 결제 버튼 클릭됨');

        if (!validateRequiredFields()) return;

        // 수정: 밀리초까지 정확하게 동일한 시각 생성
        const paymentNow = new Date();
        const pad = n => n.toString().padStart(2, '0');
        const y = paymentNow.getFullYear();
        const m = pad(paymentNow.getMonth() + 1);
        const d = pad(paymentNow.getDate());
        const h = pad(paymentNow.getHours());
        const min = pad(paymentNow.getMinutes());
        const s = pad(paymentNow.getSeconds());

        const paymentId = `PM${y}${m}${d}${h}${min}${s}`;
        const paymentDate = `${y}-${m}-${d}T${h}:${min}:${s}`;

        console.log('🔵 생성된 PaymentId:', paymentId);
        console.log('🔵 생성된 PaymentDate:', paymentDate);
        console.log('🔵 생성 시각:', paymentNow.toISOString());

        sessionStorage.setItem('paymentId', paymentId);

        const orderId = sessionStorage.getItem('orderId');
        const idForAdmin = sessionStorage.getItem('idForAdmin');

        // 결제수단 매핑
        let paymentMethod = '';
        if (paymentKakaoRadio.checked) {
            paymentMethod = 'KP';
            console.log('🔵 선택된 결제수단: 카카오페이 (KP)');
        } else if (paymentAccountRadio.checked) {
            paymentMethod = 'AC';
            console.log('🔵 선택된 결제수단: 무통장입금 (AC)');
        } else {
            console.log('❌ 결제수단이 선택되지 않음');
            alert('결제수단을 선택해 주세요.');
            return;
        }

        // 필수 정보 검증
        if (!orderId || !idForAdmin || !paymentId || !paymentMethod) {
            console.log('❌ 필수 정보 누락');
            alert('결제 정보가 부족합니다. 페이지를 새로고침 후 다시 시도해주세요.');
            return;
        }

        // 새로운 결제 시도 전 기존 PAYMENT_ATTEMPT 상태의 결제건들을 FAILED로 변경
        console.log('🔵 기존 결제건 FAILED 처리 시작');
        fetch('/api/payment/fail', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                orderId: orderId
            })
        })
        .then(res => res.json())
        .then(failData => {
            console.log('🔵 기존 결제건 FAILED 처리 완료:', failData);
            
            // 기존 결제건 처리 완료 후 새로운 결제 시도
            return processNewPayment();
        })
        .catch(error => {
            console.log('🔴 기존 결제건 FAILED 처리 중 오류:', error);
            // 오류가 발생해도 새로운 결제는 진행
            processNewPayment();
        });

        // 새로운 결제 처리 함수
        function processNewPayment() {
            console.log('🔵 새로운 결제 처리 시작');
            
            // Payment API 호출 - 정확한 시각 전달
        const paymentData = {
            orderId: orderId,
            idForAdmin: idForAdmin,
            paymentId: paymentId,
            paymentMethod: paymentMethod,
            paymentDate: paymentDate // 정확히 동일한 시각 전달
        };

        console.log('🔵 Payment API 호출 시작');
        console.log('🔵 전송할 데이터:', JSON.stringify(paymentData, null, 2));

        fetch('/api/payment/attempt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(paymentData)
        })
            .then(response => {
                console.log('🔵 Payment API 응답 상태:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('🔵 Payment API 응답 데이터:', JSON.stringify(data, null, 2));

                if (data.success) {
                    console.log('✅ Payment 테이블 인서트 성공!');

                    // 결제창 열기
                    if (paymentKakaoRadio.checked) {
                        console.log('🔵 카카오페이 결제창 열기');
                        kakaoPayRequest();
                    } else if (paymentAccountRadio.checked) {
                        console.log('🔵 무통장입금 팝업 열기');
                        openAccountPopup();
                    }
                } else {
                    console.log('❌ Payment 테이블 인서트 실패:', data.message);
                    alert('결제 정보 저장에 실패했습니다: ' + data.message);
                }
            })
            .catch(error => {
                console.log('❌ Payment API 호출 중 오류:', error);
                alert('결제 정보 저장 중 오류가 발생했습니다: ' + error.message);
            });
        } // processNewPayment 함수 종료
    });

    // === 페이지 로드 시 세션 정보 확인 (추가) ===
    window.addEventListener('load', function () {
        console.log('🔵 페이지 로드 완료 - 세션 정보 확인:');
        console.log('  - orderId:', sessionStorage.getItem('orderId'));
        console.log('  - idForAdmin:', sessionStorage.getItem('idForAdmin'));
        console.log('  - orderDate:', sessionStorage.getItem('orderDate'));
    });

    // === 카카오페이 결제 함수 (수정됨) ===
    function kakaoPayRequest() {
        const orderSummary = JSON.parse(sessionStorage.getItem('orderSummary') || '{}');
        const payInfo = {
            orderNumber: orderSummary.orderNumber,
            ordererName: orderSummary.ordererName,
            itemName: orderSummary.productList && orderSummary.productList.length > 0 ? orderSummary.productList[0].productName : '주문상품',
            quantity: orderSummary.productList ? orderSummary.productList.length : 1,
            totalAmount: orderSummary.finalAmount,
            paymentId: sessionStorage.getItem('paymentId')
        };

        fetch('/api/kakaopay/ready', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payInfo)
        })
            .then(res => res.json())
            .then(data => {
                if (data && data.next_redirect_pc_url) {
                    const width = 500, height = 700;
                    const dualScreenLeft = window.screenLeft !== undefined ? window.screenLeft : window.screenX;
                    const dualScreenTop = window.screenTop !== undefined ? window.screenTop : window.screenY;
                    const w = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
                    const h = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;
                    const left = ((w / 2) - (width / 2)) + dualScreenLeft;
                    const top = ((h / 2) - (height / 2)) + dualScreenTop;

                    currentPaymentPopup = window.open(data.next_redirect_pc_url, 'kakaoPayPopup', `width=${width},height=${height},top=${top},left=${left}`);

                    // 수정: 팝업 닫힘 감지 및 결제 완료 처리 강화
                    let popupCheckInterval;
                    let paymentCompleted = false;
                    let messageHandlerAdded = false;

                    // 결제 성공 메시지 처리 - 수정됨
                    const handleKakaoPayMessage = (event) => {
                        console.log('🔵 카카오페이 메시지 수신:', event.data);
                        
                        // 결제 성공 메시지 처리
                        if (event.data === 'KAKAO_PAY_SUCCESS' || event.data === 'KAKAO_PAY_SUMMARY') {
                            console.log('✅ 카카오페이 결제 성공 신호 받음:', event.data);
                            paymentCompleted = true;
                            clearInterval(popupCheckInterval);

                            // 결제 완료 처리
                            onPaymentSuccess(function() {
                                const orderId = sessionStorage.getItem('orderId');
                                const idForAdmin = sessionStorage.getItem('idForAdmin');
                                console.log('🔵 서머리 페이지로 이동:', orderId, idForAdmin);
                                
                                if (orderId && idForAdmin) {
                                    window.location.href = `/order/summary?orderId=${encodeURIComponent(orderId)}&idForAdmin=${encodeURIComponent(idForAdmin)}`;
                                } else {
                                    window.location.href = '/order/summary';
                                }
                                
                                // 팝업 닫기
                                if (currentPaymentPopup && !currentPaymentPopup.closed) {
                                    currentPaymentPopup.close();
                                }
                            });

                            // 메시지 리스너 제거
                            window.removeEventListener('message', handleKakaoPayMessage);
                            messageHandlerAdded = false;
                        }
                        // 결제 취소 메시지 처리
                        else if (event.data === 'KAKAO_PAY_CANCEL') {
                            console.log('❌ 카카오페이 결제 취소 신호 받음');
                            paymentCompleted = true;
                            clearInterval(popupCheckInterval);

                            // 결제 취소 처리
                            onPaymentFail();

                            // 메시지 리스너 제거
                            window.removeEventListener('message', handleKakaoPayMessage);
                            messageHandlerAdded = false;
                        }
                        // 결제 실패 메시지 처리
                        else if (event.data === 'KAKAO_PAY_FAIL') {
                            console.log('❌ 카카오페이 결제 실패 신호 받음');
                            paymentCompleted = true;
                            clearInterval(popupCheckInterval);

                            // 결제 실패 처리
                            onPaymentFail();

                            // 메시지 리스너 제거
                            window.removeEventListener('message', handleKakaoPayMessage);
                            messageHandlerAdded = false;
                        }
                    };

                    // 메시지 리스너 추가
                    if (!messageHandlerAdded) {
                        window.addEventListener('message', handleKakaoPayMessage);
                        messageHandlerAdded = true;
                    }

                    const checkClosed = () => {
                        if (currentPaymentPopup && currentPaymentPopup.closed) {
                            console.log('🔴 카카오페이 팝업이 닫혔음');
                            clearInterval(popupCheckInterval);

                            // 메시지 리스너 제거
                            if (messageHandlerAdded) {
                                window.removeEventListener('message', handleKakaoPayMessage);
                                messageHandlerAdded = false;
                            }

                            // 1초 대기 후 결제 완료 확인
                            setTimeout(() => {
                                const orderCompleted = sessionStorage.getItem('orderCompleted');
                                console.log('🔵 결제 완료 상태 확인:', orderCompleted);

                                if (orderCompleted !== 'true' && !paymentCompleted) {
                                    console.log('🔴 결제 미완료 상태로 팝업 닫힘 → 결제 실패 처리');
                                    onPaymentFail();
                                }
                            }, 1000);
                        }
                    };

                    popupCheckInterval = setInterval(checkClosed, 100); // 0.1초마다 체크

                } else {
                    alert('카카오페이 결제창 생성에 실패했습니다.');
                }
            })
            .catch(err => {
                alert('카카오페이 결제 준비 중 오류 발생: ' + err);
            });
    }

    // === KAKAO_PAY_SUMMARY 메시지 수신 시 결제 성공 처리 ===
    window.addEventListener('message', function(event) {
        if (event.data === 'KAKAO_PAY_SUMMARY') {
            // 결제 성공 처리
            onPaymentSuccess();
        }
    });

    // 무통장 입금 팝업 함수 - 팝업 이탈 감지 강화
    function openAccountPopup() {
        currentPaymentPopup = openCenteredPopup('', 'accountPopup', 400, 300, `
        <html><head><title>무통장 입금 안내</title>
        <style>body{font-family:sans-serif;padding:24px;text-align:center;}button{margin-top:24px;padding:10px 24px;font-size:1.1em;border-radius:6px;border:none;background:#222;color:#fff;cursor:pointer;}</style>
        </head><body>
        <h3>주문이 완료되었습니다. 감사합니다.</h3>
        <div style="margin:18px 0 8px 0;">입금은행: <b>패캠은행</b></div>
        <div style="margin-bottom:18px;">계좌번호: <b>123-456-7890</b></div>
        <button id="depositDoneBtn">입금완료</button>
        <script>
        document.getElementById('depositDoneBtn').onclick = async function() {
            if (window.opener && typeof window.opener.onPaymentSuccess === 'function') {
                await window.opener.onPaymentSuccess(function() {
                    const orderId = window.opener.sessionStorage.getItem('orderId');
                    const idForAdmin = window.opener.sessionStorage.getItem('idForAdmin');
                    if (orderId && idForAdmin) {
                        window.opener.location.href = \`/order/summary?orderId=\${encodeURIComponent(orderId)}&idForAdmin=\${encodeURIComponent(idForAdmin)}\`;
                    } else {
                        window.opener.location.href = '/order/summary';
                    }
                    window.close();
                });
            } else if (window.opener) {
                window.opener.location.href = '/order/summary';
                window.close();
            } else {
                window.close();
            }
        };
        </script>
        </body></html>
    `);

        // 수정: 팝업 닫힘 감지 강화
        let popupCheckInterval;
        let paymentCompleted = false;

        const checkClosed = () => {
            if (currentPaymentPopup && currentPaymentPopup.closed) {
                console.log('🔴 무통장입금 팝업이 닫혔음');
                clearInterval(popupCheckInterval);

                // 0.5초 대기 후 결제 완료 확인
                setTimeout(() => {
                    const orderCompleted = sessionStorage.getItem('orderCompleted');
                    console.log('🔵 결제 완료 상태 확인:', orderCompleted);

                    if (orderCompleted !== 'true' && !paymentCompleted) {
                        console.log('🔴 결제 미완료 상태로 팝업 닫힘 → 결제 실패 처리');
                        onPaymentFail();
                    }
                }, 500);
            }
        };

        popupCheckInterval = setInterval(checkClosed, 100); // 0.1초마다 체크
    }

    // 전역에서 접근 가능하도록 window에 등록
    window.onPaymentSuccess = onPaymentSuccess;
    window.onPaymentFail = onPaymentFail;
});

// === 모든 이탈 상황에서 주문상태를 반드시 ORDER_FAILED로 변경 ===
(function () {
    window.orderFailSent = false;

    function sendOrderFail() {
        if (window.orderFailSent) return;
        const orderId = sessionStorage.getItem('orderId');
        const idForAdmin = sessionStorage.getItem('idForAdmin');
        const orderCompleted = sessionStorage.getItem('orderCompleted');

        if (orderId && idForAdmin && orderCompleted !== 'true') {
            // 주문 상태 실패로 변경
            fetch('/api/order/update-status', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    orderId: orderId,
                    idForAdmin: idForAdmin,
                    status: 'ORDER_FAILED'
                }),
                keepalive: true
            });

            // 결제 상태도 함께 실패로 변경
            fetch('/api/payment/fail', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    orderId: orderId
                }),
                keepalive: true
            });

            window.orderFailSent = true;
        }
    }

    // 이벤트 리스너들
    window.addEventListener('beforeunload', sendOrderFail);
    window.addEventListener('unload', sendOrderFail);
    window.addEventListener('popstate', sendOrderFail);

    document.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', function (e) {
            sendOrderFail();
        });
    });

    document.querySelectorAll('form').forEach(f => {
        f.addEventListener('submit', function (e) {
            sendOrderFail();
        });
    });

    // 전역에서 접근 가능하도록 window에 등록
    window.sendOrderFail = sendOrderFail;
})();