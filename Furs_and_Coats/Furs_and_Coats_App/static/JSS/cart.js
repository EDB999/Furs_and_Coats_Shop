document.addEventListener('DOMContentLoaded', function() {
    // Проверяем наличие глобальных переменных с URL
    if (!window.cartUrls) {
        console.error('cartUrls не определены. Убедитесь, что скрипт подключен после определения window.cartUrls в HTML.');
        return;
    }

    const cartItems = document.querySelectorAll('.cart-item');

    cartItems.forEach(item => {
        const cartItemId = item.dataset.cartItemId;
        const quantityValue = item.querySelector('.quantity-value');
        const minusBtn = item.querySelector('.minus-btn');
        const plusBtn = item.querySelector('.plus-btn');
        const removeBtn = item.querySelector('.remove-btn');
        const itemTotalPrice = item.querySelector('.item-total-price');
        const productPrice = parseFloat(itemTotalPrice.dataset.unitPrice);

        function updateQuantity(change) {
            const currentQuantity = parseInt(quantityValue.textContent);
            const newQuantity = Math.max(1, currentQuantity + change);

            if (newQuantity === currentQuantity && change < 0) return;

            const formData = new FormData();
            formData.append('cart_item_id', cartItemId);
            formData.append('quantity', newQuantity);

            fetch(window.cartUrls.updateCartItem, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    quantityValue.textContent = data.quantity;
                    itemTotalPrice.textContent = parseFloat(data.item_total).toFixed(2);
                    updateTotalAmount(data.total_amount);
                } else {
                    alert('Ошибка: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при обновлении корзины');
            });
        }

        minusBtn.addEventListener('click', () => {
            const currentQuantity = parseInt(quantityValue.textContent);
            if (currentQuantity > 1) {
                updateQuantity(-1);
            }
        });

        plusBtn.addEventListener('click', () => updateQuantity(1));

        removeBtn.addEventListener('click', () => {
            if (confirm('Вы уверены, что хотите удалить этот товар из корзины?')) {
                const formData = new FormData();
                formData.append('cart_item_id', cartItemId);

                fetch(window.cartUrls.removeFromCart, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        item.style.transition = 'opacity 0.3s, transform 0.3s';
                        item.style.opacity = '0';
                        item.style.transform = 'translateX(-100px)';
                        setTimeout(() => {
                            item.remove();
                            updateTotalAmount(data.total_amount);
                            if (document.querySelectorAll('.cart-item').length === 0) {
                                location.reload();
                            }
                        }, 300);
                    } else {
                        alert('Ошибка: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Произошла ошибка при удалении товара');
                });
            }
        });
    });

    function updateTotalAmount(total) {
        const totalAmountEl = document.querySelector('.total-amount');
        if (totalAmountEl) {
            totalAmountEl.textContent = parseFloat(total).toFixed(2);
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Обновление цены товара при загрузке (с учетом количества)
    cartItems.forEach(item => {
        const quantity = parseInt(item.querySelector('.quantity-value').textContent);
        const pricePerUnit = parseFloat(item.querySelector('.item-total-price').dataset.unitPrice);
        const totalPrice = pricePerUnit * quantity;
        item.querySelector('.item-total-price').textContent = totalPrice.toFixed(2);
    });

    // Обработчик кнопки "Очистить корзину"
    const clearCartBtn = document.querySelector('.clear-cart-btn');
    if (clearCartBtn) {
        clearCartBtn.addEventListener('click', () => {
            if (confirm('Вы уверены, что хотите очистить всю корзину? Все товары будут удалены.')) {
                const formData = new FormData();
                
                fetch(window.cartUrls.clearCart, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Анимация удаления всех товаров
                        const allItems = document.querySelectorAll('.cart-item');
                        allItems.forEach((item, index) => {
                            setTimeout(() => {
                                item.style.transition = 'opacity 0.3s, transform 0.3s';
                                item.style.opacity = '0';
                                item.style.transform = 'translateX(-100px)';
                            }, index * 50);
                        });
                        
                        // Перезагрузка страницы после анимации
                        setTimeout(() => {
                            location.reload();
                        }, allItems.length * 50 + 300);
                    } else {
                        alert('Ошибка: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Произошла ошибка при очистке корзины');
                });
            }
        });
    }
});
