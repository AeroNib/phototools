#!/usr/bin/env python3
"""
Photo Rename to Date-Time

This script renames photo sets in the current directory using their EXIF timestamp
converted to UTC datetime (assumes EXIF is in EST). Files sharing the same base name
but different extensions (e.g., IMG_1234.jpg and IMG_1234.RAF) are treated as a set
and given the same new name.

Format: {YYYYMMDD-HHMMSS}[-{seq}]-{4hex}.{ext}
Examples:
    20240123-143000-a3f5.jpg
    20240123-143000-a3f5.raf
    20231223-083343-01-83ab.jpg  (burst shot sequence)

Usage:
    without installing:
        python3 rename_photos.py

    installed as a pipx package:
        rename_photos
"""

import io
import re
import secrets
import struct
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import exifread

# Configuration
SOURCE_DIR = Path.cwd()
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".raf"}
EXIF_PRIORITY = [".jpg", ".jpeg", ".raf"]
RENAMED_PATTERN = re.compile(
    r"^\d{8}-\d{6}(-\d{2})?-[0-9a-f]{4}\.(jpg|jpeg|raf)$", re.IGNORECASE
)


def _extract_raf_jpeg(file_path):
    """
    Extract the embedded JPEG from a Fujifilm RAF file.

    RAF header structure (big-endian):
        0-15:   magic "FUJIFILMCCD-RAW "
        16-19:  format version
        20-27:  unknown
        28-59:  camera model (32 bytes)
        60-63:  unknown
        64-67:  unknown
        68-71:  unknown
        84-87:  JPEG offset (uint32)
        88-91:  JPEG length (uint32)

    Returns:
        BytesIO of the embedded JPEG, or None if not found
    """
    with open(file_path, "rb") as f:
        magic = f.read(16)
        if not magic.startswith(b"FUJIFILMCCD-RAW"):
            return None

        # Read JPEG offset and length at bytes 84-91
        f.seek(84)
        jpeg_offset, jpeg_length = struct.unpack(">II", f.read(8))

        if jpeg_offset == 0 or jpeg_length == 0:
            return None

        f.seek(jpeg_offset)
        jpeg_data = f.read(jpeg_length)

    return io.BytesIO(jpeg_data)


def _parse_exif_tags(file_handle):
    """Parse EXIF tags from a file handle and return a datetime or None."""
    tags = exifread.process_file(file_handle, stop_tag="DateTimeOriginal", details=False)

    for tag_name in ("EXIF DateTimeOriginal", "Image DateTime"):
        if tag_name in tags:
            dt_str = str(tags[tag_name])
            return datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")

    return None


def get_exif_datetime(file_path):
    """
    Extract the datetime from EXIF data.

    For RAF files, extracts the embedded JPEG and reads EXIF from that.
    For other formats, reads EXIF directly via exifread.

    Args:
        file_path: Path to the image file

    Returns:
        datetime object or None if not found
    """
    try:
        if file_path.suffix.lower() == ".raf":
            jpeg_data = _extract_raf_jpeg(file_path)
            if jpeg_data is None:
                return None
            return _parse_exif_tags(jpeg_data)
        else:
            with open(file_path, "rb") as f:
                return _parse_exif_tags(f)

    except Exception as e:
        print(f"  Warning: Could not read EXIF from {file_path.name}: {e}")
        return None


