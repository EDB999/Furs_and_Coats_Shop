document.addEventListener('DOMContentLoaded', function() {
    // Проверяем наличие глобальных переменных с URL
    if (!window.catalogUrls) {
        console.error('catalogUrls не определены. Убедитесь, что скрипт подключен после определения window.catalogUrls в HTML.');
        return;
    }

    // Обработка кнопок "В корзину"
    const addToCartButtons = document.querySelectorAll('.product-btn');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            if (!productId) return;

            const originalText = this.textContent;
            this.textContent = 'Добавление...';
            this.disabled = true;

            const formData = new FormData();
            formData.append('product_id', productId);

            fetch(window.catalogUrls.addToCart, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.textContent = '✓ Добавлено';
                    this.style.background = 'linear-gradient(135deg, #4caf50 0%, #45a049 100%)';
                    setTimeout(() => {
                        this.textContent = originalText;
                        this.style.background = '';
                        this.disabled = false;
                    }, 2000);
                } else {
                    alert('Ошибка: ' + data.error);
                    this.textContent = originalText;
                    this.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при добавлении товара в корзину');
                this.textContent = originalText;
                this.disabled = false;
            });
        });
    });

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

    // Инициализация Swiper
    const paginationEl = document.querySelector('.swiper-pagination');
    if (!paginationEl) {
        console.error('Pagination element not found!');
    }

    const swiper = new Swiper('.catalog-swiper', {
        slidesPerView: 1,
        spaceBetween: 30,
        loop: true,
        autoplay: {
            delay: 3000,
            disableOnInteraction: false,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
            renderBullet: function (index, className) {
                return '<span class="' + className + '"></span>';
            },
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        breakpoints: {
            640: {
                slidesPerView: 2,
                spaceBetween: 20,
            },
            768: {
                slidesPerView: 2,
                spaceBetween: 30,
            },
            1024: {
                slidesPerView: 3,
                spaceBetween: 40,
            },
        },
        on: {
            init: function() {
                // Убеждаемся, что все слайды имеют одинаковую высоту
                this.updateAutoHeight();
                // Убеждаемся, что pagination видим
                const pagination = document.querySelector('.swiper-pagination');
                if (pagination) {
                    pagination.style.display = 'flex';
                    pagination.style.visibility = 'visible';
                    pagination.style.opacity = '1';
                }
            },
            slideChange: function() {
                this.updateAutoHeight();
            }
        }
    });
});
