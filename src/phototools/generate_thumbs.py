#!/usr/bin/env python3
"""
Thumbnail Generator for Photo Gallery

This script processes all JPG files in the images/ folder and generates
200px tall thumbnails in the thumbs/ folder.

Usage:
    python3 generate_thumbs.py
"""

from pathlib import Path

from PIL import Image

# Configuration
THUMBNAIL_HEIGHT = 200
SOURCE_DIR = Path(__file__).parent / "images_original"
THUMBS_DIR = Path(__file__).parent / "images_thumbs"


def generate_thumbnail(image_path, thumb_path, height=THUMBNAIL_HEIGHT):
    """
    Generate a thumbnail from an image with the specified height,
    maintaining aspect ratio.

    Args:
        image_path: Path to the source image
        thumb_path: Path where thumbnail will be saved
        height: Target height in pixels (default: 200)
    """
    try:
        with Image.open(image_path) as img:
            # Calculate new width to maintain aspect ratio
            aspect_ratio = img.width / img.height
            new_width = int(height * aspect_ratio)

            # Resize image
            img_resized = img.resize((new_width, height), Image.Resampling.LANCZOS)

            # Save thumbnail
            img_resized.save(thumb_path, quality=85, optimize=True)
            print(f"✓ Generated: {thumb_path.name}")

    except Exception as e:
        print(f"✗ Error processing {image_path.name}: {e}")


def main():
    """Main function to process all images."""

    # Ensure directories exist
    SOURCE_DIR.mkdir(exist_ok=True)
    THUMBS_DIR.mkdir(exist_ok=True)

    # Find all JPG files (case-insensitive)
    image_files = []
    for ext in ["*.jpg", "*.jpeg", "*.JPG", "*.JPEG"]:
        image_files.extend(SOURCE_DIR.glob(ext))

    if not image_files:
        print(f"No JPG files found in {SOURCE_DIR}")
        return

    print(f"Found {len(image_files)} image(s) to process\n")

    # Process each image
    for image_path in sorted(image_files):
        thumb_path = THUMBS_DIR / image_path.name

        # Skip if thumbnail already exists
        if thumb_path.exists():
            print(f"○ Skipped: {image_path.name} (thumbnail exists)")
            continue

        generate_thumbnail(image_path, thumb_path)

    print("\nDone!")


if __name__ == "__main__":
    main()
