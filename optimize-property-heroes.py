#!/usr/bin/env python3
"""
Phase 2 — Per-property hero thumbnails for portfolio cards

Resizes a curated hero photo for each property and writes web-ready JPEGs
to /website/assets/property-heroes/.

Each property has a slug. The output filename matches that slug so the
website can map property → image deterministically.

Run:
    python3 optimize-property-heroes.py

Requires:
    - Python 3
    - Pillow:  pip3 install --user Pillow  (auto-installed if missing)
"""

import subprocess
import sys
from pathlib import Path

PHOTOS_SRC = Path("/Users/codyleivas/Library/CloudStorage/Dropbox-Personal/04_Business/Summit_Real_Estate_Services/Marketing/Brand_System/Photos")
WEB_DEST = Path("/Users/codyleivas/Library/CloudStorage/Dropbox-Personal/04_Business/Summit_Real_Estate_Services/Marketing/Brand_System/website/assets/property-heroes")

# slug, source path under Photos/, optional notes
# Slugs match the keys we'll add to properties.js
PROPERTY_HEROES = [
    # === Phase 2: Top 20 properties by photo count ===
    ("1115-cottonwood-hartland",
     "Wisconsin/1115 Cottonwood Avenue - Hartland/DJI_0001.JPG"),
    ("201-215-stag-industrial-stl",
     "Missouri/201-215 Stag Industrial Boulevard - St. Louis/DJI_0290.JPG"),
    ("6501-hall-street-stl",
     "Missouri/6501 Hall Street - St. Louis/DJI_0092 edit-1.jpg"),
    ("6601-parkway-circle-brooklyn-center",
     "Minnesota/6601 Parkway Circle - Brooklyn Center/DJI_0157.JPG"),
    ("9009-n-51st-brown-deer",
     "Wisconsin/9009 N 51st Street - Brown Deer/Exterior lot and docks.jpg"),
    ("8900-n-55th-brown-deer",
     "Wisconsin/8900 N. 55th Street - Brown Deer/Exterior lot and docks.jpg"),
    ("9600-w-76th-eden-prairie",
     "Minnesota/9600 West 76th Street - Eden Prairie/01_1.jpg"),
    ("9700-w-76th-eden-prairie",
     "Minnesota/9700 West 76th Street - Eden Prairie/01_1.jpg"),
    ("10120-w-76th-eden-prairie",
     "Minnesota/10120 West 76th Street - Eden Prairie/01_1.jpg"),
    ("4333-w-71st-indianapolis",
     "Indiana/4333 W. 71st Street - Indianapolis/DJI_0105.jpg"),
    ("1477-hoff-industrial-ofallon",
     "Missouri/1477 Hoff Industrial Drive - O'Fallon/DJI_0088 edit.jpg"),
    ("5450-stratum-fort-worth",
     "Texas/5450 Stratum Drive - Fort Worth/Front Entry.jpg"),
    ("3235-intertech-brookfield",
     "Wisconsin/3235 Intertech Drive - Brookfield/DJI_0161.JPG"),
    ("3275-intertech-brookfield",
     "Wisconsin/3275 Intertech Drive - Brookfield/DJI_0161.JPG"),
    ("7842-n-faulkner-milwaukee",
     "Wisconsin/7842 N. Faulkner Road - Milwaukee/1.jpg"),
    ("w141-n9501-fountain-menomonee-falls",
     "Wisconsin/W141 N9501 Fountain Boulevard - Menomonee Falls/Photo Apr 21, 10 42 05 AM.jpg"),
    ("4700-briar-cleveland",
     "Ohio/4700 Briar Road - Cleveland/1.jpg"),
    ("2-92-soccer-park-fenton",
     "Missouri/2-92 Soccer Park Drive - Fenton/101_7243.JPG"),  # may need swap
    ("1400-grant-industrial-ofallon",
     "Missouri/1400 Grant Industrial Drive - O'Fallon/DJI_0384.JPG"),
    ("1100-cottonwood-hartland",
     "Wisconsin/1100 Cottonwood Avenue - Hartland/DJI_0640.JPG"),

    # === Bonus heroes (Phase 1 brand shots also become per-property heroes) ===
    ("2327-chouteau-stl",
     "Missouri/2327 Chouteau Avenue - St. Louis/DJI_0012 EDIT.jpg"),
    ("2676-metro-maryland-heights",
     "Missouri/2676 Metro Boulevard - Maryland Heights/DJI_0027 - EDITED.jpg"),
    ("4710-earth-city-bridgeton",
     "Missouri/4710 Earth City Expressway - Bridgeton/DJI_0001.JPG"),
    ("1241-ambassador-stl",
     "Missouri/1241 Ambassador Boulevard - St. Louis/DJI_0313.JPG"),
    ("2462-2470-schuetz-maryland-heights",
     "Missouri/2462-2470 Schuetz Road - Maryland Heights/DJI_0288.JPG"),
    ("2662-metro-maryland-heights",
     "Missouri/2662 Metro Boulevard - Maryland Heights/DJI_0027 - EDITED.jpg"),
]

THUMB_WIDTH = 1000   # property cards display ~400-500px wide; 2x for retina
JPEG_QUALITY = 78


def ensure_pillow():
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        print("→ Installing Pillow (one time)...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user", "Pillow"],
            capture_output=True, text=True
        )
        return result.returncode == 0


def optimize(src, dest):
    from PIL import Image, ImageOps
    if not src.exists():
        print(f"  ✗ {dest.name} — source missing")
        return False, 0
    img = Image.open(src)
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB":
        img = img.convert("RGB")
    if img.width > THUMB_WIDTH:
        ratio = THUMB_WIDTH / img.width
        new_h = int(img.height * ratio)
        img = img.resize((THUMB_WIDTH, new_h), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    return True, dest.stat().st_size


def main():
    if not ensure_pillow():
        sys.exit(1)
    WEB_DEST.mkdir(parents=True, exist_ok=True)

    print(f"Optimizing {len(PROPERTY_HEROES)} property heroes →")
    print(f"  {WEB_DEST}")
    print()

    ok = 0
    total_bytes = 0
    for slug, rel_src in PROPERTY_HEROES:
        src = PHOTOS_SRC / rel_src
        dest = WEB_DEST / f"{slug}.jpg"
        success, size = optimize(src, dest)
        if success:
            ok += 1
            total_bytes += size
            kb = size / 1024
            print(f"  ✓ {slug}.jpg  ({kb:.0f}KB)")

    print()
    print("=" * 60)
    print(f"  {ok}/{len(PROPERTY_HEROES)} property heroes ready")
    print(f"  Total: {total_bytes / 1024 / 1024:.1f} MB")
    print("=" * 60)


if __name__ == "__main__":
    main()
