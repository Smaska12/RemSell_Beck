// Вызвать updateUserStatus() сразу после загрузки страницы
document.addEventListener("DOMContentLoaded", function() {
    updateUserStatus();
});

// Периодически отправлять запросы на сервер для обновления статуса пользователя
setInterval(updateUserStatus, 100000); // каждую 1 минут (100000 миллисекунд)

function updateUserStatus() {
    fetch('/update-user-status/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {

        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error.message);
        });
}