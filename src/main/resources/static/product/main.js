// 탭 클릭 이벤트 및 데이터 로딩
const bestsellerTabs = document.querySelectorAll('.bestseller-tab');
const bestsellerList = document.getElementById('bestseller-list');
const newProductList = document.getElementById('newproduct-list');

// 베스트셀러 데이터 로딩 함수
defaultBestsellerType = 'weekly';

function getRankDisplay(idx) {
    return `No.${idx + 1}`;
}

async function loadBestseller(type = defaultBestsellerType) {
    bestsellerList.innerHTML = '<div class="loading">로딩중...</div>';
    try {
        const res = await fetch(`/api/bestseller?type=${type}`);
        const data = await res.json();
        bestsellerList.innerHTML = '';
        data.slice(0, 5).forEach((item, idx) => {
            bestsellerList.innerHTML += `
                <div class="product-item">
                    <span class="product-rank">${getRankDisplay(idx)}</span>
                    <a href="/product/detail?isbn=${item.isbn}">
                        <img src="${item.img}" alt="${item.productName}" class="product-img" />
                    </a>
                    <a href="/product/detail?isbn=${item.isbn}" class="product-title">${item.productName}</a>
                    <div class="product-author">${item.author}</div>
                </div>
            `;
        });
    } catch (e) {
        bestsellerList.innerHTML = '<div class="error">데이터를 불러오지 못했습니다.</div>';
    }
}

// 신상품 데이터 로딩 함수
async function loadNewProducts() {
    newProductList.innerHTML = '<div class="loading">로딩중...</div>';
    try {
        const res = await fetch('/api/newproducts');
        const data = await res.json();
        newProductList.innerHTML = '';
        data.slice(0, 5).forEach((item, idx) => {
            newProductList.innerHTML += `
                <div class="product-item">
                    <span class="product-rank">${getRankDisplay(idx)}</span>
                    <a href="/product/detail?isbn=${item.isbn}">
                        <img src="${item.img}" alt="${item.productName}" class="product-img" />
                    </a>
                    <a href="/product/detail?isbn=${item.isbn}" class="product-title">${item.productName}</a>
                    <div class="product-author">${item.author}</div>
                </div>
            `;
        });
    } catch (e) {
        newProductList.innerHTML = '<div class="error">데이터를 불러오지 못했습니다.</div>';
    }
}

// 탭 클릭 이벤트 바인딩 (span용으로 수정)
bestsellerTabs.forEach(tab => {
    tab.addEventListener('click', function() {
        bestsellerTabs.forEach(t => t.classList.remove('active'));
        this.classList.add('active');
        loadBestseller(this.dataset.type);
    });
});

// 최초 로딩
window.addEventListener('DOMContentLoaded', () => {
    loadBestseller();
    loadNewProducts();
});
