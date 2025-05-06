document.addEventListener("DOMContentLoaded", function() {
    // Получаем элементы из DOM
    const editAvatar = document.getElementById('edit-avatar');
    const editAvatarModal = document.getElementById('edit-avatar-modal');
    const closeAvatarModal = editAvatarModal.querySelector('.close');

    // Обработчик клика на аватарку для открытия модального окна
    editAvatar.addEventListener('click', function() {
        editAvatarModal.classList.add('active');
    });

    // Обработчик клика на кнопку закрытия модального окна
    closeAvatarModal.addEventListener('click', function() {
        editAvatarModal.classList.remove('active');
    });

    // Получаем форму изменения аватарки из DOM
    const editAvatarForm = document.getElementById('edit-avatar-form');

    // Добавляем обработчик события отправки формы
    editAvatarForm.addEventListener('submit', function(event) {
        // Предотвращаем стандартное поведение формы (отправку данных по умолчанию)
        event.preventDefault();

        // Создаем объект FormData для сбора данных формы
        const formData = new FormData(this);

        // Отправляем запрос на сервер с помощью Fetch API
        fetch('/update_avatar/', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (response.ok) {
                // Если ответ успешный, перезагружаем страницу для обновления аватарки
                location.reload();
            } else {
                // Если ответ не успешный, выводим сообщение об ошибке
                console.error('Ошибка при отправке запроса на сервер');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
    });
});
