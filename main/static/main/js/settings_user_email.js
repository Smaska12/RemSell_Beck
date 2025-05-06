document.addEventListener("DOMContentLoaded", function() {
    // Обработчик для отправки формы изменения электронной почты через AJAX
    var editemailBtn = document.getElementById('edit-email-btn');
    var editEmailModal = document.getElementById('edit-email-modal');
    var saveEmailBtn = document.getElementById('save-email-btn');
    var emailForm = document.getElementById('edit-email-form');

    // Open Edit Password Modal
    editemailBtn.onclick = function() {
        openModal('edit-email-modal');
    }

    saveEmailBtn.onclick = function(event) {
        event.preventDefault();

        var formData = new FormData(emailForm);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', updateUseremailUrl, true);
        xhr.onload = function () {
            if (xhr.status == 200) {
                var jsonResponse = JSON.parse(xhr.responseText);
                if (jsonResponse.success) {
                    closeModal('edit-email-modal');
                    document.getElementById('email-updated-message').style.display = 'block';
                    setTimeout(function() {
                        document.getElementById('email-updated-message').style.display = 'none';
                    }, 5000); // Hide message after 5 seconds
                } else {
                    console.error("Error updating email: ", jsonResponse.message);
                }
            } else {

            }
        };
        xhr.onerror = function () {
            alert('Error sending request to server');
        };
        xhr.send(formData);
    };
});
