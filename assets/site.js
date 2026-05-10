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
        const duration = 1400;
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

    // Pre-set counter targets so they show the final value before they animate
    // (prevents flash of wrong number if user scrolls quickly)
    document.querySelectorAll('[data-count]').forEach(el => {
        const target = parseInt(el.dataset.count, 10);
        if (!isNaN(target)) el.textContent = target.toLocaleString();
    });

    if ('IntersectionObserver' in window) {
        const counterObs = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCount(entry.target);
                    counterObs.unobserve(entry.target);
                }
            });
        }, { threshold: 0, rootMargin: '0px 0px -15% 0px' });
        document.querySelectorAll('[data-count]').forEach(el => counterObs.observe(el));
    }

    // ---- Mobile nav: close on link click ----
    document.querySelectorAll('.site-nav a').forEach(a => {
        a.addEventListener('click', () => {
            const nav = document.querySelector('.site-nav');
            if (nav && nav.classList.contains('open')) nav.classList.remove('open');
        });
    });

    // ---- Scroll progress bar at top ----
    if (!document.querySelector('.scroll-progress')) {
        const bar = document.createElement('div');
        bar.className = 'scroll-progress';
        document.body.prepend(bar);
        const updateProgress = () => {
            const h = document.documentElement;
            const scrollHeight = h.scrollHeight - h.clientHeight;
            const pct = scrollHeight > 0 ? (h.scrollTop / scrollHeight) * 100 : 0;
            bar.style.width = pct + '%';
        };
        window.addEventListener('scroll', updateProgress, { passive: true });
        window.addEventListener('resize', updateProgress, { passive: true });
        updateProgress();
    }

    // ---- In-view detection for additional decoration (eyebrow underline draw, grid stagger, etc) ----
    if ('IntersectionObserver' in window) {
        const decorObs = new IntersectionObserver((entries) => {
            entries.forEach(e => {
                if (e.isIntersecting) {
                    e.target.classList.add('in-view');
                    decorObs.unobserve(e.target);
                }
            });
        }, { threshold: 0.1, rootMargin: '0px 0px -8% 0px' });
        document.querySelectorAll(
            '.summit-eyebrow, .section-head, .grid-2, .grid-3, .grid-4, .props-grid, .featured-strip'
        ).forEach(el => decorObs.observe(el));
    } else {
        document.querySelectorAll(
            '.summit-eyebrow, .section-head, .grid-2, .grid-3, .grid-4, .props-grid, .featured-strip'
        ).forEach(el => el.classList.add('in-view'));
    }

    // ---- Inject "View Property →" hover CTA on every property card with a detail page ----
    document.querySelectorAll('a.prop').forEach(card => {
        const photo = card.querySelector('.photo');
        if (photo && !photo.querySelector('.hover-cta')) {
            const cta = document.createElement('div');
            cta.className = 'hover-cta';
            cta.textContent = 'View Property';
            photo.appendChild(cta);
        }
    });

    // ---- Magnetic effect on primary CTAs (subtle, tasteful) ----
    document.querySelectorAll(
        '.hero .summit-btn-primary, .cta-banner .summit-btn-primary, .detail-cta-row .summit-btn-primary'
    ).forEach(btn => {
        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            // Max 6px nudge, scaled by distance from center
            btn.style.transform = `translate(${x * 0.15}px, ${y * 0.2}px)`;
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = '';
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
