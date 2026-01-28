#!/usr/bin/env python3
"""
Image Renamer for Photo Gallery

This script renames all JPG files in the current directory using their EXIF timestamp
converted to UTC datetime plus 4 random hex characters to avoid collisions.

Format: {YYYYMMDD-HHMMSS}-{4hex}.jpg
Example: 20240123-143000-a3f5.jpg

Usage:
    without installing:
        python3 rename_images.py

    installed as a pipx package:
        rename_images
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image
from PIL.ExifTags import TAGS

# Configuration
IMAGES_DIR = Path.cwd()


def get_exif_datetime(image_path):
    """
    Extract the datetime from EXIF data.

    Args:
        image_path: Path to the image file

    Returns:
        datetime object or None if not found
    """
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()

            if not exif_data:
                return None

            # Look for DateTimeOriginal (when photo was taken)
            # Fall back to DateTime if not found
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)

                if tag_name == "DateTimeOriginal" or tag_name == "DateTime":
                    # EXIF datetime format: "2024:01:23 14:30:00"
                    dt = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    return dt

            return None

    except Exception as e:
        print(f"  Warning: Could not read EXIF from {image_path.name}: {e}")
        return None


def generate_random_hex(length=4):
    """Generate random hex characters."""
    return secrets.token_hex(length // 2)


def rename_image(image_path):
    """
    Rename an image file based on its EXIF timestamp.

    Args:
        image_path: Path to the image file

    Returns:
        True if renamed, False if skipped
    """
    # Get EXIF datetime
    dt = get_exif_datetime(image_path)

    if not dt:
        print(f"✗ Skipped: {image_path.name} (no EXIF datetime found)")
        return False

    # Convert to UTC datetime
    # EXIF datetime is in EST (UTC-5), convert to UTC
    est = timezone(timedelta(hours=-5))
    dt_est = dt.replace(tzinfo=est)
    dt_utc = dt_est.astimezone(timezone.utc)

    # Format as YYYYMMDD-HHMMSS
    utc_timestamp = dt_utc.strftime("%Y%m%d-%H%M%S")

    # Generate random hex suffix
    hex_suffix = generate_random_hex()

    # Create new filename
    new_name = f"{utc_timestamp}-{hex_suffix}{image_path.suffix.lower()}"
    new_path = image_path.parent / new_name

    # Check for collision (extremely unlikely but handle it)
    while new_path.exists():
        hex_suffix = generate_random_hex()
        new_name = f"{utc_timestamp}-{hex_suffix}{image_path.suffix.lower()}"
        new_path = image_path.parent / new_name

    # Rename the file
    try:
        image_path.rename(new_path)
        dt_str_est = dt.strftime("%Y-%m-%d %H:%M:%S EST")
        dt_str_utc = dt_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
        print(f"✓ Renamed: {image_path.name}")
        print(f"       to: {new_name}")
        print(f"          ({dt_str_est} → {dt_str_utc})")
        return True
    except Exception as e:
        print(f"✗ Error renaming {image_path.name}: {e}")
        return False


def main():
    """Main function to process all images."""

    # Find all JPG files (case-insensitive)
    image_files = []
    for ext in ["*.jpg", "*.jpeg", "*.JPG", "*.JPEG"]:
        image_files.extend(IMAGES_DIR.glob(ext))

    # Filter out files that already match the pattern (YYYYMMDD-HHMMSS-hex.jpg)
    import re

    pattern = re.compile(r"^\d{8}-\d{6}-[0-9a-f]{4}\.(jpg|jpeg)$", re.IGNORECASE)
    files_to_process = [f for f in image_files if not pattern.match(f.name)]

    if not files_to_process:
        print(
            "No images to rename (all files already have timestamp names or no JPG files found)"
        )
        return

    print(f"Found {len(files_to_process)} image(s) to rename\n")

    renamed_count = 0
    for image_path in sorted(files_to_process):
        if rename_image(image_path):
            renamed_count += 1
        print()

    print(f"Done! Renamed {renamed_count} of {len(files_to_process)} image(s)")


if __name__ == "__main__":
    main()
