#!/usr/bin/env python3
"""
Phase 4 — Property detail pages with photo galleries

For each marquee property:
  1. Walk source folder, score photos, pick best 8 for gallery
  2. Optimize each at 1600px wide → /assets/property-galleries/<slug>/01.jpg ...
  3. Generate /property/<slug>.html from template
  4. Update sitemap.xml

Run:
    python3 generate-property-pages.py
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

PHOTOS_SRC = Path("/Users/codyleivas/Library/CloudStorage/Dropbox-Personal/04_Business/Summit_Real_Estate_Services/Marketing/Brand_System/Photos")
WEB_ROOT = Path("/Users/codyleivas/Library/CloudStorage/Dropbox-Personal/04_Business/Summit_Real_Estate_Services/Marketing/Brand_System/website")
GALLERY_DEST = WEB_ROOT / "assets" / "property-galleries"
DETAIL_DEST = WEB_ROOT / "property"
HEROES_DIR = WEB_ROOT / "assets" / "property-heroes"

# 15 marquee properties
# (slug, address, city, state, hero_slug_in_property-heroes/, asset_type)
MARQUEE = [
    ("stag-industrial-stl", "201-215 Stag Industrial Boulevard", "St. Louis", "MO",
     "201-215-stag-industrial-stl", "Multi-Tenant Industrial Flex"),
    ("hall-street-stl", "6501 Hall Street", "St. Louis", "MO",
     "6501-hall-street-stl", "Distribution Facility"),
    ("parkway-circle-brooklyn-center", "6601 Parkway Circle", "Brooklyn Center", "MN",
     "6601-parkway-circle-brooklyn-center", "Multi-Tenant Industrial"),
    ("1115-cottonwood-hartland", "1115 Cottonwood Avenue", "Hartland", "WI",
     "1115-cottonwood-hartland", "Industrial / Manufacturing"),
    ("1100-cottonwood-hartland", "1100 Cottonwood Avenue", "Hartland", "WI",
     "1100-cottonwood-hartland", "Industrial / Distribution"),
    ("9009-n-51st-brown-deer", "9009 N 51st Street", "Brown Deer", "WI",
     "9009-n-51st-brown-deer", "Distribution / Warehouse"),
    ("eden-prairie-tech-park", "9600 West 76th Street", "Eden Prairie", "MN",
     "9600-w-76th-eden-prairie", "Office / Flex Campus"),
    ("4333-w-71st-indianapolis", "4333 W. 71st Street", "Indianapolis", "IN",
     "4333-w-71st-indianapolis", "Distribution Facility"),
    ("hoff-industrial-ofallon", "1477 Hoff Industrial Drive", "O'Fallon", "MO",
     "1477-hoff-industrial-ofallon", "Industrial / Manufacturing"),
    ("chouteau-stl", "2327 Chouteau Avenue", "St. Louis", "MO",
     "2327-chouteau-stl", "Urban Industrial"),
    ("grant-industrial-ofallon", "1400 Grant Industrial Drive", "O'Fallon", "MO",
     "1400-grant-industrial-ofallon", "Industrial / Logistics"),
    ("earth-city-bridgeton", "4710 Earth City Expressway", "Bridgeton", "MO",
     "4710-earth-city-bridgeton", "Office / Industrial"),
    ("ambassador-stl", "1241 Ambassador Boulevard", "St. Louis", "MO",
     "1241-ambassador-stl", "Industrial / Warehouse"),
    ("metro-blvd-maryland-heights", "2676 Metro Boulevard", "Maryland Heights", "MO",
     "2676-metro-maryland-heights", "Multi-Tenant Industrial"),
    ("crittenden-louisville", "4810-4852 Crittenden Drive", "Louisville", "KY",
     "4810-4852-crittenden-louisville", "Distribution / Logistics"),
]

STATE_NAMES = {
    "WI": "Wisconsin", "MO": "Missouri", "MN": "Minnesota", "IN": "Indiana",
    "GA": "Georgia",  "AZ": "Arizona",  "UT": "Utah",      "OH": "Ohio",
    "PA": "Pennsylvania", "TX": "Texas", "VA": "Virginia", "IL": "Illinois",
    "AR": "Arkansas", "KY": "Kentucky", "TN": "Tennessee"
}

IMAGE_EXT = {".jpg", ".jpeg", ".png"}
GOOD_KEYWORDS = ["exterior", "aerial", "front", "outside", "drone", "building"]
BAD_KEYWORDS = [
    "interior", "inside", "roof", "leak", "damage", "broken", "repair",
    "warning", "issue", "problem", "lippert tile", "asphalt", "construction",
    "demo", "thumbnail", "screenshot", "screen shot", "map", "diagram",
    "drawing", "plan", "drivers license", " dl ", " dl.", "id card",
    "headshot", "logo", "brochure", "edit bw"
]
GALLERY_WIDTH = 1600
GALLERY_QUALITY = 78
GALLERY_COUNT = 8


def ensure_pillow():
    try:
        import PIL  # noqa
        return True
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--user",
                       "--break-system-packages", "Pillow"], capture_output=True)
        try:
            import PIL  # noqa
            return True
        except ImportError:
            return False


def score_for_gallery(fpath):
    name = fpath.name.lower()
    size = fpath.stat().st_size
    score = 0
    for bad in BAD_KEYWORDS:
        if bad in name:
            return -1000
    if name.startswith("dji"):
        score += 100
    if " edit" in name or "edited" in name:
        score += 30
    for good in GOOD_KEYWORDS:
        if good in name:
            score += 20
    if size > 4_000_000: score += 30
    elif size > 1_500_000: score += 15
    elif size > 500_000: score += 5
    elif size < 100_000: score -= 30
    if re.search(r"-\d+\.[a-z]+$", name):
        score -= 5
    return score


def pick_gallery(folder):
    """Pick up to GALLERY_COUNT photos with variety (different DJI numbers / scenes)."""
    if not folder.exists():
        return []
    all_files = []
    for f in folder.iterdir():
        if not f.is_file() or f.suffix.lower() not in IMAGE_EXT:
            continue
        s = score_for_gallery(f)
        if s > 0:
            all_files.append((s, f))
    all_files.sort(key=lambda x: -x[0])

    # Bias for variety: prefer different filename "stems" (DJI_0290, DJI_0301,
    # etc — avoid 5 versions of the same photo)
    picked = []
    seen_stems = set()
    for score, f in all_files:
        # stem = base filename minus -1, -2 suffix
        stem = re.sub(r"-\d+$", "", f.stem.lower())
        # also strip trailing whitespace + edit suffix
        stem = re.sub(r"\s+edit.*$", "", stem)
        if stem in seen_stems:
            continue
        seen_stems.add(stem)
        picked.append(f)
        if len(picked) >= GALLERY_COUNT:
            break
    # If we don't have enough, fill with the best remaining (allowing dupes of stems)
    if len(picked) < GALLERY_COUNT:
        for _, f in all_files:
            if f not in picked:
                picked.append(f)
                if len(picked) >= GALLERY_COUNT:
                    break
    return picked


def optimize_for_gallery(src, dest):
    from PIL import Image, ImageOps
    img = Image.open(src)
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB":
        img = img.convert("RGB")
    if img.width > GALLERY_WIDTH:
        ratio = GALLERY_WIDTH / img.width
        new_h = int(img.height * ratio)
        img = img.resize((GALLERY_WIDTH, new_h), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "JPEG", quality=GALLERY_QUALITY, optimize=True, progressive=True)
    return dest.stat().st_size


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{addr}, {city}, {state} | Summit Real Estate Services</title>
    <meta name="description" content="{addr} in {city}, {state_full} — a {asset_type} property managed by Summit Real Estate Services. View photos and learn about this asset.">
    <meta name="theme-color" content="#19273C">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="https://teamsummitre.com/property/{slug}.html">
    <meta property="og:title" content="{addr} — {city}, {state}">
    <meta property="og:description" content="{asset_type} managed by Summit Real Estate Services in {city}, {state_full}.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://teamsummitre.com/property/{slug}.html">
    <meta property="og:image" content="https://teamsummitre.com/assets/property-heroes/{hero_slug}.jpg">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="https://teamsummitre.com/assets/property-heroes/{hero_slug}.jpg">
    <link rel="icon" type="image/svg+xml" href="../assets/summit-logo-mark-navy.svg">
    <link rel="stylesheet" href="../assets/summit-brand.css">
    <link rel="stylesheet" href="../assets/site.css">
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Place",
      "name": "{addr}",
      "address": {{
        "@type": "PostalAddress",
        "streetAddress": "{addr}",
        "addressLocality": "{city}",
        "addressRegion": "{state}",
        "addressCountry": "US"
      }}
    }}
    </script>
</head>
<body>

<header class="site-header">
    <div class="container">
        <a href="../index.html" class="site-logo">
            <img src="../assets/summit-logo-mark-navy.svg" alt="Summit Real Estate Services logomark">
            <span class="logo-text">Summit<small>Real Estate Services</small></span>
        </a>
        <button class="nav-toggle" aria-label="Toggle navigation" onclick="document.querySelector('.site-nav').classList.toggle('open')">
            <span></span><span></span><span></span>
        </button>
        <nav class="site-nav">
            <ul>
                <li><a href="../index.html">Home</a></li>
                <li><a href="../services.html">Services</a></li>
                <li><a href="../properties.html" class="active">Portfolio</a></li>
                <li><a href="../team.html">Team</a></li>
            </ul>
            <a href="../contact.html" class="summit-btn summit-btn-primary">Start a Conversation</a>
        </nav>
    </div>
</header>

<section class="detail-hero">
    <img src="../assets/property-heroes/{hero_slug}.jpg" alt="{addr} aerial view">
    <div class="container">
        <span class="summit-eyebrow">Property</span>
        <h1>{addr}</h1>
        <div class="city-state">{city}, {state_full}</div>
    </div>
</section>

<section class="fact-bar">
    <div class="container">
        <div class="fact">
            <div class="label">Market</div>
            <div class="value">{city}, {state}</div>
        </div>
        <div class="fact">
            <div class="label">Asset Type</div>
            <div class="value">{asset_type}</div>
        </div>
        <div class="fact">
            <div class="label">Region</div>
            <div class="value">{state_full}</div>
        </div>
        <div class="fact">
            <div class="label">Operator</div>
            <div class="value">Summit Real Estate Services</div>
        </div>
    </div>
</section>

<section class="section surface-paper">
    <div class="container">
        <div class="section-head">
            <span class="summit-eyebrow">Photo Gallery</span>
            <h2>{addr}</h2>
            <p>A selection of exterior, aerial, and site views of this Summit-managed asset.</p>
        </div>
        <div class="gallery-grid">
{gallery_html}
        </div>
    </div>
</section>

<section class="detail-content surface-white">
    <div class="container">
        <span class="summit-eyebrow">About This Property</span>
        <h2>Managed with institutional discipline.</h2>
        <p>{addr} in {city}, {state_full} is one of {asset_count_phrase} commercial real estate assets Summit operates across {state_count} states. As a fully integrated operator and manager, we run this property with the rigor of an institutional team and the care of a long-term owner.</p>
        <p>Summit's role on this asset spans tenant relations, lease administration, vendor and maintenance management, capital improvements, and owner reporting. The property is part of a portfolio that prioritizes durable income, downside protection, and disciplined operations — the core-plus thesis Summit brings to every building it touches.</p>
        <div class="detail-cta-row">
            <a href="../contact.html" class="summit-btn summit-btn-primary">Discuss This Property</a>
            <a href="../properties.html" class="summit-btn summit-btn-secondary">Browse Full Portfolio</a>
        </div>
    </div>
</section>

<footer class="site-footer">
    <div class="container">
        <div class="footer-grid">
            <div class="footer-brand">
                <img src="../assets/summit-logo-mark-white.svg" alt="Summit Real Estate Services logomark">
                <div class="name">Summit Real Estate Services</div>
                <p>Fully integrated operator of core-plus commercial real estate. Acquisitions, asset management, and property operations across the United States.</p>
            </div>
            <div>
                <h4>Company</h4>
                <ul>
                    <li><a href="../index.html">Home</a></li>
                    <li><a href="../services.html">Services</a></li>
                    <li><a href="../properties.html">Portfolio</a></li>
                    <li><a href="../team.html">Team</a></li>
                    <li><a href="../contact.html">Contact</a></li>
                </ul>
            </div>
            <div>
                <h4>Services</h4>
                <ul>
                    <li><a href="../services.html#acquisitions">Acquisition Advisory</a></li>
                    <li><a href="../services.html#operations">Asset & Property Management</a></li>
                    <li><a href="../services.html#sponsor">PE & Sponsor Support</a></li>
                    <li><a href="../services.html#portfolio">Portfolio Strategy</a></li>
                </ul>
            </div>
            <div>
                <h4>Contact</h4>
                <ul>
                    <li><a href="mailto:info@teamsummitre.com">info@teamsummitre.com</a></li>
                    <li><a href="../contact.html">Start a Conversation</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <span>&copy; 2026 Summit Real Estate Services. All rights reserved.</span>
            <span>107 assets · 189 tenants · 15 states</span>
        </div>
    </div>
</footer>

<!-- Lightbox -->
<div class="lightbox" id="lightbox">
    <button class="close" onclick="closeLightbox()">×</button>
    <button class="nav prev" onclick="navLightbox(-1)">‹</button>
    <button class="nav next" onclick="navLightbox(1)">›</button>
    <img id="lightbox-img" alt="">
    <div class="counter" id="lightbox-counter"></div>
</div>

<script src="../assets/site.js"></script>
<script>
(function() {{
    const photos = {photo_paths_json};
    let current = 0;
    const lb = document.getElementById('lightbox');
    const lbImg = document.getElementById('lightbox-img');
    const counter = document.getElementById('lightbox-counter');

    document.querySelectorAll('.gallery-grid > [data-idx]').forEach(el => {{
        el.addEventListener('click', () => openLightbox(parseInt(el.dataset.idx, 10)));
    }});
    function openLightbox(idx) {{
        current = idx;
        update();
        lb.classList.add('open');
    }}
    window.closeLightbox = function() {{ lb.classList.remove('open'); }};
    window.navLightbox = function(delta) {{
        current = (current + delta + photos.length) % photos.length;
        update();
    }};
    function update() {{
        lbImg.src = photos[current];
        counter.textContent = (current + 1) + ' / ' + photos.length;
    }}
    document.addEventListener('keydown', e => {{
        if (!lb.classList.contains('open')) return;
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowLeft') navLightbox(-1);
        if (e.key === 'ArrowRight') navLightbox(1);
    }});
    lb.addEventListener('click', e => {{ if (e.target === lb) closeLightbox(); }});
}})();
</script>
</body>
</html>
"""


