# phototools

Python CLI tools for automating photo workflows.

## Installation

Install with pipx:

```bash
pipx install git+https://github.com/AeroNib/phototools.git
```

Or install from a local clone:

```bash
pipx install .
```

To upgrade an existing pipx installation to the latest version:
```bash
pipx upgrade phototools
```

## Tools

### rename_photos

Renames photo files based on their EXIF timestamp.

**Format:** `{YYYYMMDD-HHMMSS}-{optional sequence}-{4hex}.jpg`  
**Example:** `20240123-143000-01-a3f5.jpg`

It processes groups of files with the same original file name as a set, e.g., `IMG_0001.JPG` and `IMG_0001.RAF` are assumed to be two file formats of the same photo and will be renamed together with the same new file name with the appropriate file extension. Files that already match the new file format are skipped.

EXIF timestamps are assumed to be in EST and will be converted to UTC. Handling different time zones may be added in a future version.

Renaming adds up to two suffixes to handle possible filename collisions. First, all names are suffixed with a four random characters. Second, if two or more file sets in a run have the same time stamp, an optional two-digit sequence is added between the time stamp and four-digit suffix. This sequence is ordered to preserve the original file order.


### rename_images

> [!IMPORTANT]
> `rename_images` has been superseded by `rename_photos`, but it has been kept for now for compatibility. `rename_photos` is more powerful and can handle photo file sets, including raw photo files.

Renames JPG files based on their EXIF timestamp, converting to UTC format. Four random characters are appended to avoid filename collisions. 

**Format:** `{YYYYMMDD-HHMMSS}-{4hex}.jpg`  
**Example:** `20240123-143000-a3f5.jpg`

**Usage:**

```bash
cd /path/to/your/photos
rename_images
```

For each JPG file in the source directory, the script will:
- Convert the EXIF timestamp to UTC (assumes EXIF is EST)
- Rename files with UTC timestamp + random hex suffix
- Skip files already matching the pattern

### resize_images

Resizes JPG images and adjusts quality for size optimization. Maintains aspect ratio and applies EXIF rotation. Images smaller than the max dimension size are optimized for quality but not resized.

**Default output:** `resized/` directory  
**Default max size:** 3000px (longest edge)  
**Default quality:** 80%

**Usage:**

```bash
# Process current directory with defaults
resize_images

# Additional arguments and options
resize_images resize_images [-h] [--pixels MAX_SIZE_IN_PIXELS] [--quality QUALITY] [source_dir] [output_dir]

# For example
resize_images --pixels 2500 --quality 90 ./photos ./web-photos 
```

For each JPG file in the source directory, the script will:
- Apply EXIF orientation and strips EXIF data from the output file
- Resize images exceeding max dimension while maintaining aspect ratio
- Save to output directory (created automatically if needed) at specified JPG quality
- Overwrite existing files with same filename

### generate_thumbs

Generates JPG thumbnails with adjustable size and quality. Maintains aspect ratio and applies EXIF rotation.

**Default output:** `thumbs/` directory  
**Default dimension:** height  
**Default size:** 200px  
**Default quality:** 80%

**Usage:**

```bash
# Process current directory with defaults (200px height thumbnails)
generate_thumbs

# Additional arguments and options
generate_thumbs [-h] [--dimension {width,height}] [--pixels DIMENSION_SIZE_IN_PIXELS] [--quality QUALITY] [source_dir] [output_dir]

# For example
generate_thumbs --dimension width --pixels 150 --quality 65 ./photos ./web-thumbnails
```

For each JPG file in the source directory, the script will:
- Apply EXIF orientation and strips EXIF data from the output file
- Scale thumbnails to specified dimension and size while maintaining aspect ratio
- Save to output directory (created automatically if needed) at specified JPG quality
- Overwrite existing files with same filename

## Requirements

- Python >=3.7
- Pillow >=9.0.0

## License

MIT
