// Функция для инициализации приложения
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация часов
    initClock();
    
    // Инициализация счетчика посещений
    initVisitorCounter();
    
    // Функционал специальных возможностей
    initAccessibilityFeatures();
    
    // Инициализация количества товаров в корзине
    updateCartItemCount();
    
    // Инициализация элементов управления количеством товара
    initQuantityControls();
    
    // Инициализация калькулятора корзины, если находимся на странице корзины
    if (document.querySelector('.cart-table')) {
        initCartCalculator();
    }
    
    // Инициализация предварительного просмотра изображений
    initImagePreviews();
});

// Функция для инициализации часов
function initClock() {
    const clockElement = document.getElementById('clock');
    if (!clockElement) return;
    
    function updateClock() {
        const now = new Date();
        let hours = now.getHours();
        let minutes = now.getMinutes();
        let seconds = now.getSeconds();
        
        // Добавляем ведущий ноль, если значение меньше 10
        hours = hours < 10 ? '0' + hours : hours;
        minutes = minutes < 10 ? '0' + minutes : minutes;
        seconds = seconds < 10 ? '0' + seconds : seconds;
        
        const timeString = `${hours}:${minutes}:${seconds}`;
        clockElement.textContent = timeString;
    }
    
    // Обновляем время каждую секунду
    updateClock();
    setInterval(updateClock, 1000);
}

// Функция для инициализации счетчика посещений
function initVisitorCounter() {
    const counterElement = document.getElementById('visitor-count');
    if (!counterElement) return;
    
    // Получаем количество посещений с сервера
    fetch('/get_visitors_count')
        .then(response => response.json())
        .then(data => {
            counterElement.textContent = data.count;
        })
        .catch(error => console.error('Ошибка при получении счетчика посещений:', error));
}

// Функции для специальных возможностей
function initAccessibilityFeatures() {
    // Эта функция теперь пустая, так как вся функциональность управления доступностью
    // перенесена в отдельный файл accessibility.js, который подключается в layout.html
    
    // Если нужно, можно добавить дополнительные функции доступности, не связанные с основными настройками
    console.log('Инициализация дополнительных функций доступности из main.js');
    
    // Пример добавления функциональности: увеличение отдельных изображений при наведении
    const productImages = document.querySelectorAll('.product-image img');
    productImages.forEach(img => {
        img.addEventListener('mouseenter', function() {
            this.style.transition = 'transform 0.3s ease';
            this.style.transform = 'scale(1.05)';
        });
        
        img.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

// Функция для обновления счетчика товаров в корзине
function updateCartItemCount() {
    const cartCountElement = document.getElementById('cart-count');
    if (!cartCountElement) return;
    
    // Получаем данные корзины из localStorage или используем пустой массив
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    
    // Подсчитываем общее количество товаров в корзине
    const itemCount = cart.reduce((total, item) => total + item.quantity, 0);
    
    // Обновляем отображение
    cartCountElement.textContent = itemCount;
    
    // Скрываем счетчик, если корзина пуста
    if (itemCount === 0) {
        cartCountElement.style.display = 'none';
    } else {
        cartCountElement.style.display = 'flex';
    }
}

// Функция для инициализации элементов управления количеством товара
function initQuantityControls() {
    const decreaseButtons = document.querySelectorAll('.quantity-decrease');
    const increaseButtons = document.querySelectorAll('.quantity-increase');
    
    decreaseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const currentValue = parseInt(input.value);
            if (currentValue > 1) {
                input.value = currentValue - 1;
                
                // Если мы на странице корзины, обновляем итоговую сумму и отправляем данные на сервер
                if (document.querySelector('.cart-table')) {
                    updateCartItemSubtotal(input);
                    
                    // Если есть функция обновления корзины на сервере, вызываем её
                    if (typeof updateCartItemOnServer === 'function') {
                        const productId = input.getAttribute('data-product-id') || 
                                        input.closest('tr').querySelector('a')?.getAttribute('href')?.split('/').pop();
                        if (productId) {
                            updateCartItemOnServer(productId, input.value);
                        }
                    }
                }
            }
        });
    });
    
    increaseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const currentValue = parseInt(input.value);
            // Добавляем проверку на максимальное значение
            const maxValue = parseInt(input.getAttribute('max') || Number.MAX_SAFE_INTEGER);
            
            if (currentValue < maxValue) {
                input.value = currentValue + 1;
                
                // Если мы на странице корзины, обновляем итоговую сумму и отправляем данные на сервер
                if (document.querySelector('.cart-table')) {
                    updateCartItemSubtotal(input);
                    
                    // Если есть функция обновления корзины на сервере, вызываем её
                    if (typeof updateCartItemOnServer === 'function') {
                        const productId = input.getAttribute('data-product-id') || 
                                        input.closest('tr').querySelector('a')?.getAttribute('href')?.split('/').pop();
                        if (productId) {
                            updateCartItemOnServer(productId, input.value);
                        }
                    }
                }
            }
        });
    });
}

