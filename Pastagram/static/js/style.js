
/* 포스트 댓글 입력하면 버튼 보이기 */
document.querySelector('.comment-content-class').addEventListener('input', function() {
    var contentValue = this.value.trim();
    var submitButton = document.querySelector('.content-button-class');

    if (contentValue.length > 0) {
        submitButton.style.display = 'block';
    } else {
        submitButton.style.display = 'none';
    }
});

/* 이미지 파일 선택하면 이름 띄우기 */
function displayFileName(input) {
    var fileInputs = input.files;
    var fileNameDisplay = document.querySelector('.file_name');

    if (fileInputs.length > 0) {
        var fileNames = Array.from(fileInputs).map(function(file) {
            return file.name;
        });

        fileNameDisplay.textContent = fileNames.join(', ');
                fileNameDisplay.style.fontSize = '10px';
                fileNameDisplay.style.width = '430px';

    } else {
        fileNameDisplay.textContent = '파일을 선택해주세요.';
        fileNameDisplay.style.fontSize = '14px';
        fileNameDisplay.style.width = '180px';


    }
}

/* 이미지 url 전송 */
function submitImages() {
    var selectedImageUrls = $('input[name="selectedImages"]:checked').map(function() {
        return $(this).val();
    }).get();

}