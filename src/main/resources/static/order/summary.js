// summary.js: 결제 완료 후 주문 요약 정보 동적 표시

// summary 페이지는 정상적인 결제 완료 후 도달하는 페이지이므로
// 팝업에서 직접 열리지 않고, 부모창에서 location.href로 이동됨

document.addEventListener('DOMContentLoaded', function() {
    console.log('Summary 페이지 로드 완료');

    // === 주문완료 후 세션 정리 ===
    sessionStorage.removeItem('orderId');
    sessionStorage.removeItem('orderDate');
    sessionStorage.removeItem('paymentId');
    sessionStorage.removeItem('idForAdmin');
    sessionStorage.removeItem('orderCompleted');
    sessionStorage.removeItem('orderSummary');

    console.log('세션 정리 완료');

    // 메인 페이지로 이동 버튼
    document.getElementById('goMainBtn')?.addEventListener('click', function() {
        window.location.href = '/main';
    });
});

// summary 페이지에서 나가는 순간 남은 세션 데이터 정리
window.addEventListener('beforeunload', function() {
    sessionStorage.removeItem('orderMeta');
    sessionStorage.removeItem('orderSummary');
});