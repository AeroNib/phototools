#!/usr/bin/env python3
#
# This CLI utility processes all JPG files in a directory and generates
# thumbnails of a configurable size and quality for web display.

import argparse
from pathlib import Path

from PIL import Image

# Default configuration
DEFAULT_TARGET_DIMENSION = "height"  # Default dim (height, width) for thumbnail scaling
DEFAULT_TARGET_PIXELS = 200  # Default thumbnail dimension in pixels
DEFAULT_QUALITY = 80  # Default thumbnail JPG quality percentage
DEFAULT_OUTPUT_DIR = "thumbs"


def generate_thumbnail(
    source_path,  # Path to the source image
    output_path,  # Path to save the thumbnail
    dim,  # Dimension (height, width) used for scaling
    size,  # Thumbnail size of the scaling dimension
    quality,  # Thumbnail JPG quality percentage
):
    try:
        with Image.open(source_path) as img:
            # ImageOps.exif_transpose handles all EXIF orientation cases
            from PIL import ImageOps

            # Bakes image orientation into image by rotating to match EXIF orientation
            img = ImageOps.exif_transpose(img)

            if img is None:
                print(f"✗ Error: Could not process orientation for {source_path.name}")
                return

            ### old code below here

            # Calculate new width to maintain aspect ratio
            aspect_ratio = img.width / img.height
            if dim == "width":
                thumb_width = size
                thumb_height = int(thumb_width / aspect_ratio)
            else:
                thumb_height = size
                thumb_width = int(thumb_height * aspect_ratio)

            # Resize thumb
            img_resized = img.resize(
                (thumb_width, thumb_height), Image.Resampling.LANCZOS
            )

            # Save thumbnail with reduced quality, removing EXIF data (orientation already applied)
            img_resized.save(output_path, quality=quality, optimize=True, exif=b"")
            print(f"✓ Generated: {output_path.name}")

    except Exception as e:
        print(f"✗ Error processing {source_path.name}: {e}")


def main():
    parser = argparse.ArgumentParser(
        prog="generate_thumbs",
        description="Generates JPG thumbnails with adjustable size and quality. Thumbnail maintains the original image's aspect ratio. The utility attempts to apply the source image's EXIF rotation to the thumbnail. If the images already exist in the destination folder with the same filename, the utility will overwrite them.",
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
        "--dimension",
        type=str,
        choices=("width", "height"),
        default=DEFAULT_TARGET_DIMENSION,
        help="Dimension used for scaling thumbnail size",
    )

    parser.add_argument(
        "--pixels",
        type=int,
        default=DEFAULT_TARGET_PIXELS,
        help="Size to scale thumbnails, in pixels",
    )

    parser.add_argument(
        "--quality",
        type=int,
        default=DEFAULT_QUALITY,
        help="Thumbnail JPG quality percentage",
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
    print(f"{args.dimension}: {args.pixels}px")
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
        generate_thumbnail(
            source_path, output_path, args.dimension, args.pixels, args.quality
        )
        print()

    print(f"Done! Processed {len(image_files)} image(s)")
    print(f"Thumbnails saved to: {output_dir}")


if __name__ == "__main__":
    main()
