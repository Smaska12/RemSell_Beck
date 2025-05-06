document.addEventListener('DOMContentLoaded', function () {
    const editButton = document.getElementById('edit-bio-btn');
    const saveButton = document.getElementById('save-bio-btn');
    const bioForm = document.getElementById('bio-form');
    const editableBio = document.getElementById('editable-bio');
    const bioTextarea = document.getElementById('bio-textarea');
    const bioText = document.querySelector('.bio-text');

    function shortenLinebreaks() {
        // Удаляем все множественные переносы строк
        let formattedText = bioText.innerHTML.replace(/(<br>\s*){2,}/g, '<br><br>');

        // Обновляем содержимое
        bioText.innerHTML = formattedText;
    }

    if (editButton) {
        editButton.addEventListener('click', function () {
            editButton.style.display = 'none';
            editableBio.style.display = 'none';
            saveButton.style.display = 'inline-block';
            bioForm.style.display = 'block';

            shortenLinebreaks();
        });
    }

    if (saveButton) {
        saveButton.addEventListener('click', function () {
            saveButton.style.display = 'none';
            editableBio.style.display = 'block';
            editButton.style.display = 'inline-block';
            bioForm.style.display = 'none';

            shortenLinebreaks();
        });
    }

    shortenLinebreaks();
});
