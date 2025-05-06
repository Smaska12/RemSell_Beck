document.addEventListener("DOMContentLoaded", function() {
    // Обработчик для отправки формы изменения настроек безопасности через AJAX
    var editsecurityBtn = document.getElementById('edit-security-btn');
    var editSecurityModal = document.getElementById('edit-security-modal');
    var saveSecurityBtn = document.getElementById('save-security-btn');
    var securityForm = document.getElementById('edit-security-form');

    // Open Edit Password Modal
//    editsecurityBtn.onclick = function() {
//        openModal('edit-security-modal');
//    }

    saveSecurityBtn.onclick = function(event) {
        event.preventDefault();

        var formData = new FormData(securityForm);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', updateUsersecurityUrl, true);
        xhr.onload = function () {
            if (xhr.status == 200) {
                var jsonResponse = JSON.parse(xhr.responseText);
                if (jsonResponse.success) {
                    closeModal('edit-security-modal');
                    alert('Security settings successfully updated!');
                } else {
                    console.error("Error updating security settings: ", jsonResponse.message);
                }
            } else {
                alert('Server error: ' + xhr.status);
            }
        };
        xhr.onerror = function () {
            alert('Error sending request to server');
        };
        xhr.send(formData);
    };
});
