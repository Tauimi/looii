// Глобальный обработчик AJAX-запросов для корзины
document.addEventListener('DOMContentLoaded', function() {
    // Обработка всех форм добавления в корзину
    document.querySelectorAll('.ajax-add-to-cart').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault(); // Предотвращаем стандартное поведение формы
            
            // Находим input с количеством внутри текущей формы
            const thisQuantityInput = form.querySelector('input[name="quantity"]');
            
            // Проверяем количество перед отправкой формы (если поле существует)
            if (thisQuantityInput) {
                let currentValue = parseInt(thisQuantityInput.value);
                let maxValue = parseInt(thisQuantityInput.getAttribute('max'));
                
                if (isNaN(currentValue) || currentValue < 1) {
                    thisQuantityInput.value = 1;
                } else if (currentValue > maxValue) {
                    thisQuantityInput.value = maxValue;
                }
            }
            
            // Подготавливаем данные формы
            const formData = new FormData(form);
            const url = form.getAttribute('action');
            
            // Показываем небольшую анимацию загрузки
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.classList.add('loading');
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            }
            
            // Добавляем заголовок для определения AJAX-запроса на сервере
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Восстанавливаем кнопку
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.classList.remove('loading');
                    submitButton.innerHTML = 'В корзину';
                }
                
                if (data.success) {
                    // Очищаем сохраненное количество после успешного добавления в корзину
                    const productId = form.getAttribute('data-product-id') || 
                                    form.querySelector('input[name="product_id"]')?.value ||
                                    form.action.split('/').pop();
                    if (productId) {
                        localStorage.removeItem('product_quantity_' + productId);
                    }
                    
                    // Обновляем счетчик товаров в корзине
                    updateCartCounter(data.cart_count);
                    
                    // Показываем уведомление об успешном добавлении
                    showNotification(data.message, 'success');
                    
                    // Анимация кнопки
                    animateAddToCartButton(submitButton);
                } else {
                    // Показываем уведомление об ошибке
                    showNotification(data.message, 'warning');
                }
            })
            .catch(error => {
                console.error('Ошибка при добавлении товара в корзину:', error);
                showNotification('Произошла ошибка при добавлении товара в корзину', 'error');
                
                // Восстанавливаем кнопку
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.classList.remove('loading');
                    submitButton.innerHTML = 'В корзину';
                }
            });
        });
    });

    // Функция обновления счетчика корзины
    function updateCartCounter(count) {
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = count;
            
            // Добавляем класс для анимации, если счетчик больше 0
            if (count > 0) {
                cartCountElement.classList.add('has-items');
            } else {
                cartCountElement.classList.remove('has-items');
            }
        }
    }

    // Функция для показа уведомления
    function showNotification(message, type = 'success') {
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
        notification.className = `notification notification-${type}`;
        
        // Выбираем иконку в зависимости от типа уведомления
        let icon = 'fa-check-circle';
        if (type === 'warning') icon = 'fa-exclamation-circle';
        if (type === 'error') icon = 'fa-times-circle';
        
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${icon}"></i>
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

    // Функция для анимации кнопки добавления в корзину
    function animateAddToCartButton(button) {
        if (button) {
            button.classList.add('added');
            setTimeout(() => {
                button.classList.remove('added');
            }, 1000);
        }
    }
}); 