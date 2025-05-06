// chat.js

document.addEventListener("DOMContentLoaded", function () {
    var messageForm = document.getElementById("message-form");
    var messageInput = document.getElementById("message-input");
    var messageBox = document.getElementById("message-full-box");
    var chatIdInput = document.getElementById("chat-id");

    var firstUpdate = true;


    if (firstUpdate) {
        messageBox.scrollTop = messageBox.scrollHeight;
        // Установите флаг в false после первого обновления
        firstUpdate = false;
    }

    // Function to send a message via AJAX
    function sendMessage(content) {
        var formData = new FormData();
        formData.append("chat_id", chatIdInput.value);
        formData.append("content", content);

        fetch(messageForm.getAttribute("data-send-message-url"), {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken") // Ensure CSRF token is sent with POST request
            }
        })
        .then(function (response) {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(function (data) {
            // Message sent successfully, update chat messages
            updateChat();
        })
        .catch(function (error) {
            console.error("Error sending message:", error);
        });
    }

    // Function to fetch and update chat messages via AJAX
    function updateChat(chatId) {
        fetch("/get_chat_messages/?chat_id=" + chatIdInput.value)
        .then(function (response) {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(function (data) {
            // Clear existing messages
            messageBox.innerHTML = "";

            // Populate chat messages
            data.messages.forEach(function (message) {
                var messageDiv = document.createElement("div");
                messageDiv.classList.add("chat-message");
                messageDiv.innerHTML = `
                    <div class="message-sender">${message.sender}</div>
                    <div class="message-content">${message.content}</div>
                `;
                messageBox.appendChild(messageDiv);
            });

        })
        .catch(function (error) {
            console.error("Error fetching chat messages:", error);
        });
    }

    // Функция для получения значения из localStorage
    function getStoredChatId() {
        return localStorage.getItem("selectedChatId");
    }

    // Функция для сохранения значения в localStorage
    function storeChatId(chatId) {
        localStorage.setItem("selectedChatId", chatId);
    }

    // Event listener for submitting message form
    messageForm.addEventListener("submit", function (event) {
        event.preventDefault();
        var messageContent = messageInput.value.trim();
        if (messageContent !== "") {
            sendMessage(messageContent);
            messageInput.value = ""; // Clear message input after sending

            // Прокрутить вниз после обновления чата
            messageBox.scrollTop = messageBox.scrollHeight;
        }
    });

    // Event listener for clicking on a chat link
    var chatLinks = document.querySelectorAll(".user-list li");
    chatLinks.forEach(function (link) {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            var chatId = link.getAttribute("data-chat-id");
            chatIdInput.value = chatId;
            storeChatId(chatId); // Сохраняем выбранный ID чата в localStorage

            // Update the URL to reflect the current chat ID
            var newUrl = "/chats/" + chatId;
            window.location.href = newUrl;

            updateChat(chatId); // Update chat messages when switching chats
        });
    });

    // При загрузке страницы проверяем, есть ли сохраненный ID чата в localStorage
    var storedChatId = getStoredChatId();
    if (storedChatId) {
        chatIdInput.value = storedChatId;
        updateChat(storedChatId); // Обновляем сообщения чата, если есть сохраненный ID
    }

    // Store chat ID in sessionStorage when page is refreshed
    window.addEventListener("beforeunload", function() {
        storeChatId(chatIdInput.value);
    });

    // Function to retrieve CSRF token from cookies
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            var cookies = document.cookie.split(";");
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function clearStoredChatId() {
        localStorage.removeItem("selectedChatId");
    }

    clearStoredChatId();

    // Function to update chat messages periodically
    // Start auto-update after a delay (e.g., 5 seconds)
    setInterval(function(chatId) {
        return function() {
            if (chatId) {
                updateChat(chatId);
            }
        };
    }(chatIdInput.value), 5000);
});


function toggleDropdown() {
    var dropdownContent = document.getElementById("dropdown-content");
    if (dropdownContent.style.display === "" || dropdownContent.style.display === "none") {
        dropdownContent.style.display = "block";
    } else {
        dropdownContent.style.display = "none";
    }
}

document.addEventListener("click", function(event) {
    var dropdownContent = document.getElementById("dropdown-content");
    var settingsIcon = document.querySelector(".settings-box-header");

    // Проверяем, произошел ли клик вне области всплывающего окна и на иконке
    if (!dropdownContent.contains(event.target) && !settingsIcon.contains(event.target)) {
        dropdownContent.style.display = "none";
    }

    // Проверяем, был ли клик на элементе выпадающего меню или иконке настройки
    if (event.target.classList.contains("settings-box-header") || dropdownContent.contains(event.target)) {
        return; // Останавливаем выполнение обработчика клика
    }
});