def generate_random_hex(length=4):
    """Generate random hex characters."""
    return secrets.token_hex(length // 2)


def scan_and_group(source_dir):
    """
    Scan directory for supported files and group them into photo sets by stem.

    Returns:
        dict mapping lowercase stem to list of Path objects, sorted by stem
    """
    sets = defaultdict(list)
    for f in source_dir.iterdir():
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            sets[f.stem.lower()].append(f)

    # Sort files within each set by extension for consistent ordering
    for stem in sets:
        sets[stem].sort(key=lambda p: p.suffix.lower())

    return sets


def is_already_renamed(photo_set):
    """Check if ALL files in a set already match the renamed pattern."""
    return all(RENAMED_PATTERN.match(f.name) for f in photo_set)


def get_set_timestamp(photo_set):
    """
    Get the EXIF timestamp for a photo set, trying files in priority order.

    Returns:
        UTC datetime string (YYYYMMDD-HHMMSS) and the original EST datetime, or (None, None)
    """
    # Sort files by EXIF_PRIORITY order
    priority_sorted = sorted(
        photo_set, key=lambda p: _ext_priority(p.suffix.lower())
    )

    for file_path in priority_sorted:
        dt = get_exif_datetime(file_path)
        if dt:
            # Convert EST (UTC-5) to UTC
            est = timezone(timedelta(hours=-5))
            dt_est = dt.replace(tzinfo=est)
            dt_utc = dt_est.astimezone(timezone.utc)
            utc_timestamp = dt_utc.strftime("%Y%m%d-%H%M%S")
            return utc_timestamp, dt, dt_utc

    return None, None, None


def _ext_priority(ext):
    """Return sort key for extension priority. Lower = higher priority."""
    try:
        return EXIF_PRIORITY.index(ext)
    except ValueError:
        return len(EXIF_PRIORITY)


def assign_sequences(sets_with_timestamps):
    """
    Assign sequence numbers to sets that share the same timestamp.
    Sets are ordered by their original stem name to preserve shot order.

    Args:
        sets_with_timestamps: list of (stem, photo_set, timestamp, dt_est, dt_utc)

    Returns:
        list of (stem, photo_set, timestamp, sequence_str, dt_est, dt_utc)
        where sequence_str is "" for unique timestamps or "-01", "-02", etc.
    """
    # Count how many sets share each timestamp
    timestamp_counts = defaultdict(int)
    for _, _, timestamp, _, _ in sets_with_timestamps:
        timestamp_counts[timestamp] += 1

    # Assign sequences, tracking per-timestamp counters
    timestamp_counters = defaultdict(int)
    result = []
    for stem, photo_set, timestamp, dt_est, dt_utc in sets_with_timestamps:
        if timestamp_counts[timestamp] > 1:
            timestamp_counters[timestamp] += 1
            seq = f"-{timestamp_counters[timestamp]:02d}"
        else:
            seq = ""
        result.append((stem, photo_set, timestamp, seq, dt_est, dt_utc))

    return result


def rename_set(photo_set, timestamp, sequence, dt_est, dt_utc):
    """
    Rename all files in a photo set.

    Returns:
        Number of files renamed (0 if error)
    """
    hex_suffix = generate_random_hex()

    renamed = []
    for file_path in photo_set:
        ext = file_path.suffix.lower()
        new_name = f"{timestamp}{sequence}-{hex_suffix}{ext}"
        new_path = file_path.parent / new_name

        # Handle collision
        while new_path.exists():
            hex_suffix = generate_random_hex()
            new_name = f"{timestamp}{sequence}-{hex_suffix}{ext}"
            new_path = file_path.parent / new_name

        try:
            file_path.rename(new_path)
            renamed.append((file_path.name, new_name))
        except Exception as e:
            print(f"  ✗ Error renaming {file_path.name}: {e}")
            return 0

    # Print results
    dt_str_est = dt_est.strftime("%Y-%m-%d %H:%M:%S EST")
    dt_str_utc = dt_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
    for old_name, new_name in renamed:
        print(f"  ✓ {old_name} → {new_name}")
    print(f"    ({dt_str_est} → {dt_str_utc})")

    return len(renamed)


def main():
    """Main function to process all photo sets."""
    # Step 1-2: Scan and group
    photo_sets = scan_and_group(SOURCE_DIR)

    if not photo_sets:
        print("No supported photo files found")
        return

    # Step 3: Filter already-renamed sets
    sets_to_process = {
        stem: files
        for stem, files in photo_sets.items()
        if not is_already_renamed(files)
    }

    if not sets_to_process:
        print("No photos to rename (all files already have timestamp names)")
        return

    # Step 4: Extract timestamps, sorted by stem to preserve original order
    sets_with_timestamps = []
    skipped = 0
    for stem in sorted(sets_to_process.keys()):
        photo_set = sets_to_process[stem]
        timestamp, dt_est, dt_utc = get_set_timestamp(photo_set)
        if timestamp:
            sets_with_timestamps.append((stem, photo_set, timestamp, dt_est, dt_utc))
        else:
            file_names = ", ".join(f.name for f in photo_set)
            print(f"✗ Skipped: {file_names} (no EXIF datetime found)")
            skipped += 1

    if not sets_with_timestamps:
        print(f"\nNo photos with EXIF timestamps found (skipped {skipped} set(s))")
        return

    # Step 5: Assign sequences for duplicate timestamps
    sets_with_sequences = assign_sequences(sets_with_timestamps)

    # Step 6: Rename
    print(f"Found {len(sets_with_sequences)} photo set(s) to rename\n")

    total_files_renamed = 0
    sets_renamed = 0
    for stem, photo_set, timestamp, sequence, dt_est, dt_utc in sets_with_sequences:
        count = rename_set(photo_set, timestamp, sequence, dt_est, dt_utc)
        if count:
            sets_renamed += 1
            total_files_renamed += count
        print()

    print(
        f"Done! Renamed {total_files_renamed} file(s) "
        f"across {sets_renamed} of {len(sets_with_sequences)} set(s)"
    )
    if skipped:
        print(f"Skipped {skipped} set(s) with no EXIF datetime")


if __name__ == "__main__":
    main()
