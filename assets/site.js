/* =============================================================================
   Summit Real Estate Services — Site interactions
   ============================================================================= */
(function() {
    'use strict';

    // ---- Sticky-header compact-on-scroll ----
    const header = document.querySelector('.site-header');
    if (header) {
        let last = 0;
        const onScroll = () => {
            const y = window.scrollY;
            if (y > 24) header.classList.add('scrolled');
            else header.classList.remove('scrolled');
            last = y;
        };
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    }

    // ---- Fade-up observer ----
    const fadeUpObserver = ('IntersectionObserver' in window)
        ? new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('in-view');
                    fadeUpObserver.unobserve(entry.target);
                }
            });
          }, { threshold: 0, rootMargin: '0px 0px -8% 0px' })
        : null;

    function observeFadeUps() {
        if (!fadeUpObserver) {
            document.querySelectorAll('.fade-up').forEach(el => el.classList.add('in-view'));
            return;
        }
        document.querySelectorAll('.fade-up:not(.in-view)').forEach(el => fadeUpObserver.observe(el));
    }
    window.observeFadeUps = observeFadeUps;
    observeFadeUps();

    // Auto-fade-up: tag every section after the first
    document.querySelectorAll('.section, .cta-banner').forEach((sec, i) => {
        if (i === 0) return;
        if (!sec.classList.contains('fade-up')) sec.classList.add('fade-up');
    });
    observeFadeUps();

    // ---- Animated stat counters ----
    function animateCount(el) {
        const target = parseInt(el.dataset.count, 10);
        if (isNaN(target)) return;
        const duration = 1100;
        const start = performance.now();
        const startVal = 0;
        const suffix = (el.dataset.suffix || '').trim();
        const tick = (now) => {
            const t = Math.min(1, (now - start) / duration);
            const ease = 1 - Math.pow(1 - t, 3); // easeOutCubic
            const val = Math.round(startVal + (target - startVal) * ease);
            el.textContent = val.toLocaleString() + suffix;
            if (t < 1) requestAnimationFrame(tick);
            else el.textContent = target.toLocaleString() + suffix;
        };
        requestAnimationFrame(tick);
    }

    if ('IntersectionObserver' in window) {
        const counterObs = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCount(entry.target);
                    counterObs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.4 });
        document.querySelectorAll('[data-count]').forEach(el => counterObs.observe(el));
    } else {
        document.querySelectorAll('[data-count]').forEach(el => animateCount(el));
    }

    // ---- Mobile nav: close on link click ----
    document.querySelectorAll('.site-nav a').forEach(a => {
        a.addEventListener('click', () => {
            const nav = document.querySelector('.site-nav');
            if (nav && nav.classList.contains('open')) nav.classList.remove('open');
        });
    });

    // ---- Smooth scroll for in-page anchors (already covered by html scroll-behavior, but add focus) ----
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', (e) => {
            const id = a.getAttribute('href').slice(1);
            const target = id && document.getElementById(id);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                target.setAttribute('tabindex', '-1');
                target.focus({ preventScroll: true });
            }
        });
    });
})();
