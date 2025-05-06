document.addEventListener('DOMContentLoaded', function() {
  const ratingContainer = document.querySelector('.rating');
  const stars = ratingContainer.querySelectorAll('.rating-star');
  const avgRating = parseFloat(ratingContainer.dataset.rating); // Получаем среднюю оценку товара

  stars.forEach((star, index) => {
    // Определяем, какие звезды нужно заполнить в зависимости от оценки
    if (avgRating >= index + 1) {
      star.classList.add('filled');
    } else if (avgRating > index) {
      star.classList.add('half-filled');
    }
  });
});

document.addEventListener('DOMContentLoaded', function() {
    // Получаем текущее значение фильтра из URL
    const urlParams = new URLSearchParams(window.location.search);
    const ratingFilter = urlParams.get('rating');

    // Если значение фильтра существует, устанавливаем атрибут "selected" для соответствующего option
    if (ratingFilter) {
        const ratingSelect = document.getElementById('rating');
        const options = ratingSelect.options;

        for (let i = 0; i < options.length; i++) {
            if (options[i].value === ratingFilter) {
                options[i].setAttribute('selected', 'selected');
                break;
            }
        }
    }
});