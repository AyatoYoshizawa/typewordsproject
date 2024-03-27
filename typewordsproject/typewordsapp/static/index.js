// キーボードのEnterが押されたらid=start-linkのaタグをクリック
const startLink = document.getElementById('start-link');

document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        startLink.click();
    }
});