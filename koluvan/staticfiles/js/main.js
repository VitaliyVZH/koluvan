// настройка свайпера блока hero
const heroSwiper = new Swiper('.swiper', {
  effect: "fade",
  allowTouchMove: false,
  loop: true,      // зацикливание
  speed: 1000,     // плавность перемещения
  autoplay: {       // настройки автозамены изображения
    delay: 4500,    // время статичности изображения
  },
  sourceMappingURL: 'bootstrap.min.css.map',
});


// Насторойка валидации формы в блоке Контакты
$(document).ready(function() {
    // Инициализация маски для телефона
    $('#id_phone').inputmask({
        mask: [
        '+7 (999) 999-99-99', // Основной формат
        '8 (999) 999-99-99'   // Альтернатива с 8
    ],
        showMaskOnHover: false,
        placeholder: '_', // Символ-заполнитель
        clearIncomplete: true, // Очищать неполные значения
        onBeforePaste: function (pastedValue) {
            // Оставляем только цифры при вставке
            return pastedValue.replace(/\D/g, '');
        }
    });

    // Автоматически добавляем +7 при фокусе, если поле пустое
    $('#id_phone').focus(function() {
        if (!this.value.trim()) {
            this.value = ' ';
        }
    });

    // Предотвращаем удаление +7
    $('#id_phone').on('keydown', function(e) {
        if (this.selectionStart < 4 &&
            (e.key === 'Backspace' || e.key === 'Delete')) {
            e.preventDefault();
        }
    });
});


// Скрипт для бургер-меню
document.addEventListener('DOMContentLoaded', function() {
  const burgerButton = document.getElementById('burgerButton');
  const mobileMenu = document.getElementById('mobileMenu');

  if (burgerButton) {
    burgerButton.addEventListener('click', function() {
      // Переключаем состояние меню
      this.classList.toggle('active');
      mobileMenu.classList.toggle('active');
      document.body.classList.toggle('no-scroll');
    });
  }

  // Закрытие меню при клике на ссылку
  const navLinks = document.querySelectorAll('.mobile-nav__link');
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      burgerButton.classList.remove('active');
      mobileMenu.classList.remove('active');
      document.body.classList.remove('no-scroll');
    });
  });

  // Закрытие меню при клике вне области
  mobileMenu.addEventListener('click', (e) => {
    if (e.target === mobileMenu) {
      burgerButton.classList.remove('active');
      mobileMenu.classList.remove('active');
      document.body.classList.remove('no-scroll');
    }
  });
});


document.addEventListener('DOMContentLoaded', function() {
  const gallerySwiper = new Swiper('.gallerySwiper', {
    loop: true,
    slidesPerView: 1,
    spaceBetween: 20,
    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    },
    pagination: {
      el: '.swiper-pagination',
      clickable: true,
    },
    breakpoints: {
      640: {
        slidesPerView: 2,
      },
      1024: {
        slidesPerView: 3,
      }
    }
  });
});


