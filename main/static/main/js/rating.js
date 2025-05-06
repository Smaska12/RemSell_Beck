document.addEventListener('DOMContentLoaded', function() {
    const ratingContainers = document.querySelectorAll('.rating');
    const ratingInput = document.getElementById('rating-input');

    ratingContainers.forEach(ratingContainer => {
        const stars = ratingContainer.querySelectorAll('.star');
        let selectedRating = 0;
        const form = ratingContainer.closest('form');

        stars.forEach((star, index) => {
            star.addEventListener('click', function() {
                selectedRating = index + 1; // Set the selected rating
                highlightStars(index, stars);
                // Update the hidden input field value
                ratingInput.value = selectedRating;
            });
            star.addEventListener('mouseenter', function() {
                if (selectedRating === 0) { // If rating is not selected, highlight stars on hover
                    highlightStars(index, stars);
                }
            });
            star.addEventListener('mouseleave', function() {
                if (selectedRating === 0) { // If rating is not selected, reset highlighting on mouse leave
                    resetStars(stars);
                }
            });
        });
    });

    function highlightStars(index, stars) {
        for (let i = 0; i <= index; i++) {
            stars[i].classList.add('active');
        }
        for (let i = index + 1; i < stars.length; i++) {
            stars[i].classList.remove('active');
        }
    }

    function resetStars(stars) {
        stars.forEach(star => {
            star.classList.remove('active');
        });
    }
});