def main():
    if not ensure_pillow():
        print("Could not install Pillow.")
        sys.exit(1)
    GALLERY_DEST.mkdir(parents=True, exist_ok=True)
    DETAIL_DEST.mkdir(parents=True, exist_ok=True)

    # For the SUMMIT_DETAIL_PAGES JS map
    detail_pages_js = {}

    print(f"Phase 4 — Property detail pages\n")

    for slug, addr, city, state, hero_slug, asset_type in MARQUEE:
        state_full = STATE_NAMES.get(state, state)
        folder = PHOTOS_SRC / state_full / f"{addr} - {city}".replace(":", "").replace("/", "-")
        photos = pick_gallery(folder)
        if len(photos) < 4:
            print(f"  ✗ {slug}: only {len(photos)} qualifying photos — skipped")
            continue

        # Optimize gallery photos
        gallery_dir = GALLERY_DEST / slug
        gallery_dir.mkdir(parents=True, exist_ok=True)
        gallery_photos = []
        for i, src in enumerate(photos[:GALLERY_COUNT], start=1):
            dest_name = f"{i:02d}.jpg"
            dest = gallery_dir / dest_name
            optimize_for_gallery(src, dest)
            gallery_photos.append(dest_name)

        # Build gallery HTML
        gallery_html_parts = []
        for i, fname in enumerate(gallery_photos):
            gallery_html_parts.append(
                f'            <div data-idx="{i}">'
                f'<img loading="lazy" src="../assets/property-galleries/{slug}/{fname}" '
                f'alt="{addr} photo {i+1}"></div>'
            )
        photo_paths_json = json.dumps([f"../assets/property-galleries/{slug}/{f}" for f in gallery_photos])

        # Render detail page
        page_html = PAGE_TEMPLATE.format(
            slug=slug,
            addr=addr,
            city=city,
            state=state,
            state_full=state_full,
            hero_slug=hero_slug,
            asset_type=asset_type,
            asset_count_phrase="107",  # could be more nuanced
            state_count="15",
            gallery_html="\n".join(gallery_html_parts),
            photo_paths_json=photo_paths_json,
        )
        detail_path = DETAIL_DEST / f"{slug}.html"
        with open(detail_path, "w") as f:
            f.write(page_html)

        detail_pages_js[f"{addr}|{city}|{state}"] = slug
        print(f"  ✓ {slug}: {len(gallery_photos)} photos → property/{slug}.html")

    # Write SUMMIT_DETAIL_PAGES JS snippet
    snippet_path = WEB_ROOT / "phase4-detail-pages.js"
    with open(snippet_path, "w") as f:
        f.write("// Phase 4 detail pages — paste into properties.js after SUMMIT_HEROES\n")
        f.write("window.SUMMIT_DETAIL_PAGES = {\n")
        for key, slug in detail_pages_js.items():
            f.write(f'  "{key}": "{slug}",\n')
        f.write("};\n")

    # Update sitemap.xml
    sitemap_path = WEB_ROOT / "sitemap.xml"
    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '    <url><loc>https://teamsummitre.com/</loc><priority>1.0</priority></url>',
        '    <url><loc>https://teamsummitre.com/services.html</loc><priority>0.9</priority></url>',
        '    <url><loc>https://teamsummitre.com/properties.html</loc><priority>0.9</priority></url>',
        '    <url><loc>https://teamsummitre.com/team.html</loc><priority>0.7</priority></url>',
        '    <url><loc>https://teamsummitre.com/contact.html</loc><priority>0.8</priority></url>',
    ]
    for slug in detail_pages_js.values():
        sitemap_lines.append(
            f'    <url><loc>https://teamsummitre.com/property/{slug}.html</loc><priority>0.6</priority></url>'
        )
    sitemap_lines.append('</urlset>')
    with open(sitemap_path, "w") as f:
        f.write("\n".join(sitemap_lines) + "\n")

    print(f"\n  Generated {len(detail_pages_js)} detail pages")
    print(f"  JS snippet: {snippet_path}")
    print(f"  Sitemap updated with {len(detail_pages_js)} new URLs")


if __name__ == "__main__":
    main()
