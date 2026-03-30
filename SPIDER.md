# Spider - Web Image Scraper

A command-line tool for downloading images from websites with recursive crawling and depth control.

## Features

- **Single-page scraping**: Extract all images from a single webpage
- **Recursive crawling**: Automatically follow links and crawl multiple pages
- **Depth limiting**: Control crawl depth (default: 5 levels)
- **Duplicate detection**: Prevent duplicate downloads
- **Same-domain filtering**: Stay on the target domain
- **Rate limiting**: 0.5s delay between requests for respectful scraping
- **Format support**: JPEG, PNG, GIF, BMP files
- **Robust error handling**: Graceful handling of network issues and timeouts

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Commands

**Download images from a single page:**
```bash
python3 spider.py https://example.com
```

**Recursively crawl and download:**
```bash
python3 spider.py -r https://example.com
```

**Limit crawl depth:**
```bash
python3 spider.py -r -l 3 https://example.com
```

**Specify output directory:**
```bash
python3 spider.py -p ./downloads https://example.com
```

**Combine options:**
```bash
python3 spider.py -r -l 2 -p ./my_images https://example.com
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | `-h` | Display help message |
| `--recursive` | `-r` | Enable recursive crawling |
| `--level` | `-l` | Maximum crawl depth (default: 5) |
| `--path` | `-p` | Output directory for images |

## Examples

### Example 1: Single Page Download
```bash
python3 spider.py https://example.com/gallery
```
Downloads all images from the specified page to `./images` (default directory).

### Example 2: Shallow Recursive Crawl
```bash
python3 spider.py -r -l 2 https://example.com
```
Crawls up to 2 levels deep and saves images to `./images`.

### Example 3: Custom Output Location
```bash
python3 spider.py -r -l 3 -p /media/scraped_images https://example.com
```
Recursively crawls up to 3 levels and saves to `/media/scraped_images`.

### Example 4: Deep Crawl with Custom Path
```bash
python3 spider.py -r -l 5 -p ./website_archive https://example.com
```
Performs a full 5-level recursive crawl and saves to `./website_archive`.

## How It Works

1. **Initial Request**: Spider fetches the starting URL
2. **Image Extraction**: All image URLs are identified and downloaded
3. **Link Discovery**: All links are identified for further crawling
4. **Recursive Crawling**: Each discovered link is processed up to the specified depth
5. **Filtering**: Same-domain filter prevents crawling off-topic sites
6. **Deduplication**: Downloaded images are tracked to prevent duplicates

## Output

Downloaded images are saved to the specified directory with their original filenames. Directory structure is created automatically.

```
images/
├── image1.jpg
├── image2.png
├── photo.gif
└── ...
```

## Performance Notes

- Rate limiting (0.5s between requests) ensures respectful scraping
- Duplicate detection prevents unnecessary downloads
- Same-domain filtering reduces unnecessary data transfer
- Typical single-page download: < 1 second
- Recursive crawl speed depends on website size and structure

## Troubleshooting

### No images downloaded
- Verify the URL is correct and accessible
- Check that the website contains images
- Ensure you have internet connectivity

### Slow performance
- Reduce crawl depth with `-l` option
- Check your internet connection speed
- Large websites may take longer to process

### Permission errors
- Ensure you have write permission to the output directory
- Check disk space is available
- Try using an absolute path with `-p` option

## Integration with Scorpion

After downloading images with Spider, use Scorpion to analyze or modify their metadata:

```bash
# Download images
python3 spider.py -r -l 2 -p ./downloads https://example.com

# Analyze metadata
python3 scorpion.py ./downloads/*.jpg --analyze

# Remove sensitive metadata
python3 scorpion.py ./downloads/*.jpg --modify --strip-exif
```

## Get Help

```bash
python3 spider.py --help
```
