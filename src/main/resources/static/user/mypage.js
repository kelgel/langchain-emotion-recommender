document.addEventListener('DOMContentLoaded', function() {
    console.log('마이페이지 JavaScript 로드 완료');

    // 탭 전환
    document.querySelectorAll('.mypage-tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            console.log('탭 클릭:', this.dataset.tab);
            document.querySelectorAll('.mypage-tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
            const targetPanel = document.querySelector('.tab-' + this.dataset.tab);
            if (targetPanel) {
                targetPanel.classList.add('active');
                console.log('탭 전환 완료:', this.dataset.tab);
                
                // 회원정보 수정 탭으로 돌아올 때 비밀번호 확인 상태 초기화
                if (this.dataset.tab === 'edit') {
                    const pwCheckSection = document.getElementById('pw-check-section');
                    const editSection = document.getElementById('edit-section');
                    if (pwCheckSection && editSection) {
                        pwCheckSection.style.display = 'block';
                        editSection.style.display = 'none';
                        // 비밀번호 입력란 초기화
                        const currentPasswordInput = document.getElementById('currentPassword');
                        if (currentPasswordInput) {
                            currentPasswordInput.value = '';
                        }
                        // 비밀번호 확인 메시지 숨김
                        const pwCheckMsg = document.getElementById('pwCheckMsg');
                        if (pwCheckMsg) {
                            pwCheckMsg.style.display = 'none';
                        }
                    }
                }
            } else {
                console.error('탭 패널을 찾을 수 없습니다:', this.dataset.tab);
            }
        });
    });

    // 비밀번호 보기/숨기기 토글
    function togglePw(inputId, toggleId) {
        const input = document.getElementById(inputId);
        const toggle = document.getElementById(toggleId);
        if (input && toggle) {
        toggle.addEventListener('click', function() {
            if (input.type === 'password') {
                input.type = 'text';
                toggle.textContent = '🙉';
            } else {
                input.type = 'password';
                toggle.textContent = '🙈';
            }
        });
        }
    }
    togglePw('userPwd', 'pwToggle1');
    togglePw('userPwdCheck', 'pwToggle2');

    // 비밀번호 검증 함수
    function isValidPassword(pw) {
        // 6~20자, 2종류 이상 조합(영문, 숫자, 특수문자)
        if (pw.length < 6 || pw.length > 20) return false;
        const hasAlpha = /[a-zA-Z]/.test(pw);
        const hasNum = /[0-9]/.test(pw);
        const hasSpecial = /[~!@#$%^&*()\-_=+\[\]{};:'\",<.>/?\\|]/.test(pw);
        return (hasAlpha + hasNum + hasSpecial) >= 2;
    }

    // 비밀번호 검증 및 일치/불일치 체크
    const pwInput = document.getElementById('userPwd');
    const pwCheckInput = document.getElementById('userPwdCheck');
    const pwMismatchMsg = document.getElementById('pwMismatchMsg');
    const pwMatchMsg = document.getElementById('pwMatchMsg');
    const pwInvalidMsg = document.getElementById('pwInvalidMsg');
    const pwValidMsg = document.getElementById('pwValidMsg');
    
    function checkPwValidation() {
        if (pwInput && pwInvalidMsg && pwValidMsg) {
            const pw = pwInput.value;
            if (pw.length === 0) {
                pwInvalidMsg.style.display = 'none';
                pwValidMsg.style.display = 'none';
            } else if (isValidPassword(pw)) {
                pwInvalidMsg.style.display = 'none';
                pwValidMsg.style.display = 'block';
            } else {
                pwInvalidMsg.style.display = 'block';
                pwValidMsg.style.display = 'none';
            }
        }
        checkPwMatch();
        updateEditBtnState();
    }
    
    function checkPwMatch() {
        if (pwInput && pwCheckInput && pwMismatchMsg && pwMatchMsg) {
            if (pwInput.value && pwCheckInput.value && pwInput.value !== pwCheckInput.value) {
                pwMismatchMsg.style.display = 'block';
                pwMatchMsg.style.display = 'none';
            } else if (pwInput.value && pwCheckInput.value && pwInput.value === pwCheckInput.value) {
                pwMismatchMsg.style.display = 'none';
                pwMatchMsg.style.display = 'block';
            } else {
                pwMismatchMsg.style.display = 'none';
                pwMatchMsg.style.display = 'none';
            }
        }
        updateEditBtnState();
    }

    if (pwInput) pwInput.addEventListener('input', checkPwValidation);
    if (pwCheckInput) pwCheckInput.addEventListener('input', checkPwMatch);

    // 닉네임 중복확인
    const checkNicknameBtn = document.getElementById('checkNickname');
    const nicknameInput = document.getElementById('userNickname');
    let nicknameChecked = true; // 초기값은 검증완료 상태
    let originalNickname = nicknameInput ? nicknameInput.value : '';
    
    if (checkNicknameBtn && nicknameInput) {
        // 닉네임 변경 감지
        nicknameInput.addEventListener('input', function() {
            const currentValue = this.value.trim();
            if (currentValue !== originalNickname) {
                // 값이 변경되었으면 중복확인 필요
                nicknameChecked = false;
                checkNicknameBtn.disabled = false;
            } else {
                // 원래 값과 같으면 검증완료 상태
                nicknameChecked = true;
                checkNicknameBtn.disabled = true;
            }
            updateEditBtnState();
        });
        
    checkNicknameBtn.addEventListener('click', function() {
        const nickname = nicknameInput.value.trim();
        if (!nickname) {
            alert('닉네임을 입력하세요.');
            return;
        }
        
        // 최소자릿수 검증 추가
        if (nickname.length < 2) {
            alert('닉네임의 최소 자릿수는 2자리입니다.');
            return;
        }
            
            fetch(`/api/user/check-nickname?nickname=${encodeURIComponent(nickname)}`)
                .then(res => res.json())
                .then(data => {
                    alert(data.message);
                    if (data.result) {
                        nicknameChecked = true;
                        checkNicknameBtn.disabled = true;
                        originalNickname = nickname; // 새로운 원본값으로 업데이트
                    } else {
                        nicknameChecked = false;
                    }
                    updateEditBtnState();
                })
                .catch(() => alert('서버 오류가 발생했습니다.'));
        });
    }

    // 이메일 도메인 선택/직접입력
    const emailDomain = document.getElementById('userEmailDomain');
    const emailDomainSelect = document.getElementById('emailDomainSelect');
    if (emailDomainSelect && emailDomain) {
    emailDomainSelect.addEventListener('change', function() {
        if (this.value === 'custom') {
            emailDomain.value = '';
            emailDomain.readOnly = false;
            emailDomain.focus();
        } else if (this.value) {
            emailDomain.value = this.value;
            emailDomain.readOnly = true;
        } else {
            emailDomain.value = '';
            emailDomain.readOnly = true;
        }
    });
    }

    // 이메일 중복확인
    const checkEmailBtn = document.getElementById('checkEmail');
    const emailIdInput = document.getElementById('userEmailId');
    let emailChecked = true; // 초기값은 검증완료 상태
    let originalEmail = '';
    
    if (checkEmailBtn && emailIdInput && emailDomain) {
        // 초기 이메일 값 저장
        originalEmail = (emailIdInput.value.trim() + '@' + emailDomain.value.trim());
        
        // 이메일 변경 감지
        function checkEmailChange() {
            const currentEmail = emailIdInput.value.trim() + '@' + emailDomain.value.trim();
            if (currentEmail !== originalEmail) {
                // 값이 변경되었으면 중복확인 필요
                emailChecked = false;
                checkEmailBtn.disabled = false;
            } else {
                // 원래 값과 같으면 검증완료 상태
                emailChecked = true;
                checkEmailBtn.disabled = true;
            }
            updateEditBtnState();
        }
        
        emailIdInput.addEventListener('input', checkEmailChange);
        emailDomain.addEventListener('input', checkEmailChange);
        
        // 이메일 도메인 셀렉트 변경 감지
        const emailDomainSelect = document.getElementById('emailDomainSelect');
        if (emailDomainSelect) {
            emailDomainSelect.addEventListener('change', checkEmailChange);
        }
        
    checkEmailBtn.addEventListener('click', function() {
        const emailId = emailIdInput.value.trim();
        const emailDomainVal = emailDomain.value.trim();
        if (!emailId || !emailDomainVal) {
            alert('이메일을 입력하세요.');
            return;
        }
            
            const email = emailId + '@' + emailDomainVal;
            fetch(`/api/user/check-email?email=${encodeURIComponent(email)}`)
                .then(res => res.json())
                .then(data => {
                    alert(data.message);
                    if (data.result) {
                        emailChecked = true;
                        checkEmailBtn.disabled = true;
                        originalEmail = email; // 새로운 원본값으로 업데이트
                    } else {
                        emailChecked = false;
                    }
                    updateEditBtnState();
                })
                .catch(() => alert('서버 오류가 발생했습니다.'));
        });
    }

    // 주소검색(다음 API)
    const searchAddressBtn = document.getElementById('searchAddress');
    if (searchAddressBtn) {
        searchAddressBtn.addEventListener('click', function() {
            // 실제 다음 주소검색 API 연동 필요
            alert('주소검색(다음 API) 호출(샘플)');
        });
    }

    // 폼 제출(수정)
    const editForm = document.getElementById('mypageEditForm');
    if (editForm) {
    editForm.addEventListener('submit', function(e) {
        e.preventDefault();
            
        // 모든 텍스트/이메일/비밀번호 입력값 앞뒤 공백 trim
        editForm.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]').forEach(function(input) {
            input.value = input.value.trim();
        });
            
            // 폼 데이터 수집
            const formData = {
                userName: document.getElementById('userName').value,
                userNickname: document.getElementById('userNickname').value,
                userPwd: document.getElementById('userPwd').value,
                userEmailId: document.getElementById('userEmailId').value,
                userEmailDomain: document.getElementById('userEmailDomain').value,
                userPhone1: document.getElementById('userPhone1').value,
                userPhone2: document.getElementById('userPhone2').value,
                userPhone3: document.getElementById('userPhone3').value,
                userAddress: document.getElementById('userAddress').value,
                userAddressDetail: document.getElementById('userAddressDetail').value
            };
            
            // API 호출
            fetch('/api/user/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    window.location.href = '/mypage'; // 마이페이지 새로고침
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('회원정보 수정 오류:', error);
                alert('회원정보 수정 중 오류가 발생했습니다.');
            });
        });
    }

    // 한글 입력 방지 함수 (register.js 참고)
    function preventIME(input) {
        if (input) {
        input.addEventListener('compositionstart', function(e) { e.preventDefault(); });
        input.addEventListener('compositionupdate', function(e) { e.preventDefault(); });
        input.addEventListener('compositionend', function(e) { e.preventDefault(); });
        input.style.imeMode = 'disabled';
    }
    }
    
    // 비밀번호, 비밀번호 확인, 이메일 id, 이메일 도메인(직접입력시) 한글 입력 방지
    const emailDomainInput = document.getElementById('userEmailDomain');
    if (pwInput) preventIME(pwInput);
    if (pwCheckInput) preventIME(pwCheckInput);
    if (emailIdInput) preventIME(emailIdInput);
    if (emailDomainInput) preventIME(emailDomainInput);
    
    // 한글 입력시 자동 제거
    function removeKorean(str) {
        return str.replace(/[\u3131-\u314e\u314f-\u3163\uac00-\ud7a3]/g, '');
    }
    
    function removeInvalidPwChars(str) {
        // 영문(대/소), 숫자, 특수문자(~!@#$%^&*()-_=+[{]};:'",<.>/?\|)만 허용
        return str.replace(/[^a-zA-Z0-9~!@#$%^&*()\-_=+\[\]{};:'\",<.>/?\\|]/g, '');
    }
    
    if (pwInput) {
    pwInput.addEventListener('input', function() {
        this.value = removeKorean(this.value);
    });
    }
    if (pwCheckInput) {
    pwCheckInput.addEventListener('input', function() {
        this.value = removeKorean(this.value);
    });
    }
    if (emailIdInput) {
    emailIdInput.addEventListener('input', function() {
        this.value = removeKorean(this.value);
    });
    }
    if (emailDomainInput) {
    emailDomainInput.addEventListener('input', function() {
        if (emailDomainInput.readOnly) return;
        this.value = removeKorean(this.value);
    });
    }

    // 휴대폰 번호 입력란 숫자만 입력 가능
    const phoneInputs = [
        document.getElementById('userPhone1'),
        document.getElementById('userPhone2'),
        document.getElementById('userPhone3')
    ];
    phoneInputs.forEach(function(input) {
        if (input) {
            input.addEventListener('input', function() {
                this.value = this.value.replace(/[^0-9]/g, '');
            });
        }
    });





    // [1] 페이지 진입 시 userInfo의 휴대폰번호, 생년월일 세팅
    // userInfo 값은 Thymeleaf에서 직접 폼에 설정됨
    console.log('사용자 정보는 Thymeleaf에서 직접 폼에 설정됩니다.');



    // 모든 정보 입력+검증 완료 시에만 수정 버튼 활성화
    function updateEditBtnState() {
        const editBtn = document.getElementById('editBtn');
        if (editBtn) {
        const requiredInputs = document.querySelectorAll('#mypageEditForm input[required], #mypageEditForm select[required]');
        let allFilled = true;
        requiredInputs.forEach(input => {
            if (!input.value) allFilled = false;
        });
            
            // 비밀번호 검증 및 일치 확인
            const pwInput = document.getElementById('userPwd');
            const pwCheckInput = document.getElementById('userPwdCheck');
            let pwValid = true;
            let pwMatch = true;
            if (pwInput && pwCheckInput && pwInput.value && pwCheckInput.value) {
                pwValid = isValidPassword(pwInput.value);
                pwMatch = (pwInput.value === pwCheckInput.value);
            }
            
            if (allFilled && nicknameChecked && emailChecked && pwValid && pwMatch) {
            editBtn.disabled = false;
        } else {
            editBtn.disabled = true;
        }
    }
    }
    
    // 모든 입력 필드에 대해 상태 업데이트 이벤트 추가
    document.querySelectorAll('#mypageEditForm input, #mypageEditForm select').forEach(input => {
        input.addEventListener('input', updateEditBtnState);
        input.addEventListener('change', updateEditBtnState);
    });
    
    // 최초 진입 시 상태 반영
    updateEditBtnState();

    // 비밀번호 확인 영역 처리 - 핵심 수정 부분
    const pwCheckSection = document.getElementById('pw-check-section');
    const editSection = document.getElementById('edit-section');
    const pwCheckForm = document.getElementById('pwCheckForm');
    const pwCheckBtn = document.getElementById('pwCheckBtn');
    const pwCheckMsg = document.getElementById('pwCheckMsg');

    console.log('비밀번호 확인 요소들:', {
        pwCheckSection: !!pwCheckSection,
        editSection: !!editSection,
        pwCheckForm: !!pwCheckForm,
        pwCheckBtn: !!pwCheckBtn,
        pwCheckMsg: !!pwCheckMsg
    });

    if (pwCheckForm) {
        console.log('비밀번호 확인 폼 이벤트 리스너 등록');
        pwCheckForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('비밀번호 확인 폼 제출됨');
            
            if (pwCheckMsg) {
            pwCheckMsg.style.display = 'none';
            }
            
            const currentPasswordInput = document.getElementById('currentPassword');
            if (!currentPasswordInput) {
                console.error('currentPassword 입력란을 찾을 수 없습니다.');
                return;
            }
            
            const pw = currentPasswordInput.value.trim();
            if (!pw) {
                if (pwCheckMsg) {
                pwCheckMsg.textContent = '비밀번호를 입력하세요.';
                pwCheckMsg.style.display = 'block';
                }
                return;
            }
            
            if (pwCheckBtn) {
            pwCheckBtn.disabled = true;
            }
            
            console.log('비밀번호 확인 API 호출:', pw);
            
            fetch('/api/user/check-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: pw })
            })
            .then(res => {
                console.log('API 응답 상태:', res.status);
                return res.json();
            })
            .then(data => {
                console.log('API 응답 데이터:', data);
                if (data.success) {
                    console.log('비밀번호 확인 성공 - 화면 전환');
                    if (pwCheckSection) {
                    pwCheckSection.style.display = 'none';
                        console.log('비밀번호 확인 섹션 숨김');
                    }
                    if (editSection) {
                    editSection.style.display = 'block';
                        console.log('회원정보 수정 섹션 표시');
                    }
                } else {
                    console.log('비밀번호 확인 실패:', data.message);
                    if (pwCheckMsg) {
                    pwCheckMsg.textContent = data.message || '비밀번호가 일치하지 않습니다.';
                    pwCheckMsg.style.display = 'block';
                    }
                }
            })
            .catch(error => {
                console.error('비밀번호 확인 API 오류:', error);
                if (pwCheckMsg) {
                pwCheckMsg.textContent = '서버 오류가 발생했습니다.';
                pwCheckMsg.style.display = 'block';
                }
            })
            .finally(() => {
                if (pwCheckBtn) {
                pwCheckBtn.disabled = false;
                }
            });
        });
    } else {
        console.error('비밀번호 확인 폼을 찾을 수 없습니다.');
    }



    // [휴대폰 번호 자동 분리 입력]
    // 휴대폰 번호는 Thymeleaf에서 직접 설정됨
    console.log('휴대폰 번호는 Thymeleaf에서 직접 설정됩니다.');

    // [리뷰 모달 관련 변수]
    const reviewModal = document.getElementById('review-modal');
    const reviewModalTitle = document.getElementById('review-modal-title');
    const reviewTitleInput = document.getElementById('review-title');
    const reviewContentInput = document.getElementById('review-content');
    const reviewLength = document.getElementById('review-length');
    const reviewCancelBtn = document.getElementById('review-cancel-btn');
    const reviewSubmitBtn = document.getElementById('review-submit-btn');
    // const reviewDeleteBtn = document.getElementById('review-delete-btn'); // 삭제버튼 제거됨
    let currentReviewMode = 'write'; // write/edit
    let currentReviewData = {};

    // 리뷰 모달 열기 함수 보완
    function openReviewModal(mode, data) {
        currentReviewMode = mode;
        currentReviewData = data;
        if (mode === 'view') {
            reviewModalTitle.textContent = '작성한 리뷰';
            reviewTitleInput.value = data.title || '';
            reviewContentInput.value = data.content || '';
            reviewTitleInput.readOnly = true;
            reviewContentInput.readOnly = true;
            reviewSubmitBtn.style.display = 'none';
        } else if (mode === 'edit') {
            reviewModalTitle.textContent = '리뷰 수정';
            reviewTitleInput.value = data.title || '';
            reviewContentInput.value = data.content || '';
            reviewTitleInput.readOnly = false;
            reviewContentInput.readOnly = false;
            reviewSubmitBtn.style.display = 'inline-block';
            reviewSubmitBtn.textContent = '수정';
        } else {
            reviewModalTitle.textContent = '리뷰 작성';
            reviewTitleInput.value = '';
            reviewContentInput.value = '';
            reviewTitleInput.readOnly = false;
            reviewContentInput.readOnly = false;
            reviewSubmitBtn.style.display = 'inline-block';
            reviewSubmitBtn.textContent = '등록';
        }
        reviewLength.textContent = `${reviewContentInput.value.length}/500`;
        reviewModal.style.display = 'flex';
    }
    // 리뷰 모달 닫기
    function closeReviewModal() {
        reviewModal.style.display = 'none';
        reviewTitleInput.value = '';
        reviewContentInput.value = '';
    }
    // 리뷰 글자수 표시
    if (reviewContentInput) {
        reviewContentInput.addEventListener('input', function() {
            reviewLength.textContent = `${this.value.length}/500`;
        });
    }
    // 리뷰 모달 취소 버튼
    if (reviewCancelBtn) {
        reviewCancelBtn.onclick = closeReviewModal;
    }
    // 리뷰 모달 등록/수정 버튼
    if (reviewSubmitBtn) {
        reviewSubmitBtn.onclick = function() {
            const title = reviewTitleInput.value.trim();
            const content = reviewContentInput.value.trim();
            if (!title || !content) {
                alert('제목과 내용을 모두 입력해주세요.');
                return;
            }
            if (title.length > 50 || content.length > 500) {
                alert('제한 길이를 초과했습니다.');
                return;
            }
            let url = currentReviewMode === 'write' ? '/api/review/write' : '/api/review/edit';
            let body = currentReviewMode === 'write'
                ? { orderId: currentReviewData.orderId, isbn: currentReviewData.isbn, title, content }
                : { reviewId: currentReviewData.reviewId, title, content };
            fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                closeReviewModal();
                loadOrderHistory(1, true); // 토글 상태 유지
            });
        };
    }
    // 모달 바깥 클릭 시 닫기
    if (reviewModal) {
        reviewModal.addEventListener('click', function(e) {
            if (e.target === reviewModal) closeReviewModal();
        });
    }

    // 토글 상태 저장용 변수
    let openOrderIds = new Set();

    // 주문내역 조회 기능 loadOrderHistory 내부에 추가/수정
    function loadOrderHistory(page = 1, preserveToggleState = false) {
        fetch('/api/user/orders')
            .then(res => res.json())
            .then(orders => {
                const orderList = document.querySelector('.order-list');
                if (!orderList) return;
                orderList.innerHTML = '';
                // 최신순 정렬(이미 최신순이면 생략 가능)
                if (Array.isArray(orders)) {
                    orders = orders.sort((a, b) => new Date(b.orderDate) - new Date(a.orderDate));
                } else {
                    alert('주문내역을 불러오지 못했습니다.');
                    return;
                }
                const pageSize = 10;
                const totalPages = Math.ceil(orders.length / pageSize);
                const currentPage = Math.max(1, Math.min(page, totalPages));
                const startIdx = (currentPage - 1) * pageSize;
                const endIdx = startIdx + pageSize;
                const pageOrders = orders.slice(startIdx, endIdx);
                // 주문상태 한글 매핑
                const statusKorMap = {
                  ORDER_REQUESTED: '주문요청',
                  ORDER_FAILED: '주문실패',
                  ORDER_COMPLETED: '주문완료',
                  PREPARING_PRODUCT: '상품준비중',
                  SHIPPING: '배송중',
                  DELIVERED: '배송완료',
                  CANCEL_COMPLETED: '주문취소완료'
                };
                if (orders.length === 0) {
                    orderList.innerHTML = '<div style="text-align:center;padding:50px;color:#666;">주문내역이 없습니다.</div>';
                } else {
                    pageOrders.forEach(order => {
                        const productKinds = order.orderDetails.length;
                        // 배송비 계산
                        const productTotalPrice = order.orderDetails.reduce((sum, detail) => sum + detail.totalProductPrice, 0);
                        const shippingFee = productTotalPrice >= 20000 ? 0 : 3000;
                        const totalPrice = (productTotalPrice + shippingFee).toLocaleString();
                        const shippingMessage = shippingFee > 0 ? ' (배송비 3,000원 포함)' : '';
                        const orderDate = new Date(order.orderDate).toISOString().slice(0, 10);
                        const statusKor = statusKorMap[order.orderStatus] || order.orderStatus;
                        const isCancelable = order.orderStatus === 'ORDER_COMPLETED';
                        const isReviewable = order.orderStatus === 'DELIVERED';
                        const detailRows = order.orderDetails.map(detail => {
                            // 리뷰 버튼 상태 결정
                            let reviewBtns = '';
                            if (isReviewable) {
                                if (!detail.hasReview) {
                                    reviewBtns = `<button class="review-write-btn btn-black" style="width:70px;height:26px;font-size:0.85em;padding:0;" data-order-id="${order.orderId}" data-isbn="${detail.isbn}">리뷰작성</button>`;
                                } else {
                                    reviewBtns = `
                                        <div style="display:flex;flex-direction:column;gap:4px;align-items:center;">
                                            <button class="review-view-btn btn-gray" style="width:70px;height:26px;font-size:0.85em;padding:0;" data-title="${detail.reviewTitle || ''}" data-content="${detail.reviewContent || ''}">작성리뷰</button>
                                            <button class="review-edit-btn btn-black" style="width:70px;height:26px;font-size:0.85em;padding:0;" data-review-id="${detail.reviewId}" data-title="${detail.reviewTitle || ''}" data-content="${detail.reviewContent || ''}">수정</button>
                                            <button class="review-delete-btn btn-red" style="width:70px;height:26px;font-size:0.85em;padding:0;" data-review-id="${detail.reviewId}">삭제</button>
                                        </div>
                                    `;
                                }
                            } else {
                                reviewBtns = '<button class="review-btn" disabled style="width:70px;height:26px;font-size:0.85em;padding:0;background:#ccc;">리뷰불가</button>';
                            }
                            return `
                                <tr>
                                    <td class="order-product-cell">
                                        <a href="/product/detail/${detail.isbn}" style="text-decoration:none;color:inherit;display:inline-block;vertical-align:middle;">
                                            <img src="${detail.img || '/product/noimg.png'}" class="order-product-img" style="width:48px;height:64px;object-fit:cover;margin-right:10px;vertical-align:middle;border-radius:5px;">
                                        </a>
                                        <div style="display:inline-block;vertical-align:middle;">
                                            <a href="/product/detail/${detail.isbn}" style="text-decoration:none;color:inherit;">
                                                <div class="book-title" style="font-weight:600;">${detail.productTitle}</div>
                                            </a>
                                            <div class="book-author" style="font-size:0.95em;color:#666;">${detail.author}</div>
                                        </div>
                                    </td>
                                    <td>${detail.orderItemQuantity}개</td>
                                    <td>${detail.totalProductPrice.toLocaleString()}원</td>
                                    <td>${reviewBtns}</td>
                                </tr>
                            `;
                        }).join('');
                        const orderBox = document.createElement('div');
                        orderBox.className = 'order-box';
                        orderBox.setAttribute('data-order-id', order.orderId);
                        orderBox.innerHTML = `
                            <div class="order-header">
                                <div>
                                    <div style="font-size:1.08em;font-weight:500;">주문번호: ${order.orderId}</div>
                                    <div style="margin-top:2px;">주문일시: ${orderDate}</div>
                                    <div style="margin-top:2px;">주문상태: ${statusKor}</div>
                                    <div style="margin-top:2px;">총 ${productKinds}개의 상품 / 결제금액: <span style="color:#e53935;font-weight:600;">${totalPrice}원</span><span style="color:#666;font-size:0.9em;">${shippingMessage}</span></div>
                                </div>
                                <div style="display:flex;align-items:flex-start;gap:10px;">
                                    <button class="order-cancel-btn btn-black" style="width:4cm;height:36px;font-size:0.95em;padding:0;" ${isCancelable ? '' : 'disabled'}>주문취소</button>
                                    <button class="order-toggle-btn" style="font-size:1.2em;background:none;border:none;cursor:pointer;width:36px;height:36px;">▼</button>
                                </div>
                            </div>
                            <div class="order-detail-table-wrap">
                                <table class="order-detail-table">
                                    <colgroup>
                                        <col style="width: 40%">
                                        <col style="width: 20%">
                                        <col style="width: 20%">
                                        <col style="width: 20%">
                                    </colgroup>
                                    <thead>
                                        <tr style="background:#f8f8f8;">
                                            <th>상품정보</th>
                                            <th>수량</th>
                                            <th>금액</th>
                                            <th>리뷰</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${detailRows}
                                    </tbody>
                                </table>
                            </div>
                        `;
                        // 주문취소 버튼 이벤트
                        setTimeout(() => {
                            const cancelBtn = orderBox.querySelector('.order-cancel-btn');
                            if (cancelBtn) {
                                cancelBtn.onclick = function() {
                                    if (!isCancelable) {
                                        alert('이 상태에서는 주문취소가 불가능합니다.');
                                        return;
                                    }
                                    if (confirm('정말 주문을 취소하시겠습니까?')) {
                                        fetch('/api/orders/cancel', {
                                            method: 'POST',
                                            headers: { 'Content-Type': 'application/json' },
                                            body: JSON.stringify({ orderId: order.orderId })
                                        })
                                        .then(res => res.json())
                                        .then(data => {
                                            alert(data.message);
                                            loadOrderHistory(1, true);
                                        });
                                    }
                                };
                            }
                            // 리뷰작성/수정/삭제/작성리뷰 버튼 이벤트
                            orderBox.querySelectorAll('.review-write-btn').forEach(btn => {
                                btn.onclick = function() {
                                    openReviewModal('write', { orderId: btn.dataset.orderId, isbn: btn.dataset.isbn });
                                };
                            });
                            orderBox.querySelectorAll('.review-edit-btn').forEach(btn => {
                                btn.onclick = function() {
                                    openReviewModal('edit', { reviewId: btn.dataset.reviewId, title: btn.dataset.title, content: btn.dataset.content });
                                };
                            });
                            orderBox.querySelectorAll('.review-delete-btn').forEach(btn => {
                                btn.onclick = function() {
                                    if (confirm('리뷰를 삭제하시겠습니까?')) {
                                        fetch('/api/review/delete', {
                                            method: 'POST',
                                            headers: { 'Content-Type': 'application/json' },
                                            body: JSON.stringify({ reviewId: btn.dataset.reviewId })
                                        })
                                        .then(res => res.json())
                                        .then(data => {
                                            alert(data.message);
                                            loadOrderHistory(1, true);
                                        });
                                    }
                                };
                            });
                            orderBox.querySelectorAll('.review-view-btn').forEach(btn => {
                                btn.onclick = function() {
                                    // 읽기 전용 모달
                                    openReviewModal('view', { title: btn.dataset.title, content: btn.dataset.content });
                                    reviewTitleInput.readOnly = true;
                                    reviewContentInput.readOnly = true;
                                    reviewSubmitBtn.style.display = 'none';
                                };
                            });
                        }, 0);
                        orderList.appendChild(orderBox);
                    });
                    // 토글 상태 복원 (preserveToggleState가 true인 경우)
                    if (preserveToggleState) {
                        pageOrders.forEach(order => {
                            if (openOrderIds.has(order.orderId)) {
                                const orderBox = document.querySelector(`[data-order-id="${order.orderId}"]`);
                                if (orderBox) {
                                    const tableWrap = orderBox.querySelector('.order-detail-table-wrap');
                                    const toggleBtn = orderBox.querySelector('.order-toggle-btn');
                                    if (tableWrap && toggleBtn) {
                                        tableWrap.style.display = 'block';
                                        toggleBtn.textContent = '▲';
                                    }
                                }
                            }
                        });
                    }
                    
                    // 토글 버튼 이벤트
                    document.querySelectorAll('.order-toggle-btn').forEach(btn => {
                        btn.addEventListener('click', function() {
                            const orderBox = this.closest('.order-box');
                            const orderId = orderBox.getAttribute('data-order-id');
                            const tableWrap = orderBox.querySelector('.order-detail-table-wrap');
                            
                            if (tableWrap.style.display === 'none' || !tableWrap.style.display) {
                                tableWrap.style.display = 'block';
                                this.textContent = '▲';
                                openOrderIds.add(orderId);
                            } else {
                                tableWrap.style.display = 'none';
                                this.textContent = '▼';
                                openOrderIds.delete(orderId);
                            }
                        });
                    });
                    // 리뷰 작성 버튼 이벤트
                    document.querySelectorAll('.review-btn:not([disabled])').forEach(btn => {
                        btn.addEventListener('click', function() {
                            const isbn = this.dataset.isbn;
                            if (isbn) {
                                window.location.href = `/review?isbn=${isbn}`;
                            }
                        });
                    });
                    // 페이지네이션 버튼 추가 - 개선된 그룹화 방식
                    const paginationContainer = document.createElement('div');
                    paginationContainer.className = 'pagination-container';
                    if (totalPages > 1) {
                        const btns = document.createElement('div');
                        btns.className = 'pagination-btns';
                        
                        // 10개 이하면 기존 방식
                        if (totalPages <= 10) {
                            for (let i = 1; i <= totalPages; i++) {
                                const btn = document.createElement('button');
                                btn.type = 'button';
                                btn.className = (i === currentPage) ? 'pagination-btn current' : 'pagination-btn';
                                btn.setAttribute('data-page', i);
                                btn.textContent = i;
                                btn.addEventListener('click', function() {
                                    loadOrderHistory(i);
                                    window.scrollTo({top: 0, behavior: 'smooth'});
                                });
                                btns.appendChild(btn);
                            }
                        } else {
                            // 10개 초과시 그룹화 방식
                            const currentGroup = Math.ceil(currentPage / 10);
                            const startPage = (currentGroup - 1) * 10 + 1;
                            const endPage = Math.min(currentGroup * 10, totalPages);
                            
                            // 처음 버튼 (2그룹 이상일 때)
                            if (currentGroup > 1) {
                                const firstBtn = document.createElement('button');
                                firstBtn.type = 'button';
                                firstBtn.className = 'pagination-btn first-btn';
                                firstBtn.textContent = '처음';
                                firstBtn.addEventListener('click', function() {
                                    loadOrderHistory(1);
                                    window.scrollTo({top: 0, behavior: 'smooth'});
                                });
                                btns.appendChild(firstBtn);
                            }
                            
                            // 이전 그룹 버튼 (2그룹 이상일 때)
                            if (currentGroup > 1) {
                                const prevBtn = document.createElement('button');
                                prevBtn.type = 'button';
                                prevBtn.className = 'pagination-btn prev-group-btn';
                                prevBtn.textContent = '이전';
                                const prevGroupLastPage = startPage - 1;
                                prevBtn.addEventListener('click', function() {
                                    loadOrderHistory(prevGroupLastPage);
                                    window.scrollTo({top: 0, behavior: 'smooth'});
                                });
                                btns.appendChild(prevBtn);
                            }
                            
                            // 현재 그룹의 페이지 번호들
                            for (let i = startPage; i <= endPage; i++) {
                                const btn = document.createElement('button');
                                btn.type = 'button';
                                btn.className = (i === currentPage) ? 'pagination-btn current' : 'pagination-btn';
                                btn.setAttribute('data-page', i);
                                btn.textContent = i;
                                btn.addEventListener('click', function() {
                                    loadOrderHistory(i);
                                    window.scrollTo({top: 0, behavior: 'smooth'});
                                });
                                btns.appendChild(btn);
                            }
                            
                            // 다음 그룹 버튼 (마지막 그룹이 아닐 때)
                            if (endPage < totalPages) {
                                const nextBtn = document.createElement('button');
                                nextBtn.type = 'button';
                                nextBtn.className = 'pagination-btn next-group-btn';
                                nextBtn.textContent = '다음';
                                const nextGroupFirstPage = endPage + 1;
                                nextBtn.addEventListener('click', function() {
                                    loadOrderHistory(nextGroupFirstPage);
                                    window.scrollTo({top: 0, behavior: 'smooth'});
                                });
                                btns.appendChild(nextBtn);
                            }
                            
                            // 끝 버튼 (마지막 그룹이 아닐 때)
                            if (endPage < totalPages) {
                                const lastBtn = document.createElement('button');
                                lastBtn.type = 'button';
                                lastBtn.className = 'pagination-btn last-btn';
                                lastBtn.textContent = '끝';
                                lastBtn.addEventListener('click', function() {
                                    loadOrderHistory(totalPages);
                                    window.scrollTo({top: 0, behavior: 'smooth'});
                                });
                                btns.appendChild(lastBtn);
                            }
                        }
                        
                        paginationContainer.appendChild(btns);
                        orderList.appendChild(paginationContainer);
                    }
                }
            })
            .catch(error => {
                console.error('주문내역 조회 오류:', error);
                const orderList = document.querySelector('.order-list');
                if (orderList) {
                    orderList.innerHTML = '<div style="text-align:center;padding:50px;color:#e53935;">주문내역을 불러오는 중 오류가 발생했습니다.</div>';
                }
            });
    }
    // 주문내역 조회 탭 클릭시 데이터 로드
    document.querySelectorAll('.mypage-tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.dataset.tab === 'orders') {
                loadOrderHistory(1);
            }
        });
    });

    console.log('마이페이지 JavaScript 초기화 완료');
});
