document.addEventListener('DOMContentLoaded', function() {
    var userProfile = document.querySelector('.user-profile');
    var dropdown = userProfile.querySelector('.dropdown');
    var dropdownArrow = userProfile.querySelector('.dropdown-arrow');

    userProfile.addEventListener('click', function(event) {
        dropdown.classList.toggle('show');
        dropdownArrow.classList.toggle('active');
    });

    document.addEventListener('click', function(event) {
        if (!userProfile.contains(event.target)) {
            dropdown.classList.remove('show');
            dropdownArrow.classList.remove('active');
        }
    });
});


document.addEventListener("DOMContentLoaded", function() {
    window.addEventListener("scroll", function() {
        var header = document.querySelector(".site-header");
        if (window.scrollY > 50) {
            header.classList.add("compact");
        } else {
            header.classList.remove("compact");
        }
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const catalogLink = document.getElementById('catalog-link');
    const catalogOverlay = document.getElementById('catalog-overlay');

    catalogLink.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent the default behavior of the anchor tag

        // Toggle the display property of the catalog overlay
        catalogOverlay.style.display = catalogOverlay.style.display === 'block' ? 'none' : 'block';
    });

    catalogOverlay.addEventListener("click", function(event) {
        if (event.target === catalogOverlay) {
            catalogOverlay.style.display = "none";
        }
    });
});


document.addEventListener("DOMContentLoaded", function() {
    var productDescriptions = document.querySelectorAll(".product-description");

    productDescriptions.forEach(function(description) {
        var maxLength = 100; // Максимальная длина описания
        var text = description.textContent.trim();

        if (text.length > maxLength) {
            var truncatedText = text.slice(0, maxLength) + "...";
            description.textContent = truncatedText;
        }
    });
});


// Открытие модального окна и передача данных о товаре
function openModal(productName, productDescription, productQuantity, productImage) {
    var modal = document.getElementById("modal");
    var modalTitle = modal.querySelector(".product-title");
    var modalDescription = modal.querySelector(".product-description");
    var modalQuantity = modal.querySelector(".product-quantity");
    var modalImage = modal.querySelector(".product-image img");

    modalTitle.textContent = productName;
    modalDescription.textContent = productDescription;
    modalQuantity.textContent = "Количество: " + productQuantity + " шт.";
    modalImage.src = productImage;

    modal.style.display = "block";
}

// Закрытие модального окна
function closeModal() {
    var modal = document.getElementById("modal");
    modal.style.display = "none";
}


// Функция для открытия модального окна добавления товара
function openAddProductModal() {
    var modal = document.getElementById('add-product-modal');
    modal.style.display = 'block';
}

// Функция для закрытия модального окна добавления товара
function closeAddProductModal() {
    var modal = document.getElementById('add-product-modal');
    modal.style.display = 'none';
}

// Закрытие модального окна при клике вне его области
window.addEventListener('click', function(event) {
    var modal = document.getElementById("modal");
    if (event.target == modal) {
        modal.style.display = "none";
    }
});



document.addEventListener("DOMContentLoaded", function() {
    // JavaScript-функция для отправки формы на сервер
    document.getElementById('add-product-form').addEventListener('submit', function(event) {
        // код обработки отправки формы
        event.preventDefault(); // Предотвращаем стандартное поведение формы (перезагрузку страницы)

        // Получаем данные формы
        var formData = new FormData(this);

        // Отправляем данные на сервер
        fetch('{% url "add_product" %}', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': '{{ csrf_token }}' // Добавляем CSRF-токен для защиты от CSRF-атак
            }
        })
        .then(response => {
            // Обрабатываем ответ сервера
            if (response.ok) {
                // Если ответ успешный, закрываем модальное окно
                closeAddProductModal();
            } else {
                // Если ответ неуспешный, обрабатываем ошибку
                throw new Error('Ошибка при добавлении товара');
            }
        })
        .catch(error => {
            // Обрабатываем ошибки
            console.error('Ошибка:', error);
            // Здесь можно добавить отображение сообщения об ошибке пользователю
        });
    });
});


function redirectToAddProduct() {
        window.location.href = "/add_product";
    }






