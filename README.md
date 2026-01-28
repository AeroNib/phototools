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

### rename_images

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
