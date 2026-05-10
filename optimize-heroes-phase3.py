#!/usr/bin/env python3
"""
Phase 3 — Auto-pick + optimize heroes for the remaining ~56 properties.

Walks /Brand_System/Photos/[State]/[Property]/, scores each file with a
heuristic (drone + exterior bias, anti-roof/interior/damage), picks the
top-scoring image, resizes to 1000px wide, writes to /assets/property-heroes/.

Run:
    python3 optimize-heroes-phase3.py

Outputs:
    - JPEGs in website/assets/property-heroes/
    - phase3-heroes.js snippet with SUMMIT_HEROES additions to copy-paste
"""

import os
import re
import subprocess
import sys
from pathlib import Path

PHOTOS_SRC = Path("/Users/codyleivas/Library/CloudStorage/Dropbox-Personal/04_Business/Summit_Real_Estate_Services/Marketing/Brand_System/Photos")
WEB_DEST = Path("/Users/codyleivas/Library/CloudStorage/Dropbox-Personal/04_Business/Summit_Real_Estate_Services/Marketing/Brand_System/website/assets/property-heroes")

# Properties already covered by Phase 1 + Phase 2 — skip these
# Keyed by (address, city, state) tuples so slug differences don't matter
ALREADY_COVERED_KEYS = {
    ("1115 Cottonwood Avenue", "Hartland", "WI"),
    ("201-215 Stag Industrial Boulevard", "St. Louis", "MO"),
    ("6501 Hall Street", "St. Louis", "MO"),
    ("6601 Parkway Circle", "Brooklyn Center", "MN"),
    ("9009 N 51st Street", "Brown Deer", "WI"),
    ("8900 N. 55th Street", "Brown Deer", "WI"),
    ("9600 West 76th Street", "Eden Prairie", "MN"),
    ("9700 West 76th Street", "Eden Prairie", "MN"),
    ("10120 West 76th Street", "Eden Prairie", "MN"),
    ("4333 W. 71st Street", "Indianapolis", "IN"),
    ("1477 Hoff Industrial Drive", "O'Fallon", "MO"),
    ("5450 Stratum Drive", "Fort Worth", "TX"),
    ("3235 Intertech Drive", "Brookfield", "WI"),
    ("3275 Intertech Drive", "Brookfield", "WI"),
    ("7842 N. Faulkner Road", "Milwaukee", "WI"),
    ("W141 N9501 Fountain Boulevard", "Menomonee Falls", "WI"),
    ("4700 Briar Road", "Cleveland", "OH"),
    ("2-92 Soccer Park Drive", "Fenton", "MO"),
    ("1400 Grant Industrial Drive", "O'Fallon", "MO"),
    ("1100 Cottonwood Avenue", "Hartland", "WI"),
    ("2327 Chouteau Avenue", "St. Louis", "MO"),
    ("2676 Metro Boulevard", "Maryland Heights", "MO"),
    ("4710 Earth City Expressway", "Bridgeton", "MO"),
    ("1241 Ambassador Boulevard", "St. Louis", "MO"),
    ("2462-2470 Schuetz Road", "Maryland Heights", "MO"),
    ("2662 Metro Boulevard", "Maryland Heights", "MO"),
}

