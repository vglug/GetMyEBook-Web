// Book Carousel Sliding Animation with Navigation
document.addEventListener('DOMContentLoaded', function () {
    console.log('Book carousel script loaded - Sliding mode');

    const carousel = document.getElementById('heroCarousel');
    const navContainer = document.getElementById('carouselNav');
    if (!carousel) return;

    const items = carousel.querySelectorAll('.book-carousel-item');
    const dots = navContainer ? navContainer.querySelectorAll('.nav-dot') : [];

    if (items.length === 0) return;

    // Standardize total books (handle duplicates if needed, but flex layout needs them all)
    // We only remove duplicates if they exist and we're on desktop
    const isMobile = window.innerWidth <= 560;

    // For sliding carousel, we normally want the unique items
    // But index.html provides duplicates. Let's keep only the first set to simplify indexing logic.
    const totalUniqueBooks = dots.length > 0 ? dots.length : items.length / 2;

    // Cleanup if multiple sets exist
    for (let i = totalUniqueBooks; i < items.length; i++) {
        items[i].remove();
    }

    const actualItems = carousel.querySelectorAll('.book-carousel-item');
    let currentIndex = 0;
    const displayDuration = 5000; // 5 seconds per book as requested
    let timer;

    function updateCarousel(index) {
        // Handle wrapping
        if (index >= actualItems.length) index = 0;
        if (index < 0) index = actualItems.length - 1;

        currentIndex = index;

        // Sliding effect using transform
        const offset = -currentIndex * 100;
        carousel.style.transform = `translateX(${offset}%)`;

        // Update active classes for items
        actualItems.forEach((item, i) => {
            if (i === currentIndex) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        // Update active classes for dots
        dots.forEach((dot, i) => {
            if (i === currentIndex) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }

    function startTimer() {
        stopTimer();
        timer = setInterval(() => {
            updateCarousel(currentIndex + 1);
        }, displayDuration);
    }

    function stopTimer() {
        if (timer) clearInterval(timer);
    }

    // Set up initial state
    updateCarousel(0);
    startTimer();

    // Dot navigation
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            updateCarousel(index);
            startTimer(); // Reset timer on manual click
        });
    });

    // Pause on hover
    carousel.addEventListener('mouseenter', stopTimer);
    carousel.addEventListener('mouseleave', startTimer);

    // Initial log
    console.log(`✅ Carousel started: ${actualItems.length} books, ${displayDuration}ms interval`);
});
