#!/usr/bin/env python3
"""
Phase 1 — Brand hero imagery optimization

Reads 8 curated drone photos + 1 hero video from /Brand_System/Photos/,
optimizes them for web (resize, compress, strip EXIF), and writes them to
/website/assets/photos/.

Run:
    python3 optimize-hero-photos.py

Requires:
    - Python 3 (built-in on macOS)
    - Pillow:  pip3 install --user Pillow   (auto-installed if missing)
    - ffmpeg:  brew install ffmpeg          (only needed for the hero video)
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

PHOTOS_SRC = Path("/Users/codyleivas/Library/CloudStorage/Dropbox-Personal/04_Business/Summit_Real_Estate_Services/Marketing/Brand_System/Photos")
WEB_DEST = Path("/Users/codyleivas/Library/CloudStorage/Dropbox-Personal/04_Business/Summit_Real_Estate_Services/Marketing/Brand_System/website/assets/photos")

# Final curated 8 brand hero photos — these will become the visual identity of the site
HERO_PHOTOS = [
    # filename in destination, source path, alt text, role
    ("hero-stl-skyline.jpg",
     "Missouri/2327 Chouteau Avenue - St. Louis/DJI_0012 EDIT.jpg",
     "Aerial view of Summit-managed industrial corridor with St. Louis skyline",
     "primary-hero"),
    ("hero-hall-street-distribution.jpg",
     "Missouri/6501 Hall Street - St. Louis/DJI_0092 edit-1.jpg",
     "Distribution facility with loading docks and tractor-trailers",
     "distribution"),
    ("hero-stag-industrial.jpg",
     "Missouri/201-215 Stag Industrial Boulevard - St. Louis/DJI_0290.JPG",
     "Multi-tenant industrial flex buildings with white roofs",
     "multi-tenant"),
    ("hero-metro-blvd-fall.jpg",
     "Missouri/2676 Metro Boulevard - Maryland Heights/DJI_0027 - EDITED.jpg",
     "Industrial buildings with autumn foliage in Maryland Heights",
     "fall-context"),
    ("hero-cottonwood-wisconsin.jpg",
     "Wisconsin/1100 Cottonwood Avenue - Hartland/DJI_0640.JPG",
     "Industrial building with fleet vehicles in Hartland Wisconsin",
     "wisconsin"),
    ("hero-brooklyn-center-winter.jpg",
     "Minnesota/6601 Parkway Circle - Brooklyn Center/DJI_0157.JPG",
     "Snow-covered industrial property in Brooklyn Center Minnesota",
     "minnesota-winter"),
    ("hero-indianapolis-warehouse.jpg",
     "Indiana/4333 W. 71st Street - Indianapolis/DJI_0105.jpg",
     "Large warehouse with trucks and rail access in Indianapolis",
     "warehouse"),
    ("hero-earth-city-modern.jpg",
     "Missouri/4710 Earth City Expressway - Bridgeton/DJI_0001.JPG",
     "Modern industrial-office building under dramatic sky in Earth City",
     "modern"),
]

HERO_VIDEO = {
    "dest": "hero-flyover.mp4",
    "src": "Missouri/201-215 Stag Industrial Boulevard - St. Louis/DJI_0329.MP4",
    "duration_seconds": 12,
    "start_seconds": 2,  # skip the takeoff/initial frames
}

MAX_WIDTH = 1920   # plenty for full-bleed hero on 4K screens; quality 80 keeps size ~250-400KB
JPEG_QUALITY = 82


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
        if result.returncode != 0:
            print(f"  Pip install failed: {result.stderr}")
            return False
        return True


def optimize_image(src, dest, alt):
    from PIL import Image, ImageOps

    if not src.exists():
        print(f"  ✗ source missing: {src.relative_to(PHOTOS_SRC)}")
        return False

    img = Image.open(src)
    img = ImageOps.exif_transpose(img)  # respect orientation
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Resize maintaining aspect ratio
    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        new_h = int(img.height * ratio)
        img = img.resize((MAX_WIDTH, new_h), Image.LANCZOS)

    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)

    src_kb = src.stat().st_size / 1024
    dest_kb = dest.stat().st_size / 1024
    print(f"  ✓ {dest.name}  ({src_kb:.0f}KB → {dest_kb:.0f}KB, {img.width}×{img.height})")
    return True


def have_ffmpeg():
    return shutil.which("ffmpeg") is not None


def optimize_video(src_path, dest_path, start, duration):
    """Trim, resize, mute, transcode to web-friendly H.264 MP4."""
    if not src_path.exists():
        print(f"  ✗ video source missing: {src_path}")
        return False
    if not have_ffmpeg():
        print(f"  ⚠ ffmpeg not installed — skipping video.")
        print(f"     Install with: brew install ffmpeg")
        print(f"     Then run this script again.")
        return False

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", str(src_path),
        "-t", str(duration),
        "-vf", "scale=1280:-2",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "26",
        "-pix_fmt", "yuv420p",
        "-an",                    # strip audio
        "-movflags", "+faststart",
        str(dest_path),
    ]
    print(f"  → ffmpeg transcoding (this takes a minute)...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ ffmpeg failed: {result.stderr[-500:]}")
        return False
    src_mb = src_path.stat().st_size / 1024 / 1024
    dest_mb = dest_path.stat().st_size / 1024 / 1024
    print(f"  ✓ {dest_path.name}  ({src_mb:.0f}MB → {dest_mb:.1f}MB)")
    return True


def main():
    if not ensure_pillow():
        sys.exit(1)

    WEB_DEST.mkdir(parents=True, exist_ok=True)
    print(f"→ Source:      {PHOTOS_SRC}")
    print(f"→ Destination: {WEB_DEST}")
    print()
    print(f"Optimizing {len(HERO_PHOTOS)} hero photos:")

    ok_count = 0
    for dest_name, rel_src, alt, role in HERO_PHOTOS:
        src = PHOTOS_SRC / rel_src
        dest = WEB_DEST / dest_name
        if optimize_image(src, dest, alt):
            ok_count += 1

    print()
    print(f"Hero video:")
    src = PHOTOS_SRC / HERO_VIDEO["src"]
    dest = WEB_DEST / HERO_VIDEO["dest"]
    optimize_video(src, dest, HERO_VIDEO["start_seconds"], HERO_VIDEO["duration_seconds"])

    print()
    print("=" * 60)
    print(f"  {ok_count}/{len(HERO_PHOTOS)} photos optimized")
    total = sum(p.stat().st_size for p in WEB_DEST.glob("*") if p.is_file())
    print(f"  Total size in {WEB_DEST.name}/: {total / 1024 / 1024:.1f} MB")
    print("=" * 60)
    print()
    print("Next: I'll wire these into the website CSS and HTML.")


if __name__ == "__main__":
    main()
