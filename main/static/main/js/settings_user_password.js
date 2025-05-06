document.addEventListener("DOMContentLoaded", function() {
    var editPasswordBtn = document.getElementById('edit-password-btn');
    var editPasswordModal = document.getElementById('edit-password-modal');
    var savePasswordBtn = document.getElementById('save-password-btn');
    var passwordForm = document.getElementById('edit-password-form');

    // Open Edit Password Modal
    editPasswordBtn.onclick = function() {
        openModal('edit-password-modal');
    }

    // Save Password Button Clicked
    savePasswordBtn.onclick = function(event) {
        event.preventDefault();

    // Create FormData object to send form data
    var formData = new FormData(passwordForm);

    // Send AJAX request to update password
    var xhr = new XMLHttpRequest();
    xhr.open('POST', updateUserpasswordUrl, true);
    xhr.onload = function () {
        if (xhr.status == 200) {
            var jsonResponse = JSON.parse(xhr.responseText);
            if (jsonResponse.success) {
                window.location.href = jsonResponse.redirect_url;
            } else {
                // Handle error
                console.error("Error updating password: ", jsonResponse.errors);
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
