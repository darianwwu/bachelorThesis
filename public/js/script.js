// JavaScript-Code in der script.js
const imageUpload = document.getElementById('imageUpload');
const previewImage = document.getElementById('previewImage');

imageUpload.addEventListener('change', function() {
    const file = this.files[0];
    const reader = new FileReader();

    reader.addEventListener('load', function() {
        previewImage.src = reader.result;
    });

    if (file) {
        reader.readAsDataURL(file);
    }
});
