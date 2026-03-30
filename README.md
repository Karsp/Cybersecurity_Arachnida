# Arachnida

A comprehensive toolkit for web image acquisition and metadata management. Arachnida consists of two complementary tools: **Spider** for downloading images from websites, and **Scorpion** for analyzing and managing image metadata.

## Overview

Arachnida provides a complete solution for working with web images:

- **Spider**: Crawl websites and download images with recursive depth control
- **Scorpion**: Extract, analyze, and modify image metadata

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

#### Spider - Download Images

```bash
# Download images from a single page
python3 spider.py https://example.com

# Recursively crawl and download (up to 3 levels deep)
python3 spider.py -r -l 3 https://example.com

# Save to specific directory
python3 spider.py -p ./images https://example.com
```

#### Scorpion - Analyze Images

```bash
# Extract metadata from an image
python3 scorpion.py photo.jpg

# Analyze all images in a directory
python3 scorpion.py *.jpg --analyze

# Export metadata to JSON
python3 scorpion.py *.jpg -f json -o metadata.json

# Remove EXIF data (privacy protection)
python3 scorpion.py photo.jpg --modify --strip-exif
```

## Documentation

- **[SPIDER.md](SPIDER.md)** - Web image scraping tool documentation
- **[SCORPION.md](SCORPION.md)** - Image metadata management tool documentation

## Features

### Spider
- Recursive website crawling with depth limiting
- Support for JPEG, PNG, GIF, BMP formats
- Duplicate detection and same-domain filtering
- Rate limiting and robust error handling

### Scorpion
- Extract EXIF, IPTC, and basic metadata
- Export to JSON, CSV, or formatted console output
- Analyze image collections with statistics
- Filter images by format, size, or metadata presence
- Safely modify and remove metadata with automatic backups

## Requirements

- Python 3.7+
- Dependencies listed in requirements.txt

## System Compatibility

- Linux
- macOS
- Windows

## Project Structure

```
arachnida/
├── spider.py              # Web image scraper
├── scorpion.py            # Metadata extraction and modification
├── metadata_parser.py     # EXIF/IPTC metadata extraction
├── metadata_modifier.py   # Metadata modification utilities
├── metadata_filter.py     # Filtering and analysis
├── output_formatter.py    # JSON/CSV export formatting
├── scorpion_gui.py        # Optional GUI interface
├── requirements.txt       # Python dependencies
├── SPIDER.md              # Spider documentation
├── SCORPION.md            # Scorpion documentation
└── test/                  # Test images and pages
```

## Help

For detailed documentation, usage examples, and troubleshooting:

- Spider questions: See [SPIDER.md](SPIDER.md)
- Scorpion questions: See [SCORPION.md](SCORPION.md)

Get help from command line:

```bash
python3 spider.py --help
python3 scorpion.py --help
```

## License

This project is part of the Arachnida cybersecurity toolkit.
