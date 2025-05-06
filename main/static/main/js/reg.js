// Функция для отображения сообщений об ошибках
function displayErrorMessages() {
    var errorMessageContainer = document.querySelector('.error-message');
    if (errorMessageContainer) {
        errorMessageContainer.style.display = 'block';
    }
}

// Вызываем функцию для отображения сообщений об ошибках при загрузке страницы
displayErrorMessages();

fetch(url)
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      window.location.href = '{% url 'home' %}';
    } else {
      errorMessage.textContent = data.error_message;
      errorMessage.style.display = 'block'; // Показываем сообщение об ошибке
    }
  })
  .catch(error => {
    console.error('Ошибка:', error);
    // Обработка ошибки по вашему усмотрению
  });
