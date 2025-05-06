// JavaScript for Settings Page

// Function to open modal
function openModal(modalId) {
    var modal = document.getElementById(modalId);
    modal.style.display = "block";
}

// Function to close modal
function closeModal(modalId) {
    var modal = document.getElementById(modalId);
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    var modals = document.getElementsByClassName('modal');
    for (var i = 0; i < modals.length; i++) {
        var modal = modals[i];
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}

// When the document is fully loaded
document.addEventListener("DOMContentLoaded", function() {
    // Edit Username Modal
    var editUsernameBtn = document.getElementById('edit-username-btn');
    var editUsernameModal = document.getElementById('edit-username-modal');
    var saveUsernameBtn = document.getElementById('save-username-btn');
    var newUsernameInput = document.getElementById('new-username');

    // Open Edit Username Modal
    editUsernameBtn.onclick = function() {
        openModal('edit-username-modal');
    }

    // Save Username Button Clicked
    saveUsernameBtn.onclick = function() {
        var newUsername = newUsernameInput.value;
        var csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
        var formData = new FormData();
        formData.append('new_username', newUsername);
        formData.append('csrfmiddlewaretoken', csrfToken);

        // AJAX Request to update username
        var xhr = new XMLHttpRequest();
        xhr.open('POST', updateUsernameUrl, true);
        xhr.onload = function () {
            if (xhr.status == 200) {
                var jsonResponse = JSON.parse(xhr.responseText);
                if (jsonResponse.success) {
                    // Update current username displayed on the page
                    document.getElementById('current-username').textContent = newUsername;
                    // Close modal
                    closeModal('edit-username-modal');
                } else {
                    // Handle error
                    console.error("Error updating username: ", jsonResponse.message);
                }
            } else {
                // Handle error
                console.error("Error updating username. Server returned status code: ", xhr.status);
            }
        };
        xhr.onerror = function () {
            console.error("Error updating username. Request failed.");
        };
        xhr.send(formData);
    }
});