# All 107 properties — same list as the website
PROPERTIES = [
    # WI
    ("16150 W. Lincoln Avenue", "New Berlin", "WI"),
    ("1100 Cottonwood Avenue", "Hartland", "WI"),
    ("1115 Cottonwood Avenue", "Hartland", "WI"),
    ("16700 W. Lincoln Avenue", "New Berlin", "WI"),
    ("17080 Pheasant Drive", "Brookfield", "WI"),
    ("9009 N 51st Street", "Brown Deer", "WI"),
    ("1505 Arcadian Avenue", "Waukesha", "WI"),
    ("16540 W Rogers Drive", "New Berlin", "WI"),
    ("1822 Dolphin Drive", "Waukesha", "WI"),
    ("3200 S 166th Street", "New Berlin", "WI"),
    ("2101 W. Camden Road", "Glendale", "WI"),
    ("N8W22323 Johnson Drive", "Waukesha", "WI"),
    ("3000-3080 S Calhoun Road", "New Berlin", "WI"),
    ("N16W23120 Stone Ridge Drive", "Waukesha", "WI"),
    ("W184 S8204 Gemini Court", "Muskego", "WI"),
    ("3015 S. 163rd St", "New Berlin", "WI"),
    ("N56 W16665 Ridgewood Drive", "Menomonee Falls", "WI"),
    ("3100 W. Mill Road", "Milwaukee", "WI"),
    ("N89 W14260 Patrita Drive", "Menomonee Falls", "WI"),
    ("3235 Intertech Drive", "Brookfield", "WI"),
    ("4450 Robertson Road", "Madison", "WI"),
    ("3275 Intertech Drive", "Brookfield", "WI"),
    ("N117 W18546 Fulton Drive", "Germantown", "WI"),
    ("6724 S. 13th Street", "Oak Creek", "WI"),
    ("S82 W19275 Apollo Drive", "Muskego", "WI"),
    ("7842 N. Faulkner Road", "Milwaukee", "WI"),
    ("W129 N10880 Washington Drive", "Germantown", "WI"),
    ("8300 W. Sleske Court", "Milwaukee", "WI"),
    ("W141 N9501 Fountain Boulevard", "Menomonee Falls", "WI"),
    ("8900 N. 55th Street", "Brown Deer", "WI"),
    ("S17W22650 Lincoln Avenue", "Waukesha", "WI"),
    ("11220 Lincoln Avenue", "West Allis", "WI"),
    # MO
    ("2-92 Soccer Park Drive", "Fenton", "MO"),
    ("2676 Metro Boulevard", "Maryland Heights", "MO"),
    ("1400 Grant Industrial Drive", "O'Fallon", "MO"),
    ("1285 West Terra Lane", "O'Fallon", "MO"),
    ("4710 Earth City Expressway", "Bridgeton", "MO"),
    ("201-215 Stag Industrial Boulevard", "St. Louis", "MO"),
    ("290-292 Hanley Industrial Boulevard", "Brentwood", "MO"),
    ("5422 Eagle Industrial Drive", "Hazelwood", "MO"),
    ("6501 Hall Street", "St. Louis", "MO"),
    ("1626 Manufacturers Drive", "Fenton", "MO"),
    ("770 Merus Court", "Fenton", "MO"),
    ("3905 Ventures Way", "Earth City", "MO"),
    ("820-860 Hanley Industrial Boulevard", "Brentwood", "MO"),
    ("9415 Dielman Rock Island Industrial Drive", "Olivette", "MO"),
    ("157-165 Compass Pointe Drive", "St. Charles", "MO"),
    ("4615 West Chestnut Expressway", "Springfield", "MO"),
    ("2462-2470 Schuetz Road", "Maryland Heights", "MO"),
    ("10601-10605 Trenton Avenue", "St. Louis", "MO"),
    ("10935 Manchester Road", "St. Louis", "MO"),
    ("1241 Ambassador Boulevard", "St. Louis", "MO"),
    ("10875 Indian Head Industrial Boulevard", "St. Louis", "MO"),
    ("1300 Grant Industrial Drive", "O'Fallon", "MO"),
    ("13500 NW Industrial Drive", "Bridgeton", "MO"),
    ("1326-1336 Strassner", "Brentwood", "MO"),
    ("13695 Rider Trail N", "Earth City", "MO"),
    ("1477 Hoff Industrial Drive", "O'Fallon", "MO"),
    ("13750 Rider Trail N", "Earth City", "MO"),
    ("2327 Chouteau Avenue", "St. Louis", "MO"),
    ("4132 Shoreline Drive", "Earth City", "MO"),
    ("2662 Metro Boulevard", "Maryland Heights", "MO"),
    ("12926 Hollenberg Drive", "Bridgeton", "MO"),
    # MN
    ("7760-7716 Golden Triangle Drive", "Eden Prairie", "MN"),
    ("2405 Xenium Lane N", "Plymouth", "MN"),
    ("801 West 106th Street", "Minneapolis", "MN"),
    ("2100 Fernbrook Lane N", "Plymouth", "MN"),
    ("6601 Parkway Circle", "Brooklyn Center", "MN"),
    ("1302 S 5th Street", "Hopkins", "MN"),
    ("9600 West 76th Street", "Eden Prairie", "MN"),
    ("2915 Niagara Lane N", "Plymouth", "MN"),
    ("9700 West 76th Street", "Eden Prairie", "MN"),
    ("2521 E Hennepin Avenue", "Minneapolis", "MN"),
    ("10120 West 76th Street", "Eden Prairie", "MN"),
    ("25 Cliff Road W", "Burnsville", "MN"),
    ("1000 Spiral Boulevard", "Hastings", "MN"),
    ("5701-5749 International Parkway", "New Hope", "MN"),
    ("321 Hoover Street NE", "Minneapolis", "MN"),
    ("9401 73rd Avenue N", "Minneapolis", "MN"),
    # GA
    ("5530 E. Ponce de Leon Ave", "Stone Mountain", "GA"),
    ("931 Main Street", "Forest Park", "GA"),
    ("1543 Gordon Hwy", "Augusta", "GA"),
    ("356 Walnut Street", "Macon", "GA"),
    ("4100 14th Avenue", "Columbus", "GA"),
    ("1231 Green Street SE", "Conyers", "GA"),
    ("1805 Enterprise Drive", "Buford", "GA"),
    # IN
    ("3001 Hamburg Pike", "Jeffersonville", "IN"),
    ("1601 Research Drive", "Jeffersonville", "IN"),
    ("4333 W. 71st Street", "Indianapolis", "IN"),
    ("6205 Morenci Trail", "Indianapolis", "IN"),
    # AZ
    ("2922 S. Roosevelt", "Tempe", "AZ"),
    ("15950 N. 76th Street", "Scottsdale", "AZ"),
    # UT
    ("2150 Technology Parkway", "West Valley", "UT"),
    ("2431 South 1070 West", "West Valley", "UT"),
    ("114 S 850 East", "Lehi", "UT"),
    # OH
    ("4700 Briar Road", "Cleveland", "OH"),
    ("5915 Jason Street", "Toledo", "OH"),
    ("5161 Wolfpen Pleasant Hill Rd", "Milford", "OH"),
    # PA
    ("723 Electronic Drive", "Horsham", "PA"),
    ("50 Commerce Drive", "Wyomissing", "PA"),
    # TX
    ("5450 Stratum Drive", "Fort Worth", "TX"),
    ("2916 Montropolis Drive", "Austin", "TX"),
    # VA
    ("3941 Deep Rock Road", "Richmond", "VA"),
    # IL
    ("303 Homer Adams Parkway", "Alton", "IL"),
    # AR
    ("11710 Vimy Ridge Road", "Alexander", "AR"),
    # KY
    ("4810-4852 Crittenden Drive", "Louisville", "KY"),
    # TN
    ("3551 Workman Road", "Knoxville", "TN"),
]

