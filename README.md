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

The script will:
- Look for JPG files in the current directory
- Extract EXIF datetime (assumes EST timezone)
- Convert to UTC
- Rename files with timestamp + random hex suffix
- Skip files already matching the pattern

## Requirements

- Python >=3.7
- Pillow >=9.0.0

## License

MIT
