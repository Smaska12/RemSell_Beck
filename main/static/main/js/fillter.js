document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchForm = document.querySelector('.search-bar');
    const searchButton = searchForm.querySelector('button[type="submit"]');
    const searchResults = document.getElementById('search-results');

    searchButton.addEventListener('click', function(event) {
        event.preventDefault(); // Отменяем действие по умолчанию при клике на кнопку

        const searchTerm = searchInput.value.trim(); // Получаем значение из поля ввода, удаляем лишние пробелы

        // Отправляем запрос на сервер для поиска товаров
        fetch(`/search/?q=${searchTerm}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Проверяем, есть ли результаты поиска
                if (data.length > 0) {
                    // Если есть результаты, обновляем содержимое страницы
                    // Например, обновляем список товаров
                    searchResults.innerHTML = ''; // Очищаем предыдущие результаты поиска
                    data.forEach(item => {
                        // Создаем элемент для каждого товара и добавляем его в список результатов
                        const listItem = document.createElement('li');
                        listItem.textContent = item.name;
                        searchResults.appendChild(listItem);
                    });
                } else {
                    // Если результаты не найдены, отображаем сообщение об отсутствии результатов
                    searchResults.innerHTML = '<p>Результаты не найдены</p>';
                }
            })
            .catch(error => {
                // Если произошла ошибка при выполнении запроса, отображаем сообщение об ошибке
                searchResults.innerHTML = '<p>Произошла ошибка при выполнении запроса</p>';
                console.error('Error:', error);
            });
    });
});