STATE_NAMES = {
    "WI": "Wisconsin", "MO": "Missouri", "MN": "Minnesota", "IN": "Indiana",
    "GA": "Georgia",  "AZ": "Arizona",  "UT": "Utah",      "OH": "Ohio",
    "PA": "Pennsylvania", "TX": "Texas", "VA": "Virginia", "IL": "Illinois",
    "AR": "Arkansas", "KY": "Kentucky", "TN": "Tennessee"
}

# Heuristic scoring for picking the best hero candidate
GOOD_KEYWORDS = ["exterior", "aerial", "front", "outside", "drone", "building"]
BAD_KEYWORDS = [
    "interior", "inside", "roof", "leak", "damage", "broken", "repair",
    "warning", "before", "issue", "problem", "lippert tile", "asphalt",
    "construction", "demo", "thumbnail", "screenshot", "screen shot",
    "pdf", "map", "diagram", "drawing", "plan", "drivers license", "dl",
    "id card", "headshot", "logo", "brochure", "edit bw"
]
ALLOWED_EXT = {".jpg", ".jpeg", ".png"}


def slug_for(addr, city):
    s = (addr + " " + city).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    s = s.replace("-avenue", "").replace("-street", "").replace("-drive", "")
    s = s.replace("-road", "").replace("-court", "").replace("-boulevard", "-blvd")
    s = s.replace("-parkway", "").replace("-pike", "")
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def score_file(fpath):
    name = fpath.name.lower()
    size = fpath.stat().st_size
    score = 0

    # Bad keywords are disqualifying
    for bad in BAD_KEYWORDS:
        if bad in name:
            return -1000
    # Drone files are best
    if name.startswith("dji"):
        score += 200
    # Edited versions of files (DJI_xxxx EDIT, DJI_xxxx edit) are usually polished
    if " edit" in name or "-edit" in name or "edited" in name:
        score += 50
    # Good keywords
    for good in GOOD_KEYWORDS:
        if good in name:
            score += 30
    # Resolution / file size proxy
    if size > 4_000_000:
        score += 40
    elif size > 1_500_000:
        score += 20
    elif size > 500_000:
        score += 5
    elif size < 100_000:
        score -= 30  # likely thumbnail
    # Penalize the duplicate variants ("-1", "-2") slightly so we prefer originals
    if re.search(r"-\d+\.[a-z]+$", name):
        score -= 1
    return score


