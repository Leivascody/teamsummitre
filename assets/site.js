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

    // ---- ⌘K Command palette ----
    (function setupCmdK() {
        // Build the palette overlay (singleton)
        if (document.querySelector('.cmdk')) return;
        const isMac = navigator.platform.toLowerCase().includes('mac');
        const modKey = isMac ? '⌘' : 'Ctrl';

        const overlay = document.createElement('div');
        overlay.className = 'cmdk';
        overlay.innerHTML = `
            <div class="cmdk-panel" role="dialog" aria-label="Command palette">
                <div class="cmdk-search">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    <input type="text" id="cmdkInput" placeholder="Search properties, pages, markets..." autocomplete="off" spellcheck="false">
                    <span class="cmdk-kbd">esc</span>
                </div>
                <div class="cmdk-results" id="cmdkResults"></div>
                <div class="cmdk-footer">
                    <span><span class="cmdk-kbd">↑↓</span> navigate</span>
                    <span><span class="cmdk-kbd">↵</span> open</span>
                    <span>Summit · ${isMac ? '⌘K' : 'Ctrl+K'} anywhere</span>
                </div>
            </div>`;
        document.body.appendChild(overlay);

        const panel = overlay.querySelector('.cmdk-panel');
        const input = overlay.querySelector('#cmdkInput');
        const results = overlay.querySelector('#cmdkResults');

        // Build the search index from window.SUMMIT_PROPERTIES + nav links
        const props = window.SUMMIT_PROPERTIES || [];
        const heroes = window.SUMMIT_HEROES || {};
        const detailPages = window.SUMMIT_DETAIL_PAGES || {};
        const stateNames = window.SUMMIT_STATE_NAMES || {};

        // Detect path depth (in /property/ subdirectory pages, links need ../ prefix)
        const inSub = window.location.pathname.includes('/property/');
        const pre = inSub ? '../' : '';

        const navItems = [
            { type: 'page', icon: 'H', title: 'Home', href: pre + 'index.html', meta: '/' },
            { type: 'page', icon: 'S', title: 'Services', href: pre + 'services.html', meta: 'services' },
            { type: 'page', icon: 'P', title: 'Portfolio · all 107 properties', href: pre + 'properties.html', meta: 'portfolio' },
            { type: 'page', icon: 'T', title: 'Team', href: pre + 'team.html', meta: 'team' },
            { type: 'page', icon: 'C', title: 'Contact · start a conversation', href: pre + 'contact.html', meta: 'contact' },
            { type: 'market', icon: 'WI', title: 'Wisconsin · 32 properties', href: pre + 'wisconsin.html', meta: 'market' },
            { type: 'market', icon: 'MO', title: 'Missouri · 31 properties', href: pre + 'missouri.html', meta: 'market' },
        ];

        const propItems = props.map(p => {
            const key = `${p.addr}|${p.city}|${p.state}`;
            const slug = detailPages[key];
            return {
                type: 'property',
                icon: p.state,
                title: `${p.addr}`,
                subtitle: `${p.city}, ${p.state}`,
                href: slug
                    ? pre + 'property/' + slug + '.html'
                    : pre + 'properties.html?state=' + p.state + '&q=' + encodeURIComponent(p.addr.split(' ')[0]),
                meta: slug ? 'detail' : 'list',
                searchable: `${p.addr} ${p.city} ${p.state} ${stateNames[p.state] || ''}`.toLowerCase(),
            };
        });

        let selectedIndex = 0;
        let currentItems = [];

        function fuzzyMatch(query, str) {
            // simple subsequence match — just-good-enough fuzzy
            query = query.toLowerCase().trim();
            str = str.toLowerCase();
            if (!query) return true;
            let qi = 0;
            for (let si = 0; si < str.length && qi < query.length; si++) {
                if (str[si] === query[qi]) qi++;
            }
            return qi === query.length;
        }
        function scoreMatch(query, item) {
            const q = query.toLowerCase().trim();
            if (!q) return 0;
            const text = (item.searchable || (item.title + ' ' + (item.meta || ''))).toLowerCase();
            if (text.startsWith(q)) return 100;
            if (text.includes(' ' + q)) return 80;
            if (text.includes(q)) return 60;
            return 20;
        }

        function render() {
            const q = input.value.trim();
            results.innerHTML = '';

            // Filter
            let nav = navItems.filter(i => fuzzyMatch(q, i.title + ' ' + (i.meta || '')));
            let pp  = propItems.filter(i => fuzzyMatch(q, i.searchable));
            if (q) {
                nav.sort((a, b) => scoreMatch(q, b) - scoreMatch(q, a));
                pp.sort((a, b) => scoreMatch(q, b) - scoreMatch(q, a));
            }
            // Cap properties
            pp = pp.slice(0, 12);

            currentItems = [];
            function appendGroup(label, items) {
                if (!items.length) return;
                const g = document.createElement('div');
                g.className = 'cmdk-group';
                g.textContent = label;
                results.appendChild(g);
                items.forEach(item => {
                    const a = document.createElement('a');
                    a.className = 'cmdk-item';
                    a.href = item.href;
                    a.innerHTML = `
                        <div class="icon">${item.icon}</div>
                        <div>
                            <div class="title">${item.title}</div>
                            ${item.subtitle ? `<div style="font-size:12px;color:var(--summit-slate);">${item.subtitle}</div>` : ''}
                        </div>
                        <div class="meta">${item.meta || ''}</div>`;
                    results.appendChild(a);
                    currentItems.push(a);
                });
            }
            appendGroup('Pages & Markets', nav);
            appendGroup(`Properties${pp.length === 12 ? ' · top 12' : ''}`, pp);

            if (!currentItems.length) {
                const empty = document.createElement('div');
                empty.className = 'cmdk-empty';
                empty.textContent = q ? `No results for "${q}"` : 'Start typing to search...';
                results.appendChild(empty);
            } else {
                selectedIndex = 0;
                updateSelection();
            }
        }
        function updateSelection() {
            currentItems.forEach((el, i) => el.classList.toggle('selected', i === selectedIndex));
            const sel = currentItems[selectedIndex];
            if (sel) sel.scrollIntoView({ block: 'nearest' });
        }
        function open() {
            overlay.classList.add('open');
            input.value = '';
            render();
            setTimeout(() => input.focus(), 30);
        }
        function close() {
            overlay.classList.remove('open');
        }

        input.addEventListener('input', render);
        input.addEventListener('keydown', e => {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                selectedIndex = Math.min(currentItems.length - 1, selectedIndex + 1);
                updateSelection();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                selectedIndex = Math.max(0, selectedIndex - 1);
                updateSelection();
            } else if (e.key === 'Enter') {
                e.preventDefault();
                const sel = currentItems[selectedIndex];
                if (sel) window.location.href = sel.href;
            } else if (e.key === 'Escape') {
                close();
            }
        });
        overlay.addEventListener('click', e => {
            if (e.target === overlay) close();
        });

        // Trigger keys (⌘K / Ctrl+K) and / to focus
        document.addEventListener('keydown', e => {
            if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
                e.preventDefault();
                if (overlay.classList.contains('open')) close();
                else open();
            } else if (e.key === '/' && !overlay.classList.contains('open')) {
                const tag = (document.activeElement && document.activeElement.tagName) || '';
                if (!['INPUT', 'TEXTAREA', 'SELECT'].includes(tag)) {
                    e.preventDefault();
                    open();
                }
            }
        });

        // Wire any .cmdk-trigger buttons in the nav
        document.querySelectorAll('.cmdk-trigger').forEach(btn => {
            btn.addEventListener('click', open);
        });

        // Expose for debugging
        window.SummitCmdK = { open, close };
    })();

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
