/**
 * Функция для обновления индикатора количества товаров в корзине 
 */
document.addEventListener('DOMContentLoaded', function() {
    // Функция обновления счетчика корзины
    function updateCartCounter() {
        fetch('/cart/count')
            .then(response => response.json())
            .then(data => {
                const cartCountElement = document.getElementById('cart-count');
                if (cartCountElement) {
                    cartCountElement.textContent = data.count;
                    
                    // Добавляем класс для анимации, если счетчик больше 0
                    if (data.count > 0) {
                        cartCountElement.classList.add('has-items');
                    } else {
                        cartCountElement.classList.remove('has-items');
                    }
                }
            })
            .catch(error => console.error('Ошибка при получении данных корзины:', error));
    }

    // Обновляем счетчик при загрузке страницы
    updateCartCounter();

    // Находим все формы добавления в корзину
    const addToCartForms = document.querySelectorAll('form[action^="/add_to_cart/"]');
    
    // Добавляем обработчики для AJAX-добавления товаров в корзину
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            // Если есть класс "ajax-add-to-cart", перехватываем отправку формы
            if (form.classList.contains('ajax-add-to-cart')) {
                event.preventDefault();
                
                const formData = new FormData(form);
                const url = form.getAttribute('action');
                
                fetch(url, {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (response.ok) {
                        // Обновляем счетчик корзины
                        updateCartCounter();
                        
                        // Показываем уведомление
                        showNotification('Товар добавлен в корзину');
                    }
                })
                .catch(error => console.error('Ошибка при добавлении в корзину:', error));
            }
        });
    });

    // Функция для показа уведомления
    function showNotification(message) {
        // Проверяем, существует ли контейнер для уведомлений
        let notificationContainer = document.getElementById('notification-container');
        
        if (!notificationContainer) {
            // Если контейнер не существует, создаем его
            notificationContainer = document.createElement('div');
            notificationContainer.id = 'notification-container';
            document.body.appendChild(notificationContainer);
        }
        
        // Создаем уведомление
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-check-circle"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Добавляем уведомление в контейнер
        notificationContainer.appendChild(notification);
        
        // Добавляем класс для анимации появления
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Удаляем уведомление через 3 секунды
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
}); 