document.addEventListener('DOMContentLoaded', function() {
    // referer 정보를 세션스토리지에 저장
    const referer = document.referrer;
    if (referer && !referer.includes('/register')) {
        sessionStorage.setItem('registerReferer', referer);
    }
    
    // 생년월일 셀렉트 옵션 동적 생성
    const yearSelect = document.getElementById('birthYear');
    const monthSelect = document.getElementById('birthMonth');
    const daySelect = document.getElementById('birthDay');
    const now = new Date();
    const thisYear = now.getFullYear();

    // 년도: 1920~현재년도
    for (let y = thisYear; y >= 1920; y--) {
        const opt = document.createElement('option');
        opt.value = y;
        opt.textContent = y + '년';
        yearSelect.appendChild(opt);
    }
    // 월
    for (let m = 1; m <= 12; m++) {
        const opt = document.createElement('option');
        opt.value = m.toString().padStart(2, '0');
        opt.textContent = m + '월';
        monthSelect.appendChild(opt);
    }
    // 일
    for (let d = 1; d <= 31; d++) {
        const opt = document.createElement('option');
        opt.value = d.toString().padStart(2, '0');
        opt.textContent = d + '일';
        daySelect.appendChild(opt);
    }

    // 이메일 도메인 선택/직접입력
    const emailDomain = document.getElementById('userEmailDomain');
    const emailDomainSelect = document.getElementById('emailDomainSelect');
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
        checkEmailBtn.disabled = false;
    });

    // 비밀번호 보기/숨기기(원숭이 이모지)
    function togglePw(inputId, toggleId) {
        const input = document.getElementById(inputId);
        const toggle = document.getElementById(toggleId);
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
    togglePw('userPwd', 'pwToggle1');
    togglePw('userPwdCheck', 'pwToggle2');

    // 비밀번호 검증 및 일치/불일치 체크
    const pwInput = document.getElementById('userPwd');
    const pwCheckInput = document.getElementById('userPwdCheck');
    const pwMismatchMsg = document.getElementById('pwMismatchMsg');
    const pwMatchMsg = document.getElementById('pwMatchMsg');
    const pwInvalidMsg = document.getElementById('pwInvalidMsg');
    const pwValidMsg = document.getElementById('pwValidMsg');
    
    function checkPwValidation() {
        // 한글 제거 및 특수문자 필터링
        let val = removeKorean(pwInput.value);
        val = removeInvalidPwChars(val);
        if (val.length > 20) {
            alert('비밀번호는 최대 20자까지 입력 가능합니다.');
            val = val.slice(0, 20);
        }
        pwInput.value = val;
        
        const pw = pwInput.value;
        if (pw.length === 0) {
            // 비밀번호가 비어있으면 모든 메시지 숨김
            pwInvalidMsg.style.display = 'none';
            pwValidMsg.style.display = 'none';
        } else if (isValidPassword(pw)) {
            pwInvalidMsg.style.display = 'none';
            pwValidMsg.style.display = 'block';
        } else {
            pwInvalidMsg.style.display = 'block';
            pwValidMsg.style.display = 'none';
        }
        checkPwMatch();
        updateRegisterBtnState();
    }
    
    function checkPwMatch() {
        // 비밀번호 확인 필드 필터링
        let val = removeKorean(pwCheckInput.value);
        val = removeInvalidPwChars(val);
        if (val.length > 20) {
            alert('비밀번호는 최대 20자까지 입력 가능합니다.');
            val = val.slice(0, 20);
        }
        pwCheckInput.value = val;
        
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
        updateRegisterBtnState();
    }
    pwInput.addEventListener('input', checkPwValidation);
    pwCheckInput.addEventListener('input', checkPwMatch);

    // 닉네임 중복확인 (실제 API 호출, fetch 응답 체크)
    const checkNicknameBtn = document.getElementById('checkNickname');
    const nicknameInput = document.getElementById('userNickname');
    let nicknameChecked = false;
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
        
        fetch(`/api/check-nickname?nickname=${encodeURIComponent(nickname)}`)
            .then(res => { if (!res.ok) throw new Error('서버 오류'); return res.json(); })
            .then(data => {
                if (data.duplicated) {
                    alert('이미 사용중인 닉네임입니다.');
                    nicknameChecked = false;
                } else {
                    alert('사용 가능한 닉네임입니다.');
                    checkNicknameBtn.disabled = true;
                    nicknameChecked = true;
                }
                updateRegisterBtnState();
            })
            .catch(() => {
                if (!window.__nicknameErrorAlerted) {
                    alert('서버 오류가 발생했습니다.');
                    window.__nicknameErrorAlerted = true;
                    setTimeout(() => { window.__nicknameErrorAlerted = false; }, 1000);
                }
            });
    });
    nicknameInput.addEventListener('input', function() {
        if (this.value.length > 10) {
            alert('닉네임은 최대 10자까지 입력 가능합니다.');
            this.value = this.value.slice(0, 10);
        }
        checkNicknameBtn.disabled = false;
        nicknameChecked = false;
        updateRegisterBtnState();
    });

    // 아이디 중복확인 (실제 API 호출, fetch 응답 체크)
    const checkUserIdBtn = document.getElementById('checkUserId');
    const userIdInput = document.getElementById('userId');
    let userIdChecked = false;
    checkUserIdBtn.addEventListener('click', function() {
        const userId = userIdInput.value.trim();
        if (!userId) {
            alert('아이디를 입력하세요.');
            return;
        }
        
        // 최소자릿수 검증 추가
        if (userId.length < 6) {
            alert('아이디의 최소 자릿수는 6자리입니다.');
            return;
        }
        
        fetch(`/api/check-id?userId=${encodeURIComponent(userId)}`)
            .then(res => { if (!res.ok) throw new Error('서버 오류'); return res.json(); })
            .then(data => {
                if (data.duplicated) {
                    alert('이미 사용중인 아이디입니다.');
                    userIdChecked = false;
                } else {
                    alert('사용 가능한 아이디입니다.');
                    checkUserIdBtn.disabled = true;
                    userIdChecked = true;
                }
                updateRegisterBtnState();
            })
            .catch(() => {
                if (!window.__idErrorAlerted) {
                    alert('서버 오류가 발생했습니다.');
                    window.__idErrorAlerted = true;
                    setTimeout(() => { window.__idErrorAlerted = false; }, 1000);
                }
            });
    });
    const checkEmailBtn = document.getElementById('checkEmail');
    const emailIdInput = document.getElementById('userEmailId');
    let emailChecked = false;

    // IME(한글모드) 입력 자체를 막는 함수
    function preventIME(input) {
        input.addEventListener('compositionstart', function(e) { e.preventDefault(); });
        input.addEventListener('compositionupdate', function(e) { e.preventDefault(); });
        input.addEventListener('compositionend', function(e) { e.preventDefault(); });
        input.style.imeMode = 'disabled';
    }
    preventIME(userIdInput);
    preventIME(pwInput);
    preventIME(pwCheckInput);
    preventIME(emailIdInput);
    userIdInput.addEventListener('input', function() {
        this.value = this.value.replace(/[ㄱ-ㅎㅏ-ㅣ가-힣]/g, '');
    });
    emailIdInput.addEventListener('input', function() {
        this.value = this.value.replace(/[ㄱ-ㅎㅏ-ㅣ가-힣]/g, '');
    });

    // 이메일 중복확인 (실제 API 호출, fetch 응답 체크)
    checkEmailBtn.addEventListener('click', function() {
        const emailId = emailIdInput.value.trim();
        const emailDomainVal = emailDomain.value.trim();
        if (!emailId || !emailDomainVal) {
            alert('이메일을 입력하세요.');
            return;
        }
        const email = emailId + '@' + emailDomainVal;
        fetch(`/api/check-email?email=${encodeURIComponent(email)}`)
            .then(res => { if (!res.ok) throw new Error('서버 오류'); return res.json(); })
            .then(data => {
                if (data.duplicated) {
                    alert('이미 사용중인 이메일입니다.');
                    emailChecked = false;
                } else {
                    alert('사용 가능한 이메일입니다.');
                    checkEmailBtn.disabled = true;
                    emailDomainSelect.disabled = true;
                    emailChecked = true;
                }
                updateRegisterBtnState();
            })
            .catch(() => {
                if (!window.__emailErrorAlerted) {
                    alert('서버 오류가 발생했습니다.');
                    window.__emailErrorAlerted = true;
                    setTimeout(() => { window.__emailErrorAlerted = false; }, 1000);
                }
            });
    });
    emailIdInput.addEventListener('input', function() {
        this.value = this.value.replace(/\s+/g, '');
        this.value = this.value.replace(/[ㄱ-ㅎㅏ-ㅣ가-힣]/g, '');
        // 이메일 id는 영문, 숫자, 일부 특수문자 허용(기존 로직 유지)
        updateRegisterBtnState();
    });

    // 가입확인 (이름+생년월일, 실제 API 호출, fetch 응답 체크)
    const checkJoinableBtn = document.getElementById('checkJoinable');
    const nameInput = document.getElementById('userName');
    let joinableChecked = false;
    checkJoinableBtn.addEventListener('click', function() {
        const name = nameInput.value.trim();
        const year = yearSelect.value;
        const month = yearSelect.value ? monthSelect.value : '';
        const day = yearSelect.value && monthSelect.value ? daySelect.value : '';
        if (!name || !year || !month || !day) {
            alert('이름과 생년월일을 모두 입력하세요.');
            return;
        }
        
        // 미래날짜 검증 추가
        const birthDate = `${year}-${month}-${day}`;
        const selectedDate = new Date(birthDate);
        const today = new Date();
        today.setHours(0, 0, 0, 0); // 시간 부분 제거하여 날짜만 비교
        
        if (selectedDate > today) {
            alert('생년월일은 오늘 날짜보다 미래일 수 없습니다.');
            return;
        }
        
        console.log('가입확인', name, birthDate);
        fetch(`/api/check-joinable?userName=${encodeURIComponent(name)}&userBirth=${birthDate}`)
            .then(res => { if (!res.ok) throw new Error('서버 오류'); return res.json(); })
            .then(data => {
                alert(data.message);
                joinableChecked = data.joinable;
                checkJoinableBtn.disabled = data.joinable;
                updateRegisterBtnState();
            })
            .catch(() => {
                if (!window.__joinableErrorAlerted) {
                    alert('서버 오류가 발생했습니다.');
                    window.__joinableErrorAlerted = true;
                    setTimeout(() => { window.__joinableErrorAlerted = false; }, 1000);
                }
            });
    });
    nameInput.addEventListener('input', function() {
        checkJoinableBtn.disabled = false;
        joinableChecked = false;
        updateRegisterBtnState();
    });
    yearSelect.addEventListener('change', function() {
        checkJoinableBtn.disabled = false;
        joinableChecked = false;
        updateRegisterBtnState();
    });
    monthSelect.addEventListener('change', function() {
        checkJoinableBtn.disabled = false;
        joinableChecked = false;
        updateRegisterBtnState();
    });
    daySelect.addEventListener('change', function() {
        checkJoinableBtn.disabled = false;
        joinableChecked = false;
        updateRegisterBtnState();
    });

    // 다음 우편번호 검색 API 연동
    document.getElementById('searchAddress').addEventListener('click', function() {
        new daum.Postcode({
            oncomplete: function(data) {
                document.getElementById('userAddress').value = data.address;
                document.getElementById('userAddressDetail').focus();
            }
        }).open();
    });

    // 상세주소를 제외한 모든 입력박스에서 공백 입력 방지
    document.querySelectorAll('input:not(#userAddressDetail)').forEach(function(input) {
        input.addEventListener('keydown', function(e) {
            if (e.key === ' ') {
                e.preventDefault();
            }
        });
        input.addEventListener('input', function(e) {
            if (this.value.includes(' ')) {
                this.value = this.value.replace(/\s+/g, '');
            }
        });
    });

    // 아이디 입력 조건 및 중복확인
    userIdInput.addEventListener('input', function() {
        this.value = this.value.replace(/\s+/g, '');
        this.value = this.value.replace(/[ㄱ-ㅎㅏ-ㅣ가-힣]/g, '');
        this.value = this.value.replace(/[^a-z0-9]/g, '');
        if (this.value.length > 15) {
            alert('아이디는 최대 15자까지 입력 가능합니다.');
            this.value = this.value.slice(0, 15);
        }
        checkUserIdBtn.disabled = false;
        userIdChecked = false;
        updateRegisterBtnState();
    });
    // 이메일 id 입력란(공백, 한글 입력 불가, 영문/숫자/특수문자만)
    emailIdInput.addEventListener('input', function() {
        this.value = this.value.replace(/\s+/g, '');
        this.value = this.value.replace(/[ㄱ-ㅎㅏ-ㅣ가-힣]/g, '');
        // 이메일 id는 영문, 숫자, 일부 특수문자 허용(기존 로직 유지)
        updateRegisterBtnState();
    });
    // 닉네임 입력란(한글 입력 가능, 기존 한글제한 코드 제거)
    nicknameInput.addEventListener('input', function() {
        if (this.value.length > 10) {
            alert('닉네임은 최대 10자까지 입력 가능합니다.');
            this.value = this.value.slice(0, 10);
        }
        checkNicknameBtn.disabled = false;
        nicknameChecked = false;
        updateRegisterBtnState();
    });

    // 휴대폰번호 입력란 숫자만 입력 가능하도록 강제
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

    // 회원가입 버튼 활성화 제어
    function getSelectedGender() {
        const checked = document.querySelector('input[name="gender"]:checked');
        return checked ? checked.value : '';
    }

    function updateRegisterBtnState() {
        const allFilled = [
            userIdInput.value.trim(),
            nameInput.value.trim(),
            nicknameInput.value.trim(),
            pwInput.value.trim(),
            pwCheckInput.value.trim(),
            yearSelect.value,
            monthSelect.value,
            daySelect.value,
            getSelectedGender(),
            emailIdInput.value.trim(),
            emailDomain.value.trim(),
            document.getElementById('userPhone1').value.trim(),
            document.getElementById('userPhone2').value.trim(),
            document.getElementById('userPhone3').value.trim(),
            document.getElementById('userAddress').value.trim(),
            document.getElementById('userAddressDetail').value.trim()
        ].every(Boolean);
        const idValid = /^[a-z0-9]{6,15}$/.test(userIdInput.value);
        const nicknameValid = nicknameInput.value.length >= 2 && nicknameInput.value.length <= 10;
        const pwValid = isValidPassword(pwInput.value);
        const pwMatch = pwInput.value === pwCheckInput.value && pwInput.value.length > 0;
        const allChecked = userIdChecked && nicknameChecked && emailChecked && joinableChecked;
        document.getElementById('registerBtn').disabled = !(allFilled && idValid && nicknameValid && pwValid && pwMatch && allChecked);
    }
    // 모든 입력값에 대해 실시간으로 버튼 상태 갱신
    document.querySelectorAll('input, select').forEach(el => {
        el.addEventListener('input', updateRegisterBtnState);
        el.addEventListener('change', updateRegisterBtnState);
    });

    // 성별 라디오 버튼 변경 시에도 버튼 상태 갱신
    document.querySelectorAll('input[name="gender"]').forEach(el => {
        el.addEventListener('change', updateRegisterBtnState);
    });

    // 폼 제출 이벤트
    document.getElementById('registerForm').addEventListener('submit', function(e) {
        e.preventDefault();
        // 버튼들 모두 비활성화 확인
        if (!userIdChecked || !nicknameChecked || !emailChecked || !joinableChecked) {
            alert('중복확인/가입확인을 모두 완료해주세요.');
            return;
        }
        // 휴대폰번호 합치기
        const userPhone = [
            document.getElementById('userPhone1').value.trim(),
            document.getElementById('userPhone2').value.trim(),
            document.getElementById('userPhone3').value.trim()
        ].join('');
        // 생년월일 yyyy-MM-dd 형태로 합치기
        const userBirth = `${yearSelect.value}-${monthSelect.value}-${daySelect.value}`;
        // 이메일 합치기
        const userEmail = emailIdInput.value.trim() + '@' + emailDomain.value.trim();
        // 서버로 전송할 데이터
        const formData = {
            userName: nameInput.value.trim(),
            userNickname: nicknameInput.value.trim(),
            idForUser: userIdInput.value.trim(),
            userPwd: pwInput.value.trim(),
            userBirth,
            userEmail,
            userPhoneNumber: userPhone,
            userAddress: document.getElementById('userAddress').value.trim(),
            userAddressDetail: document.getElementById('userAddressDetail').value.trim(),
            userGender: getSelectedGender()
        };
        
        // 회원가입 API 호출
        fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                // 세션에서 referer 정보 확인
                const referer = sessionStorage.getItem('registerReferer');
                if (referer && referer.includes('/login')) {
                    // 로그인 페이지에서 온 경우 로그인 페이지로 리다이렉트
                    window.location.href = '/login';
                } else if (referer) {
                    // 다른 페이지에서 온 경우 원래 페이지로 리다이렉트
                    window.location.href = referer;
                } else {
                    // 기본적으로 로그인 페이지로 리다이렉트
                    window.location.href = '/login';
                }
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('회원가입 오류:', error);
            alert('회원가입 중 오류가 발생했습니다.');
        });
    });

    // 폼 제출 시 모든 텍스트/이메일/비밀번호 입력값 앞뒤 공백 trim
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            registerForm.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]').forEach(function(input) {
                input.value = input.value.trim();
            });
        });
    }

    // 비밀번호 입력 시 한글 입력 방지 및 특수문자 제한
    function removeKorean(str) {
        return str.replace(/[ㄱ-ㅎㅏ-ㅣ가-힣]/g, '');
    }
    function removeInvalidPwChars(str) {
        // 영문(대/소), 숫자, 특수문자(~!@#$%^&*()-_=+[{]};:'",<.>/?\|)만 허용
        return str.replace(/[^a-zA-Z0-9~!@#$%^&*()\-_=+\[\]{};:'\",<.>/?\\|]/g, '');
    }
    function isValidPassword(pw) {
        // 6~20자, 2종류 이상 조합(영문, 숫자, 특수문자)
        if (pw.length < 6 || pw.length > 20) return false;
        const hasAlpha = /[a-zA-Z]/.test(pw);
        const hasNum = /[0-9]/.test(pw);
        const hasSpecial = /[~!@#$%^&*()\-_=+\[\]{};:'\",<.>/?\\|]/.test(pw);
        return (hasAlpha + hasNum + hasSpecial) >= 2;
    }
});
