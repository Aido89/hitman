(function () {
  function initSlider(root) {
    const track = root.querySelector('.slider-track');
    const slides = Array.from(root.querySelectorAll('.slider-slide'));
    const dotsContainer = root.querySelector('.slider-dots');
    const prevBtn = root.querySelector('[data-slide-prev]');
    const nextBtn = root.querySelector('[data-slide-next]');
    if (!track || slides.length === 0) return;

    let index = 0;
    let autoplay;

    slides.forEach((_, i) => {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'slider-dot' + (i === 0 ? ' active' : '');
      dot.setAttribute('aria-label', 'Слайд ' + (i + 1));
      dot.addEventListener('click', () => goTo(i));
      dotsContainer && dotsContainer.appendChild(dot);
    });
    const dots = dotsContainer ? Array.from(dotsContainer.children) : [];

    function goTo(i) {
      index = (i + slides.length) % slides.length;
      track.style.transform = `translateX(-${index * 100}%)`;
      dots.forEach((d, di) => d.classList.toggle('active', di === index));
    }

    prevBtn && prevBtn.addEventListener('click', () => goTo(index - 1));
    nextBtn && nextBtn.addEventListener('click', () => goTo(index + 1));

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function startAutoplay() {
      if (prefersReducedMotion) return;
      autoplay = setInterval(() => goTo(index + 1), 6000);
    }
    startAutoplay();
    root.addEventListener('mouseenter', () => clearInterval(autoplay));
    root.addEventListener('mouseleave', startAutoplay);
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-slider]').forEach(initSlider);
  });
})();
