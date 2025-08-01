document.addEventListener('DOMContentLoaded', function() {
    console.log('헤더 JavaScript 로드 완료');

    // DOM 요소들 선택
    const elements = {
        menuToggle: document.getElementById('menuToggle'),
        menuDropdown: document.getElementById('menuDropdown'),
        menuCloseBtn: document.getElementById('menuCloseBtn'),
        detailedSearchToggle: document.getElementById('detailedSearchToggle'),
        detailedSearchDropdown: document.getElementById('detailedSearchDropdown'),
        rollingText: document.getElementById('rollingText'),
        searchBtn: document.getElementById('searchBtn'),
        searchInput: document.getElementById('searchInput'),
        detailedSearchBtn: document.querySelector('.detailed-search-btn'),
        topButton: document.getElementById('topButton'),
        clearRecentBtn: document.getElementById('clearRecentBtn'),
        // 챗봇 요소들
        chatbotToggle: document.getElementById('chatbotToggle'),
        chatbotWindow: document.getElementById('chatbotWindow'),
        chatbotClose: document.getElementById('chatbotClose'),
        chatbotInput: document.getElementById('chatbotInput'),
        chatbotSend: document.getElementById('chatbotSend'),
        chatbotMessages: document.getElementById('chatbotMessages'),
        chatbotNewChat: document.getElementById('chatbotNewChat')
    };

    // 카테고리 토글 이벤트 리스너 추가 (교보문고 스타일)
    function addCategoryEventListeners() {
        console.log('카테고리 이벤트 리스너 추가 시작');

        // 대분류 버튼 클릭 이벤트
        document.querySelectorAll('.top-category-button').forEach(button => {
            button.addEventListener('click', function() {
                const categoryId = this.dataset.categoryId;
                console.log(`대분류 클릭: ${categoryId}`);

                // 기존 활성화된 대분류 버튼 비활성화
                document.querySelectorAll('.top-category-button.active').forEach(btn => {
                    btn.classList.remove('active');
                });

                // 현재 클릭된 대분류 버튼 활성화
                this.classList.add('active');

                // 기존 활성화된 중분류/소분류 콘텐츠 숨기기
                document.querySelectorAll('.sub-category-content.active').forEach(content => {
                    content.classList.remove('active');
                });

                // 기본 메시지 숨기기
                const defaultMessage = document.querySelector('.default-message');
                if (defaultMessage) {
                    defaultMessage.style.display = 'none';
                }

                // 해당 대분류의 중분류/소분류 콘텐츠 표시
                const subContent = document.getElementById(`sub-${categoryId}`);
                if (subContent) {
                    subContent.classList.add('active');

                    // 해당 대분류 내의 모든 중분류 소분류 초기화
                    subContent.querySelectorAll('.middle-category-button.active').forEach(btn => {
                        btn.classList.remove('active');
                    });
                    subContent.querySelectorAll('.low-category-list.active').forEach(list => {
                        list.classList.remove('active');
                    });
                }
            });
        });

        // 중분류 버튼 클릭 이벤트
        document.querySelectorAll('.middle-category-button').forEach(button => {
            button.addEventListener('click', function() {
                const categoryId = this.dataset.categoryId;
                const parentId = this.dataset.parent;
                console.log(`중분류 클릭: ${categoryId}, 부모: ${parentId}`);

                // 같은 대분류 내의 다른 중분류들 비활성화
                const parentContent = document.getElementById(`sub-${parentId}`);
                if (parentContent) {
                    parentContent.querySelectorAll('.middle-category-button.active').forEach(btn => {
                        if (btn !== this) {
                            btn.classList.remove('active');
                        }
                    });
                    parentContent.querySelectorAll('.low-category-list.active').forEach(list => {
                        const listCategoryId = list.id.replace('low-', '');
                        if (listCategoryId !== categoryId) {
                            list.classList.remove('active');
                        }
                    });
                }

                // 현재 중분류 토글
                const isActive = this.classList.contains('active');
                const lowCategoryList = document.getElementById(`low-${categoryId}`);

                if (isActive) {
                    // 비활성화
                    this.classList.remove('active');
                    if (lowCategoryList) {
                        lowCategoryList.classList.remove('active');
                    }
                } else {
                    // 활성화
                    this.classList.add('active');
                    if (lowCategoryList) {
                        lowCategoryList.classList.add('active');
                    }
                }
            });
        });

        // 소분류 클릭 이벤트
        document.querySelectorAll('.low-category-item').forEach(item => {
            item.addEventListener('click', function() {
                const categoryId = this.dataset.categoryId;
                const categoryName = this.textContent.trim();
                console.log(`소분류 선택: ${categoryName} (ID: ${categoryId})`);

                // 메뉴 닫기
                closeMenu();

                // 소분류 페이지로 이동
                window.location.href = `/product/category/low/${categoryId}`;
            });
        });

        console.log('카테고리 이벤트 리스너 추가 완료');
    }

    // 햄버거 메뉴 토글 기능
    if (elements.menuToggle && elements.menuDropdown) {
        elements.menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleMenu();
        });
    }

    // 메뉴 닫기 버튼 기능
    if (elements.menuCloseBtn && elements.menuDropdown) {
        elements.menuCloseBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            closeMenu();
        });
    }

    // 상세검색 토글
    if (elements.detailedSearchToggle && elements.detailedSearchDropdown) {
        elements.detailedSearchToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleDetailedSearch();
        });
    }

    // TOP 버튼 기능
    if (elements.topButton) {
        elements.topButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // 검색 기능
    if (elements.searchBtn && elements.searchInput) {
        elements.searchBtn.addEventListener('click', performSearch);
        elements.searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch();
            }
        });
    }

    // 상세검색 기능
    if (elements.detailedSearchBtn) {
        elements.detailedSearchBtn.addEventListener('click', performDetailedSearch);
    }

    // 최근 조회 목록 삭제 기능
    if (elements.clearRecentBtn) {
        elements.clearRecentBtn.addEventListener('click', function() {
            if (confirm('최근 조회한 책 목록을 모두 삭제하시겠습니까?')) {
                clearRecentBooks();
            }
        });
    }

    // 로그인이 필요한 기능 처리
    const needLoginElements = document.querySelectorAll('.need-login');
    needLoginElements.forEach(element => {
        element.addEventListener('click', handleNeedLogin);
    });

    // 외부 클릭시 드롭다운 닫기
    document.addEventListener('click', function(e) {
        const isDropdownButton = e.target.closest('.detailed-search-toggle') ||
            e.target.closest('.menu-toggle');
        const isDropdownContent = e.target.closest('.detailed-search-dropdown') ||
            e.target.closest('.menu-dropdown-content') ||
            e.target.closest('.popular-search-detail');

        if (!isDropdownButton && !isDropdownContent) {
            closeAllDropdowns();
        }
    });

    // 키보드 접근성 지원
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllDropdowns();
        }
    });

    // 인기검색어 클릭 이벤트
    document.addEventListener('click', function(e) {
        if (e.target.closest('.popular-search-list li')) {
            const keyword = e.target.textContent.trim();
            searchKeyword(keyword);
        }
    });

    // 함수 정의들
    function toggleMenu() {
        const isActive = elements.menuToggle.classList.contains('active');
        closeAllDropdowns();

        if (!isActive) {
            elements.menuToggle.classList.add('active');
            elements.menuDropdown.classList.add('active');
            elements.menuToggle.setAttribute('aria-expanded', 'true');

            // 메뉴 열릴 때 초기화
            resetMenuState();
        } else {
            closeMenu();
        }
    }

    function closeMenu() {
        if (elements.menuToggle && elements.menuDropdown) {
            elements.menuToggle.classList.remove('active');
            elements.menuDropdown.classList.remove('active');
            elements.menuToggle.setAttribute('aria-expanded', 'false');
        }
    }

    function resetMenuState() {
        // 모든 대분류 버튼 비활성화
        document.querySelectorAll('.top-category-button.active').forEach(btn => {
            btn.classList.remove('active');
        });

        // 모든 중분류/소분류 콘텐츠 숨기기
        document.querySelectorAll('.sub-category-content.active').forEach(content => {
            content.classList.remove('active');
        });

        // 모든 중분류 버튼 비활성화
        document.querySelectorAll('.middle-category-button.active').forEach(btn => {
            btn.classList.remove('active');
        });

        // 모든 소분류 목록 숨기기
        document.querySelectorAll('.low-category-list.active').forEach(list => {
            list.classList.remove('active');
        });

        // 기본 메시지 표시
        const defaultMessage = document.querySelector('.default-message');
        if (defaultMessage) {
            defaultMessage.style.display = 'block';
        }
    }

    function toggleDetailedSearch() {
        const isActive = elements.detailedSearchToggle.classList.contains('active');

        if (!isActive) {
            elements.detailedSearchToggle.classList.add('active');
            elements.detailedSearchDropdown.classList.add('active');
        } else {
            elements.detailedSearchToggle.classList.remove('active');
            elements.detailedSearchDropdown.classList.remove('active');
        }
    }

    function closeAllDropdowns() {
        // 상세검색 드롭다운 닫기
        if (elements.detailedSearchDropdown && elements.detailedSearchToggle) {
            elements.detailedSearchDropdown.classList.remove('active');
            elements.detailedSearchToggle.classList.remove('active');
        }

        // 메뉴 드롭다운 닫기
        closeMenu();
    }

    function performSearch() {
        const keyword = elements.searchInput.value.trim();
        if (keyword) {
            window.location.href = `/product/search?q=${encodeURIComponent(keyword)}`;
        } else {
            alert('검색어를 입력해주세요.');
        }
    }

    function performDetailedSearch() {
        const title = document.getElementById('bookTitle').value.trim();
        const publisher = document.getElementById('publisher').value.trim();
        const author = document.getElementById('author').value.trim();

        if (!title && !publisher && !author) {
            alert('검색 조건을 하나 이상 입력해주세요.');
            return;
        }

        const params = new URLSearchParams();
        if (title) params.append('title', title);
        if (publisher) params.append('publisher', publisher);
        if (author) params.append('author', author);

        window.location.href = `/search/detailed?${params.toString()}`;
    }

    function handleNeedLogin(e) {
        e.preventDefault();
        alert('로그인이 필요한 기능입니다. 로그인 후 이용해 주세요.');
        window.location.href = '/login?redirectUrl=' + encodeURIComponent(window.location.pathname + window.location.search);
    }

    function searchKeyword(keyword) {
        if (elements.searchInput) {
            elements.searchInput.value = keyword;
        }
        window.location.href = `/search?keyword=${encodeURIComponent(keyword)}`;
    }

    let popularSearchItems = [];
    let currentIndex = 0;
    let rollingInterval;
    let baseTime = '';

    async function fetchPopularKeywords() {
        try {
            const res = await fetch('/api/popular-keywords');
            const data = await res.json();
            popularSearchItems = data.keywords.map(item => item.productName);
            baseTime = data.baseTime;
            renderPopularSearchList(data.keywords);
            renderPopularSearchTime(data.baseTime);
            currentIndex = 0;
            startRolling();
        } catch (e) {
            // 에러 처리
        }
    }

    function renderPopularSearchList(keywords) {
        const list = document.querySelector('.popular-search-list');
        if (list) {
            list.innerHTML = keywords.map((item, idx) =>
                `<li data-rank="${idx+1}" data-isbn="${item.isbn}">${item.productName}</li>`
            ).join('');
            // 기존 이벤트 제거 후 새로 바인딩
            list.querySelectorAll('li').forEach(li => {
                li.onclick = null; // 기존 onclick 제거
                li.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    const isbn = this.getAttribute('data-isbn');
                    if (isbn) {
                        window.location.href = `/product/detail?isbn=${isbn}`;
                    }
                });
            });
        }
    }

    function renderPopularSearchTime(time) {
        const timeDiv = document.getElementById('popular-keyword-time');
        if (timeDiv) {
            timeDiv.textContent = `${time} 기준`;
        }
    }

    function updateRollingText() {
        if (!elements.rollingText || popularSearchItems.length === 0) return;
        const currentSpan = elements.rollingText.querySelector('span');
        if (currentSpan) {
            currentSpan.classList.add('slide-out');
            setTimeout(() => {
                currentIndex = (currentIndex + 1) % popularSearchItems.length;
                elements.rollingText.innerHTML = `<span class="slide-in active">${popularSearchItems[currentIndex]}</span>`;
                setTimeout(() => {
                    const newSpan = elements.rollingText.querySelector('span');
                    if (newSpan) {
                        newSpan.classList.remove('slide-in');
                    }
                }, 50);
            }, 500);
        } else {
            elements.rollingText.innerHTML = `<span>${popularSearchItems[currentIndex]}</span>`;
        }
    }

    function startRolling() {
        if (elements.rollingText && popularSearchItems.length > 0) {
            elements.rollingText.innerHTML = `<span>${popularSearchItems[currentIndex]}</span>`;
        }
        if (rollingInterval) clearInterval(rollingInterval);
        rollingInterval = setInterval(updateRollingText, 3000);
    }

    function stopRolling() {
        if (rollingInterval) {
            clearInterval(rollingInterval);
        }
    }

    const popularSearchRolling = document.getElementById('popularSearchRolling');
    if (popularSearchRolling) {
        popularSearchRolling.addEventListener('mouseenter', stopRolling);
        popularSearchRolling.addEventListener('mouseleave', startRolling);
    }

    // 인기검색어 드롭다운 마우스 이벤트 추가
    const popularSearchDetail = document.getElementById('popularSearchDetail');
    if (popularSearchDetail) {
        let dropdownTimeout;
        
        // 롤링 영역에 마우스 진입
        popularSearchRolling.addEventListener('mouseenter', function() {
            stopRolling();
            clearTimeout(dropdownTimeout);
            popularSearchDetail.classList.add('show');
        });
        
        // 롤링 영역에서 마우스 나감
        popularSearchRolling.addEventListener('mouseleave', function(e) {
            // 드롭다운 영역으로 이동하는지 확인
            const relatedTarget = e.relatedTarget;
            if (!popularSearchDetail.contains(relatedTarget)) {
                dropdownTimeout = setTimeout(() => {
                    popularSearchDetail.classList.remove('show');
                    startRolling();
                }, 100);
            }
        });
        
        // 드롭다운 영역에 마우스 진입
        popularSearchDetail.addEventListener('mouseenter', function() {
            clearTimeout(dropdownTimeout);
            stopRolling();
        });
        
        // 드롭다운 영역에서 마우스 나감
        popularSearchDetail.addEventListener('mouseleave', function() {
            dropdownTimeout = setTimeout(() => {
                popularSearchDetail.classList.remove('show');
                startRolling();
            }, 100);
        });
    }

    // 최근 조회한 책 목록 관리
    function updateRecentBooksDisplay() {
        const recentBooksList = document.getElementById('recentBooksList');
        if (!recentBooksList) return;

        // 로그인한 유저만 표시
        const clearBtn = document.getElementById('clearRecentBtn');
        if (typeof window.isUserLoggedIn !== 'undefined' && !window.isUserLoggedIn) {
            recentBooksList.innerHTML = '<div style="text-align:center; color:#aaa; font-size:13px; padding:20px 5px;">로그인 후<br>최근 조회목록을<br>이용할 수 있습니다</div>';
            if (clearBtn) clearBtn.disabled = true;
            return;
        } else {
            if (clearBtn) clearBtn.disabled = false;
        }

        try {
            const userId = window.userId || 'guest';
            let recentBooks = JSON.parse(localStorage.getItem('recentBooks_' + userId) || '[]');
            // 중복 제거 (isbn 기준, 최신순)
            const seen = new Set();
            const uniqueBooks = [];
            for (const book of recentBooks) {
                if (!seen.has(book.isbn)) {
                    seen.add(book.isbn);
                    uniqueBooks.push(book);
                }
            }
            recentBooks = uniqueBooks;

            // recentBooksList 초기화
            recentBooksList.innerHTML = '';

            if (recentBooks.length === 0) {
                recentBooksList.innerHTML = '<div style="text-align: center; color: #999; font-size: 13px; padding: 20px 5px;">조회한 책이<br>없습니다</div>';
                // 높이 초기화
                recentBooksList.style.maxHeight = '';
                recentBooksList.style.overflowY = '';
                return;
            }

            // recentBooks 개수에 따라 높이/스크롤 동적 조정
            if (recentBooks.length <= 3) {
                recentBooksList.style.maxHeight = (recentBooks.length * 110) + 'px'; // 썸네일+여백 기준
                recentBooksList.style.overflowY = 'hidden';
            } else {
                recentBooksList.style.maxHeight = (3 * 110) + 'px';
                recentBooksList.style.overflowY = 'auto';
            }

            // 썸네일 누적 append, 가운데 정렬
            recentBooks.forEach(book => {
                const item = document.createElement('div');
                item.className = 'recent-book-item';
                item.title = book.title;
                item.style.display = 'flex';
                item.style.alignItems = 'center';
                item.style.justifyContent = 'center';
                item.style.gap = '8px';
                item.style.cursor = 'pointer';
                item.innerHTML = `<img src="${book.image || 'https://via.placeholder.com/70x96/e74c3c/ffffff?text=No+Image'}" alt="${book.title}" style="display:block;">`;
                item.onclick = function() { goToBook(book.isbn); };
                recentBooksList.appendChild(item);
            });
        } catch (error) {
            console.error('Error updating recent books display:', error);
            recentBooksList.innerHTML = '<div style="text-align: center; color: #999; font-size: 13px; padding: 20px 5px;">오류가<br>발생했습니다</div>';
            recentBooksList.style.maxHeight = '';
            recentBooksList.style.overflowY = '';
        }
    }

    function clearRecentBooks() {
        try {
            const userId = window.userId || 'guest';
            localStorage.removeItem('recentBooks_' + userId);
            updateRecentBooksDisplay();
        } catch (error) {
            console.error('Error clearing recent books:', error);
        }
    }

    function goToBook(isbn) {
        // 최근조회 추가 (userId별로 분리)
        const userId = window.userId || 'guest';
        let recentBooks = JSON.parse(localStorage.getItem('recentBooks_' + userId) || '[]');
        // 이미 있는 경우 삭제(최신순 유지)
        recentBooks = recentBooks.filter(book => book.isbn !== isbn);
        // 상품 정보 추출 (페이지에서 동적으로 가져오거나, 최소한 isbn만 저장)
        // 여기서는 최소한 isbn만 저장 (실제 구현에서는 title, image 등도 같이 저장 필요)
        recentBooks.unshift({ isbn: isbn });
        // 최대 10개까지만 저장
        if (recentBooks.length > 10) recentBooks = recentBooks.slice(0, 10);
        localStorage.setItem('recentBooks_' + userId, JSON.stringify(recentBooks));
        window.location.href = `/product/detail?isbn=${isbn}`;
    }

    // 로그아웃 버튼 이벤트 핸들러 추가
    function bindLogoutEvent() {
        const logoutBtn = document.querySelector('.user-logged-in .header-link[href="/logout"]');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const userId = window.userId || 'guest';
                // 로그아웃 시 해당 유저의 최근조회목록 삭제
                localStorage.removeItem('recentBooks_' + userId);
                fetch('/logout', { method: 'POST', credentials: 'same-origin' })
                    .then(res => {
                        if (res.ok) {
                            updateHeaderToLoggedOut();
                            // 플로팅바도 즉시 갱신
                            if (typeof window.updateRecentBooksDisplay === 'function') {
                                window.updateRecentBooksDisplay();
                            }
                        } else {
                            alert('로그아웃에 실패했습니다.');
                        }
                    });
            });
        }
    }
    bindLogoutEvent();

    // 상단바를 로그아웃 상태로 동적으로 변경하는 함수
    function updateHeaderToLoggedOut() {
        alert('로그아웃이 완료되었습니다.');
        const userMenu = document.querySelector('.user-menu');
        if (userMenu) {
            userMenu.innerHTML = `
                <div class="user-not-logged">
                    <a href="/login" class="header-link">로그인</a>
                    <a href="/register" class="header-link">회원가입</a>
                    <a href="#" class="header-link need-login">장바구니</a>
                    <a href="#" class="header-link need-login">마이페이지</a>
                </div>
            `;
            // need-login 이벤트 재등록
            userMenu.querySelectorAll('.need-login').forEach(element => {
                element.addEventListener('click', handleNeedLogin);
            });
        }
        // 로그아웃 시 새로고침
        window.location.reload();
    }

    // 카테고리별 책 개수 표시 기능 추가
    async function fetchAndDisplayCategoryCounts() {
        // 전체 상품 개수
        const totalRes = await fetch('/api/total-product-count');
        const totalCount = await totalRes.json();
        const allProductsBtn = document.querySelector('.all-products-btn');
        if (allProductsBtn && totalCount > 0) {
            allProductsBtn.innerHTML = `전체 상품 <span style='color:#888;font-size:0.9em;'>(${totalCount})</span>`;
        }
        
        // 대분류
        const topRes = await fetch('/api/category/top-count');
        const topCounts = await topRes.json();
        topCounts.forEach(item => {
            const btn = document.querySelector(`.top-category-button[data-category-id='${item.topCategory}']`);
            if (btn) {
                btn.innerHTML = `${item.topCategoryName} <span style='color:#888;font-size:0.9em;'>(${item.bookCount})</span>`;
            }
        });
        // 중분류
        const midRes = await fetch('/api/category/middle-count');
        const midCounts = await midRes.json();
        midCounts.forEach(item => {
            const btn = document.querySelector(`.middle-category-button[data-category-id='${item.midCategory}']`);
            if (btn) {
                const categoryNameSpan = btn.querySelector('span');
                if (categoryNameSpan) {
                    categoryNameSpan.innerHTML = `${item.midCategoryName} <span style='color:#999;font-size:12px;'>(${item.bookCount})</span>`;
                } else {
                    btn.innerHTML = `<span>${item.midCategoryName} <span style='color:#999;font-size:12px;'>(${item.bookCount})</span></span>`;
                }
            }
        });
        // 소분류
        const lowRes = await fetch('/api/category/low-count');
        const lowCounts = await lowRes.json();
        lowCounts.forEach(item => {
            const div = document.querySelector(`.low-category-item[data-category-id='${item.lowCategory}']`);
            if (div) {
                div.innerHTML = `${item.lowCategoryName} <span style='color:#888;font-size:0.9em;'>(${item.bookCount})</span>`;
            }
        });
    }

    // 초기화
    addCategoryEventListeners(); // 교보문고 스타일 카테고리 이벤트 추가
    fetchPopularKeywords();
    updateRecentBooksDisplay();
    fetchAndDisplayCategoryCounts();

    // 전역 함수 등록
    window.goToBook = goToBook;
    window.searchKeyword = searchKeyword;
    window.updateRecentBooksDisplay = updateRecentBooksDisplay;

    function isForceMainPage() {
        const path = window.location.pathname;
        return (
            path.startsWith('/cart') ||
            path.startsWith('/order') ||
            path.startsWith('/summary') ||
            path.startsWith('/mypage')
        );
    }

    // 로그아웃 버튼 클릭 시 main으로 이동
    document.body.addEventListener('click', function(e) {
        const target = e.target;
        if (target.matches('.user-logged-in .header-link') && target.textContent.includes('로그아웃')) {
            e.preventDefault();
            fetch('/logout', { method: 'POST' })
                .then(() => {
                    if (isForceMainPage()) {
                        window.location.href = '/main';
                    } else {
                        window.location.reload();
                    }
                });
        }
    });

    // 관리자 접근 제한 로직
    function setupAdminRestrictions() {
        if (window.isAdmin) {
            console.log('관리자 계정: 일반 사용자 메뉴 제한 적용');
            
            // 장바구니 링크 차단
            const cartLink = document.getElementById('headerCartLink');
            if (cartLink) {
                cartLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    alert('일반 사용자 전용 화면입니다.');
                });
                // 시각적으로 비활성화 표시
                cartLink.style.opacity = '0.5';
                cartLink.style.cursor = 'not-allowed';
            }
            
            // 마이페이지 링크 차단
            const mypageLink = document.getElementById('headerMypageLink');
            if (mypageLink) {
                mypageLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    alert('일반 사용자 전용 화면입니다.');
                });
                // 시각적으로 비활성화 표시
                mypageLink.style.opacity = '0.5';
                mypageLink.style.cursor = 'not-allowed';
            }
        }
    }
    
    // 관리자 제한 설정 적용
    setupAdminRestrictions();
    
    // AI 챗봇 기능 초기화
    initializeChatbot();

    console.log('헤더 초기화 완료');
    
    // AI 챗봇 기능
    function initializeChatbot() {
        console.log('챗봇 초기화 시작');
        
        // 세션 ID를 함수 내부에서 관리
        let sessionId = localStorage.getItem('ai_session_id');
        console.log('초기 세션 ID:', sessionId);
        
        // 페이지 로드 시 이전 채팅 기록 복원
        restoreChatHistory();
        
        // 챗봇 토글 버튼 클릭 이벤트
        if (elements.chatbotToggle) {
            elements.chatbotToggle.addEventListener('click', function() {
                console.log('챗봇 토글 클릭');
                const isActive = elements.chatbotWindow.classList.toggle('active');
                
                // 챗봇 창이 열릴 때 스크롤을 맨 아래로 이동
                if (isActive) {
                    elements.chatbotMessages.scrollTop = elements.chatbotMessages.scrollHeight;
                }
            });
        }
        
        // 챗봇 닫기 버튼 클릭 이벤트
        if (elements.chatbotClose) {
            elements.chatbotClose.addEventListener('click', function() {
                console.log('챗봇 닫기 클릭');
                elements.chatbotWindow.classList.remove('active');
            });
        }
        
        // 제안 버튼 클릭 이벤트
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('suggestion-btn')) {
                const text = e.target.getAttribute('data-text');
                if (text && elements.chatbotInput) {
                    elements.chatbotInput.value = text;
                    sendMessage();
                }
            }
        });
        
        // 메시지 전송 버튼 클릭 이벤트
        if (elements.chatbotSend) {
            elements.chatbotSend.addEventListener('click', sendMessage);
        }
        
        // 입력창 엔터 키 이벤트
        if (elements.chatbotInput) {
            elements.chatbotInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        }

        // 새 대화 시작 버튼 이벤트
        if (elements.chatbotNewChat) {
            elements.chatbotNewChat.addEventListener('click', startNewChat);
        }
        
        // 새 대화 시작 함수
        function startNewChat() {
            if (confirm('대화 기록을 모두 지우고 새 대화를 시작할까요?')) {
                console.log('새 대화 시작...');
                
                // 로컬 스토리지에서 현재 세션 기록 삭제
                if (sessionId) {
                    localStorage.removeItem(`chat_history_${sessionId}`);
                }
                // 세션 ID 자체도 삭제
                localStorage.removeItem('ai_session_id');
                
                // 내부 변수 초기화
                sessionId = null;
                
                // 화면의 메시지 초기화
                elements.chatbotMessages.innerHTML = `
                    <div class="bot-message">안녕하세요! 책크인 AI 서비스입니다.<br>어떤 서비스를 찾고 계신가요?
                        <div class="message-suggestions">
                            <button class="suggestion-btn" data-text="작가 한강 정보 알려줘">🕵️ 위키서비스</button>
                            <button class="suggestion-btn" data-text="우울한데 위로가 되는 책 추천해줘">😌 힐링 도서</button>
                            <button class="suggestion-btn" data-text="자기계발서 추천해줘">💪 자기계발</button>
                        </div>
                    </div>
                `;
                
                console.log('대화 기록 및 세션이 초기화되었습니다.');
            }
        }
        
        // 메시지 전송 함수
        async function sendMessage() {
            const message = elements.chatbotInput.value.trim();
            if (!message) return;

            // ★ FIX: 세션 ID를 메시지 추가 전에 확인 및 생성
            if (!sessionId) {
                sessionId = 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
                localStorage.setItem('ai_session_id', sessionId);
                console.log('새 세션 ID 생성:', sessionId);
            }
            
            // 사용자 메시지 추가 (이제 sessionId가 항상 존재)
            addMessage(message, 'user');
            
            // 입력창 비우기
            elements.chatbotInput.value = '';
            
            // 로딩 메시지 표시
            const loadingDiv = addLoadingMessage();
            
            try {
                // 실제 AI 채팅 API 호출
                const headers = {
                    'Content-Type': 'application/json',
                    'X-Session-ID': sessionId
                };
                
                const response = await fetch('http://localhost:8000/api/chat', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({ message: message })
                });

                const data = await response.json();
                
                // 로딩 메시지 제거
                loadingDiv.remove();
                
                if (data.response) {
                    addMessage(data.response, 'bot');
                } else {
                    addMessage(data.error || 'AI 서비스에서 오류가 발생했습니다.', 'bot');
                }
                
            } catch (error) {
                console.error('AI 채팅 오류:', error);
                loadingDiv.remove();
                addMessage('네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.', 'bot');
            }
        }
        
        // 채팅 기록 복원 함수
        function restoreChatHistory() {
            if (!sessionId) return;
            
            const chatHistory = localStorage.getItem(`chat_history_${sessionId}`);
            if (chatHistory) {
                try {
                    const messages = JSON.parse(chatHistory);
            
            // 기존 메시지 제거 (환영 메시지 제외)
            const messagesContainer = elements.chatbotMessages;
            while (messagesContainer.children.length > 1) {
                messagesContainer.removeChild(messagesContainer.lastChild);
            }
            
            // 저장된 메시지들 복원
            messages.forEach(message => {
                addMessage(message.text, message.type, false); // 저장하지 않고 추가
            });
                    
                    console.log(`${messages.length}개의 이전 메시지를 복원했습니다.`);
                } catch (error) {
                    console.error('채팅 기록 복원 오류:', error);
                }
            }
        }
        
        // 채팅 기록 저장 함수
        function saveChatHistory(text, type) {
            if (!sessionId) return;
            
            try {
                const chatHistory = localStorage.getItem(`chat_history_${sessionId}`);
                let messages = chatHistory ? JSON.parse(chatHistory) : [];
                
                messages.push({ text, type, timestamp: Date.now() });
                
                // 최대 50개 메시지만 저장 (메모리 절약)
                if (messages.length > 50) {
                    messages = messages.slice(-50);
                }
                
                localStorage.setItem(`chat_history_${sessionId}`, JSON.stringify(messages));
            } catch (error) {
                console.error('채팅 기록 저장 오류:', error);
            }
        }

        // 메시지 추가 함수 (수정됨)
        function addMessage(text, type, shouldSave = true) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `${type}-message`;
            
            // 텍스트 처리: 줄바꿈과 링크를 HTML로 변환
            let processedText = text;
            
            // 줄바꿈 처리 (\n을 <br>로 변환)
            processedText = processedText.replace(/\n/g, '<br>');
            
            // URL을 클릭 가능한 링크로 변환 (단어 경계와 긴 URL 처리)
            processedText = processedText.replace(
                /(https?:\/\/[^\s<>"']+)/g, 
                '<a href="$1" target="_blank" rel="noopener noreferrer" class="chatbot-link">링크 보기</a>'
            );
            
            // **볼드** 텍스트 처리
            processedText = processedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            
            messageDiv.innerHTML = processedText;
            
            elements.chatbotMessages.appendChild(messageDiv);
            elements.chatbotMessages.scrollTop = elements.chatbotMessages.scrollHeight;
            
            // 채팅 기록 저장 (shouldSave가 true일 때만)
            if (shouldSave) {
                saveChatHistory(text, type);
            }
            
            return messageDiv;
        }
        
        // 로딩 메시지 추가 함수
        function addLoadingMessage() {
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'loading-message';
            loadingDiv.textContent = '🤔 생각 중...';
            
            elements.chatbotMessages.appendChild(loadingDiv);
            elements.chatbotMessages.scrollTop = elements.chatbotMessages.scrollHeight;
            
            return loadingDiv;
        }

        console.log('챗봇 초기화 완료');
    }
});