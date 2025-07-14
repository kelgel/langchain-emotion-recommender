document.addEventListener('DOMContentLoaded', function() {
    console.log('로그인 페이지 JavaScript 로드 완료');

    // 페이지 모드 상태 관리
    let currentMode = 'login'; // 'login', 'findId', 'findPassword'

    // DOM 요소들 선택
    const elements = {
        loginForm: document.getElementById('loginForm'),
        usernameInput: document.getElementById('username'),
        passwordInput: document.getElementById('password'),
        nameInput: document.getElementById('name'),
        emailInput: document.getElementById('email'),
        mainBtn: document.getElementById('mainBtn'),
        bottomBtn: document.getElementById('bottomBtn'),
        passwordToggle: document.getElementById('passwordToggle'),
        usernameError: document.getElementById('usernameError'),
        passwordError: document.getElementById('passwordError'),
        nameError: document.getElementById('nameError'),
        emailError: document.getElementById('emailError'),
        messageArea: document.getElementById('messageArea'),
        rememberMe: document.getElementById('rememberMe'),
        pageTitle: document.getElementById('pageTitle'),
        findIdLink: document.getElementById('findIdLink'),
        findPasswordLink: document.getElementById('findPasswordLink'),
        usernameGroup: document.getElementById('usernameGroup'),
        passwordGroup: document.getElementById('passwordGroup'),
        nameGroup: document.getElementById('nameGroup'),
        emailGroup: document.getElementById('emailGroup'),
        formOptions: document.getElementById('formOptions'),
        rememberSection: document.getElementById('rememberSection')
    };

    // 초기화
    initializeForm();
    addEventListeners();

    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleFormSubmit);
    }

    /**
     * 폼 초기화
     */
    function initializeForm() {
        // URL 파라미터로 모드 확인
        const urlParams = new URLSearchParams(window.location.search);
        const mode = urlParams.get('mode');

        if (mode === 'findId') {
            switchToFindIdMode();
        } else if (mode === 'findPassword') {
            switchToFindPasswordMode();
        } else {
            switchToLoginMode();
        }

        // 저장된 아이디 불러오기 (로그인 모드일 때만)
        if (currentMode === 'login') {
            const savedUsername = localStorage.getItem('savedUsername');
            if (savedUsername) {
                elements.usernameInput.value = savedUsername;
                elements.rememberMe.checked = true;
            }
        }

        // 초기 버튼 상태 확인
        checkFormValid();
        hideAllMessages();
    }

    /**
     * 이벤트 리스너 등록 (중복 제거)
     */
    function addEventListeners() {
        // 입력 필드 이벤트
        elements.usernameInput.addEventListener('input', handleInputChange);
        elements.usernameInput.addEventListener('blur', validateCurrentFields);

        elements.passwordInput.addEventListener('input', handleInputChange);
        elements.passwordInput.addEventListener('blur', validateCurrentFields);

        elements.nameInput.addEventListener('input', handleInputChange);
        elements.nameInput.addEventListener('blur', validateCurrentFields);

        elements.emailInput.addEventListener('input', handleInputChange);
        elements.emailInput.addEventListener('blur', validateCurrentFields);

        // 비밀번호 보기/숨기기 토글
        elements.passwordToggle.addEventListener('click', togglePasswordVisibility);

        // 폼 제출 이벤트 (한 번만 등록)
        elements.loginForm.addEventListener('submit', handleFormSubmit);

        // 모드 전환 링크
        elements.findIdLink.addEventListener('click', function(e) {
            e.preventDefault();
            switchToFindIdMode();
        });

        elements.findPasswordLink.addEventListener('click', function(e) {
            e.preventDefault();
            switchToFindPasswordMode();
        });

        // 키보드 이벤트 (통합)
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleEnterKey(e);
            } else if (e.key === 'Escape') {
                hideAllMessages();
            }
        });

        // 브라우저 뒤로가기 버튼 처리
        window.addEventListener('popstate', function(event) {
            const urlParams = new URLSearchParams(window.location.search);
            const mode = urlParams.get('mode');

            if (mode === 'findId') {
                switchToFindIdMode();
            } else if (mode === 'findPassword') {
                switchToFindPasswordMode();
            } else {
                switchToLoginMode();
            }
        });

        // 비밀번호 입력 시 한글 입력 방지 (입력값에서 한글 자동 제거) 및 alert 제거
        // IME(한글모드) 입력 자체 차단만 적용
        function preventIME(input) {
            input.addEventListener('compositionstart', function(e) {
                e.preventDefault();
            });
            input.addEventListener('compositionupdate', function(e) {
                e.preventDefault();
            });
            input.addEventListener('compositionend', function(e) {
                e.preventDefault();
            });
            input.style.imeMode = 'disabled';
        }
        if (elements.passwordInput) {
            preventIME(elements.passwordInput);
            elements.passwordInput.addEventListener('input', function() {
                this.value = this.value.replace(/[ㄱ-ㅎㅏ-ㅣ가-힣]/g, '');
            });
        }
        // 아이디찾기/비밀번호찾기 아이디 입력란(한글 입력 불가)
        if (elements.usernameInput) {
            elements.usernameInput.addEventListener('input', function() {
                this.value = this.value.replace(/[ㄱ-ㅎㅏ-ㅣ가-힣]/g, '');
            });
        }
        // 아이디찾기 이메일 입력란(한글, punycode, 허용되지 않은 특수문자 입력 불가)
        if (elements.emailInput) {
            elements.emailInput.addEventListener('input', function() {
                // 한글 제거
                this.value = this.value.replace(/[ㄱ-ㅎㅏ-ㅣ가-힣]/g, '');
                // punycode(xn--) 제거
                this.value = this.value.replace(/xn--[a-z0-9-]+/g, '');
            });
        }
    }

    /**
     * 모드 전환 공통 함수
     */
    function switchMode(mode, config) {
        currentMode = mode;

        // 제목 변경
        elements.pageTitle.textContent = config.title;

        // 폼 필드 표시/숨김
        elements.usernameGroup.style.display = config.showUsername ? 'block' : 'none';
        elements.passwordGroup.style.display = config.showPassword ? 'block' : 'none';
        elements.nameGroup.style.display = config.showName ? 'block' : 'none';
        elements.emailGroup.style.display = config.showEmail ? 'block' : 'none';
        elements.formOptions.style.display = config.showOptions ? 'flex' : 'none';

        // 플레이스홀더 설정
        if (config.usernamePlaceholder) {
            elements.usernameInput.placeholder = config.usernamePlaceholder;
        }

        // 버튼 텍스트 변경
        elements.mainBtn.textContent = config.mainBtnText;
        elements.mainBtn.onclick = null;
        elements.bottomBtn.textContent = config.bottomBtnText;
        elements.bottomBtn.onclick = config.bottomBtnAction;

        // URL 변경
        history.replaceState(null, '', config.url);

        // 폼 초기화
        clearFormInputs();
        hideAllMessages();
        checkFormValid();

        // 포커스 설정
        if (config.focusElement) {
            config.focusElement.focus();
        }
    }

    /**
     * 로그인 모드로 전환
     */
    function switchToLoginMode() {
        switchMode('login', {
            title: '로그인',
            showUsername: true,
            showPassword: true,
            showName: false,
            showEmail: false,
            showOptions: true,
            usernamePlaceholder: '아이디를 입력해 주세요',
            mainBtnText: '로그인',
            bottomBtnText: '회원가입',
            bottomBtnAction: function() { location.href = '/register'; },
            url: '/login'
        });
    }

    /**
     * 아이디 찾기 모드로 전환
     */
    function switchToFindIdMode() {
        switchMode('findId', {
            title: '아이디 찾기',
            showUsername: false,
            showPassword: false,
            showName: true,
            showEmail: true,
            showOptions: false,
            mainBtnText: '아이디 찾기',
            bottomBtnText: '이전',
            bottomBtnAction: function() { switchToLoginMode(); },
            url: '/login?mode=findId',
            focusElement: elements.nameInput
        });
    }

    /**
     * 비밀번호 찾기 모드로 전환
     */
    function switchToFindPasswordMode() {
        switchMode('findPassword', {
            title: '비밀번호 찾기',
            showUsername: true,
            showPassword: false,
            showName: true,
            showEmail: false,
            showOptions: false,
            usernamePlaceholder: '아이디를 입력해 주세요',
            mainBtnText: '비밀번호 찾기',
            bottomBtnText: '이전',
            bottomBtnAction: function() { switchToLoginMode(); },
            url: '/login?mode=findPassword',
            focusElement: elements.usernameInput
        });
    }

    /**
     * 입력 변경 처리
     */
    function handleInputChange() {
        hideAllMessages();
        checkFormValid();
    }

    /**
     * 현재 모드에 맞는 필드 유효성 검사
     */
    function validateCurrentFields() {
        switch (currentMode) {
            case 'login':
                return validateUsername() && validatePassword();
            case 'findId':
                return validateName() && validateEmail();
            case 'findPassword':
                return validateUsername() && validateName();
            default:
                return false;
        }
    }

    /**
     * 개별 필드 유효성 검사 함수들
     */
    function validateUsername() {
        return validateField('username', '아이디를 입력해 주세요.');
    }

    function validatePassword() {
        return validateField('password', '비밀번호를 입력해 주세요.');
    }

    function validateName() {
        return validateField('name', '이름을 입력해 주세요.');
    }

    function validateEmail() {
        const email = elements.emailInput.value.trim();

        if (!email) {
            showError('email', '이메일을 입력해 주세요.');
            return false;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            showError('email', '올바른 이메일 형식을 입력해 주세요.');
            return false;
        }

        hideError('email');
        return true;
    }

    /**
     * 공통 필드 검증 함수
     */
    function validateField(fieldName, errorMessage) {
        const value = elements[fieldName + 'Input'].value.trim();

        if (!value) {
            showError(fieldName, errorMessage);
            return false;
        }

        hideError(fieldName);
        return true;
    }

    /**
     * 폼 유효성 검사 및 버튼 활성화
     */
    function checkFormValid() {
        let isValid = false;

        switch (currentMode) {
            case 'login':
                isValid = elements.usernameInput.value.trim() && elements.passwordInput.value.trim();
                break;
            case 'findId':
                isValid = elements.nameInput.value.trim() && elements.emailInput.value.trim();
                break;
            case 'findPassword':
                isValid = elements.usernameInput.value.trim() && elements.nameInput.value.trim();
                break;
        }

        elements.mainBtn.disabled = !isValid;
    }

    /**
     * 메시지 관리 함수들
     */
    function showMessage(message, type = 'error') {
        elements.messageArea.textContent = message;
        elements.messageArea.className = `message-area show ${type}`;
    }

    function hideMessage() {
        elements.messageArea.classList.remove('show', 'error', 'success', 'info');
        setTimeout(() => {
            if (!elements.messageArea.classList.contains('show')) {
                elements.messageArea.textContent = '';
            }
        }, 300);
    }

    function showError(field, message) {
        const errorElement = elements[field + 'Error'];
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.add('show');
        }
    }

    function hideError(field) {
        const errorElement = elements[field + 'Error'];
        if (errorElement) {
            errorElement.classList.remove('show');
        }
    }

    function hideAllMessages() {
        hideMessage();
        hideError('username');
        hideError('password');
        hideError('name');
        hideError('email');
    }

    /**
     * 비밀번호 보기/숨기기 토글
     */
    function togglePasswordVisibility() {
        const isPassword = elements.passwordInput.type === 'password';
        elements.passwordInput.type = isPassword ? 'text' : 'password';
        elements.passwordToggle.querySelector('.eye-icon').textContent = isPassword ? '🙉' : '🙈';
    }

    /**
     * Enter 키 처리
     */
    function handleEnterKey(e) {
        const activeElement = document.activeElement;

        switch (currentMode) {
            case 'login':
                if (activeElement === elements.usernameInput) {
                    elements.passwordInput.focus();
                } else if (activeElement === elements.passwordInput && !elements.mainBtn.disabled) {
                    submitForm();
                }
                break;
            case 'findId':
                if (activeElement === elements.nameInput) {
                    elements.emailInput.focus();
                } else if (activeElement === elements.emailInput && !elements.mainBtn.disabled) {
                    submitForm();
                }
                break;
            case 'findPassword':
                if (activeElement === elements.usernameInput) {
                    elements.nameInput.focus();
                } else if (activeElement === elements.nameInput && !elements.mainBtn.disabled) {
                    submitForm();
                }
                break;
        }
    }

    /**
     * 폼 제출 처리
     */
    function handleFormSubmit(e) {
        e.preventDefault();
        submitForm();
    }

    /**
     * 실제 폼 제출 로직
     */
    function submitForm() {
        if (!validateCurrentFields()) {
            return;
        }

        showLoading();

        switch (currentMode) {
            case 'login':
                submitLoginForm();
                break;
            case 'findId':
                submitFindIdForm();
                break;
            case 'findPassword':
                submitFindPasswordForm();
                break;
        }
    }

    /**
     * AJAX 요청 공통 함수
     */
    function makeAjaxRequest(url, formData, successCallback) {
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => {
                console.log('서버 응답 상태:', response.status);
                return response.json().then(data => ({ status: response.status, body: data }));
            })
            .then(({ status, body }) => {
                console.log('서버 응답 데이터:', body);
                hideLoading();
                successCallback(status, body);
            })
            .catch(error => {
                console.error(`${url} 에러:`, error);
                hideLoading();
                showMessage(`${url} 중 오류가 발생했습니다.`, 'error');
            });
    }

    /**
     * 로그인 폼 제출
     */
    function submitLoginForm() {
        handleRememberMe();

        const formData = new FormData();
        formData.append('username', elements.usernameInput.value.trim());
        formData.append('password', elements.passwordInput.value.trim());

        const referrer = document.referrer || '/main';
        const previousPage = sessionStorage.getItem('previousPage') || referrer;
        formData.append('redirectUrl', previousPage);

        makeAjaxRequest('/login', formData, (status, body) => {
            if (status === 200 && body.success) {
                console.log('로그인 성공:', body);
                sessionStorage.removeItem('previousPage');
                const redirectUrl = body.redirectUrl || previousPage || '/main';
                window.location.href = redirectUrl;
            } else {
                console.log('로그인 실패:', body.message);
                showMessage(body.message || '로그인에 실패했습니다.', 'error');
                elements.passwordInput.focus();
                elements.passwordInput.select();
            }
        });
    }

    /**
     * 아이디 찾기 폼 제출
     */
    function submitFindIdForm() {
        const formData = new FormData();
        formData.append('name', elements.nameInput.value.trim());
        formData.append('email', elements.emailInput.value.trim());

        makeAjaxRequest('/findId', formData, (status, body) => {
            if (status === 200 && body.success) {
                console.log('아이디 찾기 성공:', body);
                if (body.userInfo && body.userInfo.idForUser) {
                    showMessage(`아이디: ${body.userInfo.idForUser}`, 'info');
                    changeToReturnToLogin();
                }
            } else {
                showMessage(body.message || '아이디 찾기에 실패했습니다.', 'error');
            }
        });
    }

    /**
     * 비밀번호 찾기 폼 제출
     */
    function submitFindPasswordForm() {
        const formData = new FormData();
        formData.append('username', elements.usernameInput.value.trim());
        formData.append('name', elements.nameInput.value.trim());

        makeAjaxRequest('/findPassword', formData, (status, body) => {
            if (status === 200 && body.success) {
                console.log('비밀번호 찾기 성공:', body);
                showMessage(body.message || '임시 비밀번호가 등록된 이메일로 전송되었습니다.', 'success');
                changeToReturnToLogin();
            } else {
                showMessage(body.message || '비밀번호 찾기에 실패했습니다.', 'error');
            }
        });
    }

    /**
     * "로그인하러 가기" 버튼으로 변경 (중복 제거)
     */
    function changeToReturnToLogin() {
        elements.mainBtn.textContent = '로그인하러 가기';
        elements.mainBtn.onclick = function() {
            switchToLoginMode();
            if (currentMode === 'findPassword') {
                elements.usernameInput.value = elements.usernameInput.value;
            } else {
                elements.usernameInput.value = '';
            }
            elements.passwordInput.focus();
        };
    }

    /**
     * 아이디 저장 처리
     */
    function handleRememberMe() {
        const username = elements.usernameInput.value.trim();
        if (elements.rememberMe.checked) {
            localStorage.setItem('savedUsername', username);
        } else {
            localStorage.removeItem('savedUsername');
        }
    }

    /**
     * 로딩 상태 관리
     */
    function showLoading() {
        elements.mainBtn.disabled = true;
        const originalText = elements.mainBtn.textContent;
        elements.mainBtn.setAttribute('data-original-text', originalText);
        elements.mainBtn.textContent = getLoadingText();
    }

    function hideLoading() {
        elements.mainBtn.disabled = false;
        const originalText = elements.mainBtn.getAttribute('data-original-text');
        if (originalText) {
            elements.mainBtn.textContent = originalText;
            elements.mainBtn.removeAttribute('data-original-text');
        }
        checkFormValid();
    }

    function getLoadingText() {
        switch (currentMode) {
            case 'login': return '로그인 중';
            case 'findId': return '아이디 찾기';
            case 'findPassword': return '비밀번호 찾기';
            default: return '처리 중';
        }
    }

    /**
     * 폼 입력 필드 초기화
     */
    function clearFormInputs() {
        elements.usernameInput.value = '';
        elements.passwordInput.value = '';
        elements.nameInput.value = '';
        elements.emailInput.value = '';
    }

    /**
     * 페이지 진입 시 이전 페이지 정보 저장
     */
    function savePreviousPage() {
        const urlParams = new URLSearchParams(window.location.search);
        const redirectParam = urlParams.get('redirect');

        if (redirectParam) {
            sessionStorage.setItem('previousPage', decodeURIComponent(redirectParam));
        } else if (document.referrer && !document.referrer.includes('/login')) {
            sessionStorage.setItem('previousPage', document.referrer);
        } else {
            sessionStorage.setItem('previousPage', '/main');
        }

        console.log('이전 페이지 저장:', sessionStorage.getItem('previousPage'));
    }

    /**
     * URL 파라미터로부터 에러 메시지 확인
     */
    function checkUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const error = urlParams.get('error');

        if (error === 'invalid') {
            showMessage('입력하신 정보가 일치하지 않습니다.\n 다시 확인해 주세요.', 'error');
        } else if (error === 'expired') {
            showMessage('세션이 만료되었습니다. 다시 로그인해주세요.', 'error');
        }
    }

    // 초기 설정 (로그인 모드일 때만)
    if (currentMode === 'login') {
        savePreviousPage();
        checkUrlParams();
    }

    console.log('로그인 페이지 초기화 완료 - 현재 모드:', currentMode);
});