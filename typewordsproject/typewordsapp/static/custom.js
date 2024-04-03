// トップページ
const startLink = document.getElementById('start-link');
const wordListListLink = document.getElementById('word-list-list-link');
const createWordListLink = document.getElementById('create-word-list-link');
const indexLink = document.getElementById('index-link');

document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && startLink !== null) {
        startLink.click();
    } else if (event.key === 'c' && wordListListLink !== null) {
        wordListListLink.click();
    } else if (event.key === 'Enter' && indexLink !== null) {
        indexLink.click();
    }
});