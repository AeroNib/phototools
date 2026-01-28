#!/usr/bin/env python3
#
# This CLI utility processes all JPG files in a directory and resizes them to
# a maximum dimension with adjustable quality to reduce file size for web display.

import argparse
from pathlib import Path

from PIL import Image

# Default configuration
DEFAULT_MAX_PIXELS = 3000  # Default max JPG dimension (longest edge) in pixels
DEFAULT_QUALITY = 80  # Default JPG quality percentage
DEFAULT_OUTPUT_DIR = "resized"


def resize(
    source_path,  # Path to the source image
    output_path,  # Path to save the resized image
    max_pixels,  # Max output height or width in pixels
    quality,  # Output JPG quality percentage
):
    try:
        with Image.open(source_path) as img:
            # Make a copy to avoid modifying original during context
            img = img.copy()

            # ImageOps.exif_transpose handles all EXIF orientation cases
            from PIL import ImageOps

            # Bakes image orientation into image by rotating to match EXIF orientation
            img = ImageOps.exif_transpose(img)

            if img is None:
                print(f"✗ Error: Could not process orientation for {source_path.name}")
                return

            width, height = img.size
            max_original = max(width, height)

            if max_original <= max_pixels:
                # Still re-save with quality reduction, removing EXIF data
                img.save(output_path, quality=quality, optimize=True, exif=b"")
                print(f"✓ Optimized quality: {source_path.name}")
                print(f"  Size: {width}x{height} (no resize needed)")
                return

            # Calculate new dimension values maintaining aspect ratio
            if width > height:
                new_width = max_pixels
                new_height = int((height / width) * max_pixels)
            else:
                new_height = max_pixels
                new_width = int((width / height) * max_pixels)

            # Resize image
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Save resized with reduced quality, removing EXIF data (orientation already applied)
            img_resized.save(output_path, quality=quality, optimize=True, exif=b"")
            print(f"✓ Resized: {source_path.name}")
            print(f"  {width}x{height} → {new_width}x{new_height}")

    except Exception as e:
        print(f"✗ Error processing {source_path.name}: {e}")


def main():
    parser = argparse.ArgumentParser(
        prog="resize_images",
        description="Resizes JPG images and adjusts quality for size optimization. Resizing maintains the image's aspect ratio. The utility attempts to apply the source image's EXIF rotation to the output image. Images already smaller than the max dimension will not be increased or decreased in size, but will still be saved with the output JPG quality. If the images already exist in the destination folder with the same filename, the utility will overwrite them.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "source_dir",
        nargs="?",
        default=".",
        help="Source directory containing images",
    )

    parser.add_argument(
        "output_dir",
        nargs="?",
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for resized images, automatically created if it does not exist",
    )

    parser.add_argument(
        "--pixels",
        type=int,
        default=DEFAULT_MAX_PIXELS,
        help="Output max size of longest side in pixels",
    )

    parser.add_argument(
        "--quality",
        type=int,
        default=DEFAULT_QUALITY,
        help="Output JPG quality percentage",
    )

    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    output_dir = Path(args.output_dir)

    if not source_dir.exists():
        print(f"Error: {source_dir} does not exist")
        return

    image_files = []
    for ext in ["*.jpg", "*.jpeg", "*.JPG", "*.JPEG"]:
        image_files.extend(source_dir.glob(ext))

    if not image_files:
        print(f"No JPG files found in {source_dir}")
        return

    print(f"Found {len(image_files)} image(s) to process")
    print("=== Process Parameters ===")
    print(f"Max height or width: {args.pixels}px")
    print(f"Quality: {args.quality}%")
    print("==========================")
    print(f"\nProcessing images from {source_dir} to {output_dir}...\n")

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each image
    for source_path in sorted(image_files):
        # Create output path
        output_path = output_dir / source_path.name

        # Resize and optimize
        resize(source_path, output_path, args.pixels, args.quality)
        print()

    print(f"Done! Processed {len(image_files)} image(s)")
    print(f"Resized images saved to: {output_dir}")


if __name__ == "__main__":
    main()
