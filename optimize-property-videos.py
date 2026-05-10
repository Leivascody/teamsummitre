#!/usr/bin/env python3
"""
Phase 5 — Drone video clips on marquee property detail pages

For each marquee property with DJI drone footage:
  1. Transcode raw 300-750MB DJI MP4 to web-friendly ~5-8MB clip
     (1280x720, H.264 CRF 26, 15-second loop, audio stripped, faststart)
  2. Save to /assets/property-videos/<slug>.mp4
  3. Inject a <section class="video-section"> into the corresponding
     /property/<slug>.html (idempotent — won't duplicate)

Run:
    python3 optimize-property-videos.py

Requires:
    - ffmpeg:  brew install ffmpeg
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

PHOTOS_SRC = Path("/Users/codyleivas/Library/CloudStorage/Dropbox-Personal/04_Business/Summit_Real_Estate_Services/Marketing/Brand_System/Photos")
VIDEO_DEST = Path("/Users/codyleivas/Library/CloudStorage/Dropbox-Personal/04_Business/Summit_Real_Estate_Services/Marketing/Brand_System/website/assets/property-videos")
DETAIL_DIR = Path("/Users/codyleivas/Library/CloudStorage/Dropbox-Personal/04_Business/Summit_Real_Estate_Services/Marketing/Brand_System/website/property")

# (slug, source_relative_path, addr, city)
VIDEOS = [
    ("stag-industrial-stl",
     "Missouri/201-215 Stag Industrial Boulevard - St. Louis/DJI_0329.MP4",
     "201-215 Stag Industrial Boulevard", "St. Louis"),
    ("parkway-circle-brooklyn-center",
     "Minnesota/6601 Parkway Circle - Brooklyn Center/DJI_0189.MP4",
     "6601 Parkway Circle", "Brooklyn Center"),
    ("1115-cottonwood-hartland",
     "Wisconsin/1115 Cottonwood Avenue - Hartland/DJI_0662.MP4",
     "1115 Cottonwood Avenue", "Hartland"),
    ("1100-cottonwood-hartland",
     "Wisconsin/1100 Cottonwood Avenue - Hartland/DJI_0661.MP4",
     "1100 Cottonwood Avenue", "Hartland"),
    ("grant-industrial-ofallon",
     "Missouri/1400 Grant Industrial Drive - O'Fallon/DJI_0383.MP4",
     "1400 Grant Industrial Drive", "O'Fallon"),
]

START_SECONDS = 2     # skip takeoff
DURATION_SECONDS = 18  # short loop
SCALE = "1280:-2"
CRF = "26"


def have_ffmpeg():
    return shutil.which("ffmpeg") is not None


def transcode(src, dest):
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(START_SECONDS),
        "-i", str(src),
        "-t", str(DURATION_SECONDS),
        "-vf", f"scale={SCALE}",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", CRF,
        "-pix_fmt", "yuv420p",
        "-an",
        "-movflags", "+faststart",
        str(dest),
    ]
    print(f"  → ffmpeg {dest.name} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr[-500:] if result.returncode else ""


VIDEO_SECTION_TEMPLATE = """
<!-- video-section -->
<section class="video-section">
    <div class="container">
        <span class="summit-eyebrow">Aerial Footage</span>
        <h2>{addr}, {city}.</h2>
        <div class="video-wrap">
            <video autoplay muted loop playsinline preload="metadata">
                <source src="../assets/property-videos/{slug}.mp4" type="video/mp4">
            </video>
        </div>
    </div>
</section>
"""


def inject_video_section(slug, addr, city):
    """Inject video section into the property detail HTML before the gallery section.
    Idempotent: skips if already injected (look for <!-- video-section --> marker)."""
    page = DETAIL_DIR / f"{slug}.html"
    if not page.exists():
        print(f"  ⚠ {slug}.html not found — skipping HTML inject")
        return False
    content = page.read_text()
    if "<!-- video-section -->" in content:
        # Already injected — replace existing block
        content = re.sub(
            r"\n*<!-- video-section -->.*?</section>\n*",
            "\n",
            content,
            count=1,
            flags=re.DOTALL,
        )
    # Inject before <section class="section surface-paper"> (the gallery section)
    block = VIDEO_SECTION_TEMPLATE.format(addr=addr, city=city, slug=slug)
    new_content = content.replace(
        '<section class="section surface-paper">',
        block + '<section class="section surface-paper">',
        1,
    )
    if new_content == content:
        print(f"  ⚠ Could not find gallery section in {slug}.html — no inject")
        return False
    page.write_text(new_content)
    return True


def main():
    if not have_ffmpeg():
        print("ffmpeg not installed. Install with: brew install ffmpeg")
        print("Then re-run this script.")
        sys.exit(1)
    VIDEO_DEST.mkdir(parents=True, exist_ok=True)

    print(f"Phase 5 — Drone video clips\n")
    print(f"Source: {PHOTOS_SRC}")
    print(f"Dest:   {VIDEO_DEST}\n")

    ok = 0
    for slug, rel_src, addr, city in VIDEOS:
        src = PHOTOS_SRC / rel_src
        dest = VIDEO_DEST / f"{slug}.mp4"
        if not src.exists():
            print(f"  ✗ source missing: {rel_src}")
            continue
        # Skip transcoding if dest exists (idempotent)
        if dest.exists():
            print(f"  · {dest.name} already exists, skipping transcode ({dest.stat().st_size/1024/1024:.1f}MB)")
        else:
            success, err = transcode(src, dest)
            if not success:
                print(f"  ✗ transcode failed for {slug}: {err}")
                continue
            mb = dest.stat().st_size / 1024 / 1024
            print(f"  ✓ {dest.name} ({mb:.1f}MB)")

        if inject_video_section(slug, addr, city):
            print(f"     → embedded in property/{slug}.html")
            ok += 1

    print()
    print("=" * 60)
    print(f"  {ok}/{len(VIDEOS)} property videos ready and embedded")
    print("=" * 60)


if __name__ == "__main__":
    main()
