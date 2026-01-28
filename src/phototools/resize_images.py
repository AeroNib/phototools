#!/usr/bin/env python3
"""
Web Image Resizer for Photo Gallery

This script processes all JPG files in the images_original/ folder and resizes them to
a maximum of 3000px in the longest dimension with 80% quality to reduce file size
for web display.

The script reads from images_original/ and writes the resized versions to images_resized/.

Usage:
    python3 resize_images.py
"""

from pathlib import Path

from PIL import Image

# Configuration
MAX_DIMENSION = 3000
QUALITY = 80
SOURCE_DIR = Path(__file__).parent / "images_original"
OUTPUT_DIR = Path(__file__).parent / "images_resized"


def resize_images(
    source_path, output_path, max_dimension=MAX_DIMENSION, quality=QUALITY
):
    """
    Resize an image to a maximum dimension while maintaining aspect ratio
    and reduce quality for web display. Properly handles EXIF orientation.

    Args:
        source_path: Path to the source image
        output_path: Path to save the resized image
        max_dimension: Maximum dimension in pixels (default: 3000)
        quality: JPG quality percentage (default: 80)
    """
    try:
        with Image.open(source_path) as img:
            # Apply EXIF orientation before processing
            # This rotates the image data to match the EXIF orientation tag
            img = img.copy()  # Make a copy to avoid modifying original during context

            # ImageOps.exif_transpose handles all EXIF orientation cases
            from PIL import ImageOps

            img = ImageOps.exif_transpose(img)

            if img is None:
                print(f"✗ Error: Could not process orientation for {source_path.name}")
                return

            # Get dimensions after orientation correction
            width, height = img.size
            max_original = max(width, height)

            # Check if resizing is needed
            if max_original <= max_dimension:
                # Still re-save with quality reduction
                img.save(output_path, quality=quality, optimize=True, exif=b"")
                print(f"✓ Optimized quality: {source_path.name}")
                print(f"  Size: {width}x{height} (no resize needed)")
                return

            # Calculate new dimensions maintaining aspect ratio
            if width > height:
                new_width = max_dimension
                new_height = int((height / width) * max_dimension)
            else:
                new_height = max_dimension
                new_width = int((width / height) * max_dimension)

            # Resize image
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Save with reduced quality, removing EXIF data (orientation already applied)
            img_resized.save(output_path, quality=quality, optimize=True, exif=b"")
            print(f"✓ Resized: {source_path.name}")
            print(f"  {width}x{height} → {new_width}x{new_height}")

    except Exception as e:
        print(f"✗ Error processing {source_path.name}: {e}")


def main():
    """Main function to process all images."""

    if not SOURCE_DIR.exists():
        print(f"Error: {SOURCE_DIR} does not exist")
        return

    # Find all JPG files (case-insensitive)
    image_files = []
    for ext in ["*.jpg", "*.jpeg", "*.JPG", "*.JPEG"]:
        image_files.extend(SOURCE_DIR.glob(ext))

    if not image_files:
        print(f"No JPG files found in {SOURCE_DIR}")
        return

    print(f"Found {len(image_files)} image(s) to process")
    print(f"Max dimension: {MAX_DIMENSION}px, Quality: {QUALITY}%")
    print(f"\nProcessing images from {SOURCE_DIR} to {OUTPUT_DIR}...\n")

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Process each image
    for source_path in sorted(image_files):
        # Create output path
        output_path = OUTPUT_DIR / source_path.name

        # Resize and optimize
        resize_images(source_path, output_path)
        print()

    print(f"Done! Processed {len(image_files)} image(s)")
    print(f"Resized images saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