def find_best_hero(state_full, addr, city):
    folder_name = f"{addr} - {city}".replace(":", "").replace("/", "-")
    folder = PHOTOS_SRC / state_full / folder_name
    if not folder.exists():
        return None
    candidates = []
    for f in folder.iterdir():
        if not f.is_file():
            continue
        if f.suffix.lower() not in ALLOWED_EXT:
            continue
        s = score_file(f)
        if s > 0:
            candidates.append((s, f))
    if not candidates:
        return None
    candidates.sort(key=lambda x: -x[0])
    return candidates[0][1]


def ensure_pillow():
    try:
        import PIL  # noqa
        return True
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--user", "--break-system-packages", "Pillow"],
                       capture_output=True)
        try:
            import PIL  # noqa
            return True
        except ImportError:
            return False


THUMB_WIDTH = 1000
JPEG_QUALITY = 78


def optimize(src, dest):
    from PIL import Image, ImageOps
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
    return dest.stat().st_size


def main():
    if not ensure_pillow():
        print("Could not install Pillow. Run: python3 -m pip install --user --break-system-packages Pillow")
        sys.exit(1)
    WEB_DEST.mkdir(parents=True, exist_ok=True)

    print(f"Phase 3 hero auto-picker")
    print(f"Source: {PHOTOS_SRC}")
    print(f"Dest:   {WEB_DEST}")
    print()

    new_heroes = {}  # key -> slug
    skipped_already = 0
    skipped_no_photos = 0
    no_good_candidate = []

    for addr, city, state in PROPERTIES:
        if (addr, city, state) in ALREADY_COVERED_KEYS:
            skipped_already += 1
            continue
        slug = slug_for(addr, city)
        state_full = STATE_NAMES[state]
        best = find_best_hero(state_full, addr, city)
        if best is None:
            # Check if folder exists but no good candidates
            folder = PHOTOS_SRC / state_full / f"{addr} - {city}".replace(":", "").replace("/", "-")
            if folder.exists() and any(folder.iterdir()):
                no_good_candidate.append((addr, city, state))
            else:
                skipped_no_photos += 1
            continue

        dest = WEB_DEST / f"{slug}.jpg"
        size = optimize(best, dest)
        new_heroes[f"{addr}|{city}|{state}"] = slug
        kb = size / 1024
        print(f"  ✓ {slug}.jpg  ({kb:.0f}KB)  ← {best.name}")

    # Write JS snippet to add to properties.js
    snippet_path = Path("/Users/codyleivas/Library/CloudStorage/Dropbox-Personal/04_Business/Summit_Real_Estate_Services/Marketing/Brand_System/website/phase3-heroes.js")
    with open(snippet_path, "w") as f:
        f.write("// Phase 3 auto-picked heroes — paste into SUMMIT_HEROES in assets/properties.js\n")
        for key, slug in new_heroes.items():
            f.write(f'  "{key}": "{slug}",\n')

    print()
    print("=" * 60)
    print(f"  Already covered (Phase 1+2):     {skipped_already}")
    print(f"  Newly optimized (Phase 3):        {len(new_heroes)}")
    print(f"  No source photos available:       {skipped_no_photos}")
    print(f"  Source has files but no good pick: {len(no_good_candidate)}")
    print("=" * 60)
    if no_good_candidate:
        print("\nProperties with photos but no qualifying hero (consider manual pick):")
        for addr, city, state in no_good_candidate:
            print(f"  · [{state}] {addr} — {city}")
    print(f"\nJS snippet for properties.js: {snippet_path}")


if __name__ == "__main__":
    main()
