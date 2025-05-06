document.addEventListener('DOMContentLoaded', function () {
    const descriptionTextarea = document.getElementById('id_description');

    function shortenLinebreaks() {
        // Удаляем все множественные переносы строк
        let formattedText = descriptionTextarea.value.replace(/\n\s*\n/g, '\n');

        // Если осталось больше двух переносов строк, оставляем только два
        const count = (formattedText.match(/\n/g) || []).length;
        if (count > 2) {
            formattedText = formattedText.replace(/(\n\s*){3,}/g, '\n\n');
        }

        // Обновляем содержимое
        descriptionTextarea.value = formattedText;
    }

    descriptionTextarea.addEventListener('input', function () {
        shortenLinebreaks();
    });

    // Вызываем функцию shortenLinebreaks при загрузке страницы
    shortenLinebreaks();
});
