/**
 * Карусель для главной страницы ТехноМаркета
 */
document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.querySelector('.carousel');
    if (!carousel) return; // Если карусели нет, завершаем выполнение

    const carouselSlide = carousel.querySelector('.carousel-slide');
    const carouselItems = carousel.querySelectorAll('.carousel-item');
    const prevBtn = carousel.querySelector('.carousel-prev');
    const nextBtn = carousel.querySelector('.carousel-next');
    const dotsContainer = carousel.querySelector('.carousel-dots');

    // Начальный индекс
    let currentIndex = 0;
    let interval;
    
    // Проверяем, что у нас есть слайды
    if (carouselItems.length === 0) return;

    // Создаем точки навигации
    carouselItems.forEach((_, index) => {
        const dot = document.createElement('span');
        dot.classList.add('carousel-dot');
        if (index === 0) dot.classList.add('active');
        dot.addEventListener('click', () => {
            goToSlide(index);
            resetInterval();
        });
        dotsContainer.appendChild(dot);
    });

    // Получаем все точки
    const dots = dotsContainer.querySelectorAll('.carousel-dot');

    // Устанавливаем обработчики для кнопок
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            goToPrev();
            resetInterval();
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            goToNext();
            resetInterval();
        });
    }

    // Переход к следующему слайду
    function goToNext() {
        currentIndex = (currentIndex + 1) % carouselItems.length;
        updateCarousel();
    }

    // Переход к предыдущему слайду
    function goToPrev() {
        currentIndex = (currentIndex - 1 + carouselItems.length) % carouselItems.length;
        updateCarousel();
    }

    // Переход к конкретному слайду
    function goToSlide(index) {
        currentIndex = index;
        updateCarousel();
    }

    // Обновляем карусель
    function updateCarousel() {
        const translateValue = -currentIndex * 100 + '%';
        carouselSlide.style.transform = `translateX(${translateValue})`;
        
        // Обновляем активную точку
        dots.forEach((dot, index) => {
            if (index === currentIndex) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }

    // Автоматическое переключение слайдов
    function startInterval() {
        interval = setInterval(() => {
            goToNext();
        }, 5000); // Меняем слайд каждые 5 секунд
    }

    // Сбрасываем интервал после ручного переключения
    function resetInterval() {
        clearInterval(interval);
        startInterval();
    }

    // Останавливаем автоматическое переключение при наведении
    carousel.addEventListener('mouseenter', () => {
        clearInterval(interval);
    });

    // Возобновляем автоматическое переключение после ухода курсора
    carousel.addEventListener('mouseleave', () => {
        startInterval();
    });

    // Обработка свайпов на мобильных устройствах
    let touchStartX = 0;
    let touchEndX = 0;

    carousel.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].clientX;
    }, { passive: true });

    carousel.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].clientX;
        handleSwipe();
    }, { passive: true });

    function handleSwipe() {
        const difference = touchStartX - touchEndX;
        if (difference > 50) {  // Свайп влево (следующий слайд)
            goToNext();
            resetInterval();
        } else if (difference < -50) {  // Свайп вправо (предыдущий слайд)
            goToPrev();
            resetInterval();
        }
    }

    // Запускаем автоматическое переключение
    startInterval();
});