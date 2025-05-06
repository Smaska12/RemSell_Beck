document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');

    // При загрузке страницы проверяем, есть ли сохраненное значение в локальном хранилище
    const savedSearchTerm = localStorage.getItem('searchTerm');
    if (savedSearchTerm) {
        searchInput.value = savedSearchTerm; // Устанавливаем значение в поле поиска
    }

    searchInput.addEventListener('input', function(event) {
        const searchTerm = event.target.value.trim();
        localStorage.setItem('searchTerm', searchTerm);

        // Отправить запрос на сервер
        fetch(`/search-products/?q=${searchTerm}`)
            .then(response => response.json())
            .then(data => {
                // Обновить содержимое страницы с полученными результатами
                updateProductList(data);
            })
            .catch(error => {
                console.error('Error fetching search results:', error);
            });
    });

    function updateProductList(products) {
        // Очистить текущий список товаров
        const productListContainer = document.querySelector('.product-line-all');
        productListContainer.innerHTML = '';
        console.log(products.length)
        if (products.length === 0) {
            // Если товары не найдены, вывести сообщение
            productListContainer.innerHTML = '<li>Пользователь еще не опубликовал ни одного товара.</li>';
        } else {
            // Добавить новые товары в список
            products.forEach(product => {
                const productHTML = `
                    <div class="product">
                        <a href="{% url 'product_detail' product.id %}">
                            <div class="product-card">
                                <div class="product-image">
                                    <img src="{{ product.image.url }}" alt="{{ product.name }}">
                                </div>
                                <div class="product-details">
                                    <span class="product-title dt1">{{ product.name }}</span>
                                    <span class="product-description dt">{{ product.description }}</span>
                                    <span class="product-quantity dt">Количество: {{ product.quantity }} шт.</span>
                                    <div class="product-rating">
                                        {% for i in stars_range %}
                                            {% if i <= product.avg_rating %}
                                                <svg class="reviews-star" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                                                    <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>
                                                </svg>
                                            {% else %}
                                                <svg class="rating-star" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                                                    <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>
                                                </svg>
                                            {% endif %}
                                        {% endfor %}
                                    </div>
                                </div>
                            </div>
                        </a>
                    </div>
                `;
                productListContainer.insertAdjacentHTML('beforeend', productHTML);
            });
        }
    }
});