// Функция для инициализации калькулятора корзины
function initCartCalculator() {
    const quantityInputs = document.querySelectorAll('.cart-quantity input');
    
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            // Проверяем и корректируем введенное значение
            let currentValue = parseInt(this.value);
            let maxValue = parseInt(this.getAttribute('max') || Number.MAX_SAFE_INTEGER);
            
            if (isNaN(currentValue) || currentValue < 1) {
                this.value = 1;
            } else if (currentValue > maxValue) {
                this.value = maxValue;
            }
            
            updateCartItemSubtotal(this);
            
            // Если есть функция обновления корзины на сервере, вызываем её
            if (typeof updateCartItemOnServer === 'function') {
                const productId = this.getAttribute('data-product-id') || 
                                this.closest('tr').querySelector('a')?.getAttribute('href')?.split('/').pop();
                if (productId) {
                    updateCartItemOnServer(productId, this.value);
                }
            }
        });
    });
    
    // Начальный расчет
    calculateCartTotal();
}

// Функция для обновления промежуточной суммы товара в корзине
function updateCartItemSubtotal(input) {
    const row = input.closest('tr');
    const priceElement = row.querySelector('.item-price');
    const subtotalElement = row.querySelector('.item-subtotal');
    
    if (!priceElement || !subtotalElement) return;
    
    const price = parseFloat(priceElement.dataset.price);
    const quantity = parseInt(input.value);
    
    const subtotal = price * quantity;
    subtotalElement.textContent = subtotal.toFixed(2) + ' ₽';
    subtotalElement.dataset.subtotal = subtotal;
    
    // Пересчитываем общую сумму корзины
    calculateCartTotal();
}

// Функция для расчета общей суммы корзины
function calculateCartTotal() {
    const subtotalElements = document.querySelectorAll('.item-subtotal');
    const totalElement = document.getElementById('cart-total-value');
    
    if (!totalElement) return;
    
    let total = 0;
    
    subtotalElements.forEach(element => {
        total += parseFloat(element.dataset.subtotal);
    });
    
    totalElement.textContent = total.toFixed(2) + ' ₽';
}

// Функция для инициализации предварительного просмотра изображений
function initImagePreviews() {
    const thumbnails = document.querySelectorAll('.thumbnail');
    
    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', function() {
            const fullImageSrc = this.dataset.fullImage;
            const fullImageAlt = this.alt;
            
            // Создаем модальное окно для просмотра полного изображения
            const modal = document.createElement('div');
            modal.classList.add('image-modal');
            
            const modalContent = document.createElement('div');
            modalContent.classList.add('image-modal-content');
            
            const image = document.createElement('img');
            image.src = fullImageSrc;
            image.alt = fullImageAlt;
            
            const closeButton = document.createElement('span');
            closeButton.classList.add('modal-close');
            closeButton.innerHTML = '&times;';
            closeButton.addEventListener('click', function() {
                document.body.removeChild(modal);
            });
            
            modalContent.appendChild(image);
            modalContent.appendChild(closeButton);
            modal.appendChild(modalContent);
            
            // Закрытие модального окна при клике вне изображения
            modal.addEventListener('click', function(event) {
                if (event.target === modal) {
                    document.body.removeChild(modal);
                }
            });
            
            document.body.appendChild(modal);
        });
    });
}

// Функция для добавления товара в корзину
function addToCart(productId, productName, productPrice, quantity = 1) {
    // Получаем текущую корзину из localStorage или создаем новую
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    
    // Проверяем, есть ли уже этот товар в корзине
    const existingItemIndex = cart.findIndex(item => item.productId === productId);
    
    if (existingItemIndex !== -1) {
        // Если товар уже есть, увеличиваем количество
        cart[existingItemIndex].quantity += quantity;
    } else {
        // Если товара еще нет, добавляем его
        cart.push({
            productId: productId,
            name: productName,
            price: productPrice,
            quantity: quantity
        });
    }
    
    // Сохраняем обновленную корзину
    localStorage.setItem('cart', JSON.stringify(cart));
    
    // Обновляем отображение количества товаров в корзине
    updateCartItemCount();
    
    // Показываем сообщение об успешном добавлении
    showNotification('Товар добавлен в корзину');
}

// Функция для отображения уведомления
function showNotification(message) {
    // Проверяем, существует ли уже уведомление
    let notification = document.querySelector('.notification');
    
    if (!notification) {
        // Создаем элемент уведомления
        notification = document.createElement('div');
        notification.classList.add('notification');
        document.body.appendChild(notification);
    }
    
    // Обновляем текст и показываем уведомление
    notification.textContent = message;
    notification.classList.add('show');
    
    // Скрываем уведомление через 3 секунды
    setTimeout(function() {
        notification.classList.remove('show');
    }, 3000);
} 