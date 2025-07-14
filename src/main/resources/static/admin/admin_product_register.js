// admin_product_register.js

document.addEventListener('DOMContentLoaded', function() {
    // --- 카테고리 셀렉트 연동 ---
    const topCategory = document.getElementById('topCategory');
    const middleCategory = document.getElementById('middleCategory');
    const lowCategory = document.getElementById('lowCategory');

    // 대분류 불러오기
    fetch('/api/category/top')
        .then(res => res.json())
        .then(data => {
            data.forEach(cat => {
                const opt = document.createElement('option');
                opt.value = cat.topCategory;
                opt.textContent = cat.topCategoryName;
                topCategory.appendChild(opt);
            });
        });

    // 대분류 선택 시 중분류 불러오기
    topCategory.addEventListener('change', function() {
        middleCategory.innerHTML = '<option value="">중분류 선택</option>';
        lowCategory.innerHTML = '<option value="">소분류 선택</option>';
        middleCategory.disabled = true;
        lowCategory.disabled = true;
        if (!this.value) return;
        fetch(`/api/category/middle?topCategory=${this.value}`)
            .then(res => res.json())
            .then(data => {
                data.forEach(cat => {
                    const opt = document.createElement('option');
                    opt.value = cat.midCategory;
                    opt.textContent = cat.midCategoryName;
                    middleCategory.appendChild(opt);
                });
                middleCategory.disabled = false;
            });
    });

    // 중분류 선택 시 소분류 불러오기
    middleCategory.addEventListener('change', function() {
        lowCategory.innerHTML = '<option value="">소분류 선택</option>';
        lowCategory.disabled = true;
        if (!this.value) return;
        fetch(`/api/category/low?midCategory=${this.value}`)
            .then(res => res.json())
            .then(data => {
                data.forEach(cat => {
                    const opt = document.createElement('option');
                    opt.value = cat.lowCategory;
                    opt.textContent = cat.lowCategoryName;
                    lowCategory.appendChild(opt);
                });
                lowCategory.disabled = false;
            });
    });

    // --- 숫자 입력 제한 ---
    function onlyNumberInput(e) {
        // 허용: 숫자, 백스페이스, 딜리트, 방향키
        if (!/^[0-9]*$/.test(e.target.value)) {
            e.target.value = e.target.value.replace(/[^0-9]/g, '');
        }
    }
    function onlyDecimalInput(e) {
        // 허용: 숫자, 소수점 1개
        e.target.value = e.target.value.replace(/[^0-9.]/g, '');
        const parts = e.target.value.split('.');
        if (parts.length > 2) {
            e.target.value = parts[0] + '.' + parts.slice(1).join('');
        }
    }
    document.getElementById('isbn').addEventListener('input', onlyNumberInput);
    document.getElementById('price').addEventListener('input', onlyNumberInput);
    document.getElementById('width').addEventListener('input', onlyNumberInput);
    document.getElementById('height').addEventListener('input', onlyNumberInput);
    document.getElementById('page').addEventListener('input', onlyNumberInput);
    document.getElementById('rate').addEventListener('input', onlyDecimalInput);

    // --- textarea UX 개선: 스크롤 항상 표시 ---
    document.getElementById('briefDescription').style.overflowY = 'auto';
    document.getElementById('detailDescription').style.overflowY = 'auto';

    // --- 등록버튼 활성화 조건 ---
    const requiredFields = [
        'isbn', 'title', 'author', 'publisher', 'price', 'rate', 'img',
        'width', 'height', 'page', 'salesStatus', 'regDate', 'lowCategory'
    ];
    const registerBtn = document.getElementById('registerBtn');
    const form = document.getElementById('productRegisterForm');
    function checkFormValid() {
        let valid = true;
        for (const id of requiredFields) {
            const el = document.getElementById(id);
            if (!el || el.disabled || !el.value) {
                valid = false;
                break;
            }
        }
        // ISBN 중복확인 통과 여부(추후 구현)
        if (!window.isIsbnChecked) valid = false;
        registerBtn.disabled = !valid;
    }
    form.addEventListener('input', checkFormValid);
    form.addEventListener('change', checkFormValid);

    const duplicateCheckBtn = document.getElementById('duplicateCheckBtn');
    const isbnInput = document.getElementById('isbn');

    // --- ISBN 중복확인 (예시, 실제 API 필요) ---
    window.isIsbnChecked = false;
    duplicateCheckBtn.addEventListener('click', function() {
        const isbn = isbnInput.value.trim();
        if (!isbn) {
            alert('ISBN을 입력하세요.');
            return;
        }
        console.log('ISBN 중복확인 요청:', isbn);
        fetch(`/admin/api/product/check-isbn?isbn=${isbn}`)
            .then(res => {
                console.log('응답 상태:', res.status);
                if (!res.ok) {
                    throw new Error(`HTTP error! status: ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                console.log('응답 데이터:', data);
                if (data.duplicated) {
                    alert('이미 등록된 ISBN입니다.');
                    window.isIsbnChecked = false;
                    duplicateCheckBtn.disabled = false;
                } else {
                    alert('등록 가능한 ISBN입니다.');
                    window.isIsbnChecked = true;
                    duplicateCheckBtn.disabled = true;
                }
                checkFormValid();
            })
            .catch(error => {
                console.error('중복확인 오류:', error);
                alert('중복확인 중 오류 발생: ' + error.message);
                window.isIsbnChecked = false;
                duplicateCheckBtn.disabled = false;
                checkFormValid();
            });
    });
    // ISBN 입력값이 바뀌면 중복확인 다시 가능
    isbnInput.addEventListener('input', function() {
        window.isIsbnChecked = false;
        duplicateCheckBtn.disabled = false;
        checkFormValid();
    });

    // 상품등록 폼 제출 처리
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!window.isIsbnChecked) {
            alert('ISBN 중복확인을 먼저 해주세요.');
            return;
        }

        // 폼 데이터 수집
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        console.log('상품등록 데이터:', data);

        // 등록 버튼 비활성화
        registerBtn.disabled = true;
        registerBtn.textContent = '등록 중...';

        // API 요청
        fetch('/admin/api/product/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(res => {
            console.log('응답 상태:', res.status);
            return res.json();
        })
        .then(data => {
            console.log('응답 데이터:', data);
            if (data.success) {
                alert(data.message || '상품이 성공적으로 등록되었습니다.');
                // 폼 초기화
                form.reset();
                window.isIsbnChecked = false;
                duplicateCheckBtn.disabled = false;
                middleCategory.disabled = true;
                lowCategory.disabled = true;
                checkFormValid();
            } else {
                alert('등록 실패: ' + (data.message || '알 수 없는 오류가 발생했습니다.'));
            }
        })
        .catch(error => {
            console.error('등록 오류:', error);
            alert('등록 중 오류가 발생했습니다: ' + error.message);
        })
        .finally(() => {
            // 등록 버튼 재활성화
            registerBtn.disabled = false;
            registerBtn.textContent = '등록';
            checkFormValid();
        });
    });
});
