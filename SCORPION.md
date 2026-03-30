# Scorpion - Image Metadata Manager

A command-line tool for extracting, analyzing, and modifying image metadata. Supports JPEG, PNG, GIF, and BMP formats.

## Features

- **Metadata extraction**: EXIF, IPTC, basic image properties
- **Multiple export formats**: JSON, CSV, formatted console output
- **Analysis and reporting**: Statistics on image collections
- **Filtering**: Filter by format, size, or metadata presence
- **Metadata modification**: Remove EXIF data, strip metadata, add comments
- **Safe operations**: Automatic backups for all modifications
- **Batch processing**: Process multiple images efficiently

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Commands

**Extract metadata from an image:**
```bash
python3 scorpion.py photo.jpg
```

**Analyze multiple images:**
```bash
python3 scorpion.py *.jpg
python3 scorpion.py images/*
```

**Export to JSON:**
```bash
python3 scorpion.py *.jpg -f json -o metadata.json
```

**Export to CSV:**
```bash
python3 scorpion.py *.jpg -f csv -o report.csv
```

**Analyze collection:**
```bash
python3 scorpion.py *.jpg --analyze
```

### Metadata Modification

**Remove EXIF data (privacy):**
```bash
python3 scorpion.py photo.jpg --modify --strip-exif
```

**Remove all metadata:**
```bash
python3 scorpion.py photo.jpg --modify --strip-all
```

**Add comment:**
```bash
python3 scorpion.py photo.jpg --modify --add-comment "Summer 2024"
```

**Restore from backup:**
```bash
python3 scorpion.py photo.jpg --modify --restore
```

### Filtering

**Filter by image format:**
```bash
python3 scorpion.py *.* --analyze --filter-format JPEG
```

**Filter by file size (in KB):**
```bash
python3 scorpion.py *.* --analyze --filter-size 50 500
```

**Only process images with EXIF:**
```bash
python3 scorpion.py *.jpg --analyze --filter-exif
```

### Options

| Option | Description |
|--------|-------------|
| `-f, --format` | Output format: `console` (default), `json`, or `csv` |
| `-o, --output` | Output file path (required for json/csv) |
| `--modify` | Enable modification mode |
| `--strip-exif` | Remove EXIF data from images |
| `--strip-all` | Remove all metadata from images |
| `--add-comment TEXT` | Add text comment to image |
| `--restore` | Restore image from backup |
| `--analyze` | Generate analysis report |
| `--filter-format FMT` | Filter by format (JPEG, PNG, GIF, BMP) |
| `--filter-size MIN MAX` | Filter by size range in KB |
| `--filter-exif` | Only process images with EXIF data |

## Examples

### Example 1: Extract Metadata
```bash
python3 scorpion.py photo.jpg
```
Displays image dimensions, format, color mode, and other properties.

### Example 2: Export Metadata Collection
```bash
python3 scorpion.py *.jpg -f json -o images.json
```
Exports metadata from all JPEGs to a JSON file for further processing.

### Example 3: Analyze Image Directory
```bash
python3 scorpion.py images/* --analyze
```
Generates statistics: format distribution, file sizes, metadata coverage.

### Example 4: Remove Sensitive Data
```bash
python3 scorpion.py photo.jpg --modify --strip-exif
```
Removes EXIF data (location, camera info) before sharing. Original is backed up.

### Example 5: Filter and Analyze
```bash
python3 scorpion.py *.* --analyze --filter-format JPEG
```
Analyzes only JPEG files from a mixed-format directory.

### Example 6: Batch Remove Metadata
```bash
python3 scorpion.py *.jpg --modify --strip-all
```
Removes all metadata from all JPEGs with automatic backups.

### Example 7: Size-Based Analysis
```bash
python3 scorpion.py *.* --analyze --filter-size 100 1000
```
Analyzes only images between 100 KB and 1 MB.

## Metadata Information

### EXIF (Exchangeable Image File Format)
Camera settings, GPS data, capture date, camera model, exposure, ISO, etc. Typically found in JPEG and TIFF files.

### IPTC (International Press Telecommunications Council)
Keywords, copyright, author, description, title, etc.

### Basic Metadata
Image dimensions, file size, format, color mode.

### Other Metadata
Color profile, compression, software used.

## Workflow Examples

### Privacy Protection Workflow
```bash
# 1. Check what metadata is present
python3 scorpion.py personal_photos/*.jpg

# 2. Remove sensitive EXIF data
python3 scorpion.py personal_photos/*.jpg --modify --strip-exif

# 3. Verify removal
python3 scorpion.py personal_photos/*.jpg
```

### Image Archive Workflow
```bash
# 1. Analyze collection
python3 scorpion.py archive/*.* --analyze -f json -o analysis.json

# 2. Export complete metadata
python3 scorpion.py archive/*.* -f csv -o metadata.csv

# 3. Create documentation
cat metadata.csv  # Review in spreadsheet application
```

### Web Publishing Workflow
```bash
# 1. Remove all metadata
python3 scorpion.py website_photos/*.jpg --modify --strip-all

# 2. Export list for reference
python3 scorpion.py website_photos/*.jpg -f csv -o published_images.csv

# 3. Verify clean metadata
python3 scorpion.py website_photos/*.jpg --analyze
```

## Backup System

When using `--modify`, Scorpion automatically creates backups:

```
original_photo.jpg          # Modified version
original_photo_backup.jpg   # Original backup
```

To restore the original:
```bash
python3 scorpion.py original_photo.jpg --modify --restore
```

Keep backup files safe. They contain your original images.

## Output Formats

### Console (Default)
```
📷 File: photo.jpg
📊 BASIC INFORMATION:
   Dimensions: 1920 x 1080
   Format: JPEG
   Size: 245 KB
```

### JSON
Structured format for programmatic processing and archival.

### CSV
Spreadsheet-compatible format for analysis in Excel, Google Sheets, etc.

## Performance

- Single image metadata extraction: ~100ms
- Batch processing (10 images): ~500ms
- Analysis report generation: ~1-2 seconds
- Scales efficiently to large collections

## Troubleshooting

### No EXIF data found
This is normal. PNG, GIF, and BMP files don't contain EXIF metadata. Only JPEG and TIFF typically have EXIF data.

### Backup file not found
Ensure you're using the correct filename. Backups are created with `_backup` suffix in the same directory.

### Permission denied
Check that you have write permission to the image directory:
```bash
chmod +r *.jpg  # Read permission for images
```

### Export file already exists
The output file will be overwritten. To preserve, use a different filename with `-o` option.

## Integration with Spider

Use Spider to download images, then Scorpion to manage them:

```bash
# Download images
python3 spider.py -r -l 2 -p ./downloads https://example.com

# Analyze the collection
python3 scorpion.py ./downloads/*.jpg --analyze

# Remove metadata before publishing
python3 scorpion.py ./downloads/*.jpg --modify --strip-exif
```

## Get Help

```bash
python3 scorpion.py --help
```
