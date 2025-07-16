// 제목 길이에 따른 폰트 크기 자동 조절
document.addEventListener('DOMContentLoaded', function() {
    const title = document.querySelector('.product-info h2');
    if (!title) return;
    
    const titleText = title.textContent.trim();
    const titleLength = titleText.length;
    
    // 제목 길이에 따른 폰트 크기 조절
    if (titleLength > 80) {
        title.style.fontSize = '0.9rem';
        title.style.lineHeight = '1.1';
    } else if (titleLength > 60) {
        title.style.fontSize = '1.1rem';
        title.style.lineHeight = '1.2';
    } else if (titleLength > 40) {
        title.style.fontSize = '1.3rem';
        title.style.lineHeight = '1.25';
    } else if (titleLength > 25) {
        title.style.fontSize = '1.5rem';
        title.style.lineHeight = '1.3';
    } else {
        title.style.fontSize = '1.8rem';
        title.style.lineHeight = '1.3';
    }
});