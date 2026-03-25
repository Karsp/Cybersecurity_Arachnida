# Spider - Web Image Scraper

A Python-based web scraper that recursively downloads images from websites with support for depth limiting and custom save paths.

## Features

- **Single-page scraping**: Extract all images from a single webpage
- **Recursive crawling**: Automatically follow links and crawl multiple pages
- **Depth limiting**: Control how deep the recursive crawl goes (default: 5 levels)
- **Duplicate detection**: Avoid downloading the same image twice
- **Same-domain filtering**: Stay on the original domain to prevent crawling the entire web
- **Rate limiting**: Respectful 0.5s delay between requests
- **Multiple formats**: Downloads .jpg, .jpeg, .png, .gif, .bmp files
- **Error handling**: Robust error handling for network issues, timeouts, and invalid files

## Installation

### Requirements
- Python 3.7+
- pip

### Setup

```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Single-Page Scraping

Download all images from a single webpage:

```bash
./spider.py https://example.com
```

### Recursive Crawling

Recursively crawl a website and download images from all linked pages:

```bash
./spider.py -r https://example.com
```

### Control Depth Level

Limit how deep the recursive crawl goes (default is 5):

```bash
./spider.py -r -l 3 https://example.com
```

### Custom Save Directory

Save downloaded images to a custom location:

```bash
./spider.py -p ./my_images/ https://example.com
./spider.py -r -l 2 -p /tmp/downloads/ https://example.com
```

### All Options Together

```bash
./spider.py -r -l 4 -p ./website_images/ https://example.com
```

## Testing

### Test Suite Organization

All test files are organized in the `test/` directory:

```
test/
├── page0.html           # Main page (Depth 1) - 4 images
├── page1.html           # Gallery (Depth 2) - 3 images
├── page2.html           # Portfolio (Depth 3) - 4 images
├── page3.html           # Archive (Depth 4) - 2 images
├── page4.html           # Final page (Depth 5) - 2 images
├── page5.html           # Beyond limit (Depth 6) - 2 images
├── test.html            # Feature test page (9+ images)
├── images/              # Dummy PNG image files
│   ├── image1.jpg
│   ├── image2.jpeg
│   ├── image3.gif
│   ├── image4.png
│   └── image5.bmp
└── TESTING.md           # Detailed testing guide
```

### Quick Test: Single Page Crawl

Test Spider with a simple single-page download:

```bash
# Terminal 1: Start HTTP server (from project root)
python3 -m http.server 8000

# Terminal 2: In another terminal, run Spider
source venv/bin/activate
./spider.py http://localhost:8000/test/page0.html
```

**Expected**: Downloads 4 images from page0.html to `./data/`

### Test: Recursive Crawling with Depth Limiting

Test the full recursive crawling suite:

```bash
# Terminal 1: Start HTTP server (from project root)
python3 -m http.server 8000

# Terminal 2: Crawl up to depth 5
source venv/bin/activate
./spider.py -r -l 5 http://localhost:8000/test/page0.html
```

**Expected Results:**
- ✅ Visits pages 0-4 (depths 1-5)
- ✅ Does NOT visit page5 (depth 6, beyond limit)
- ✅ Downloads ~15 total images
- ✅ Detects duplicates and skips them

### Test Cases Available

1. **Feature Test** (`test/test.html`)
   - Tests all image formats (.jpg, .png, .gif, .bmp)
   - Tests relative and absolute URL resolution
   - Tests query parameters and fragments
   - Tests invalid extensions filtering

2. **Recursive Crawl Test** (`test/page0.html` - `test/page5.html`)
   - Tests multi-page recursive crawling
   - Tests depth limiting (page5 should not be crawled with -l 5)
   - Tests duplicate image detection
   - Tests same-domain filtering

### For Detailed Testing Instructions

See `test/TESTING.md` for:
- All testing scenarios with expected results
- Different depth level tests
- Duplicate detection verification
- Depth limiting validation

### Example 4: Test with local server
```bash
# Terminal 1
python3 -m http.server 8000

# Terminal 2
./spider.py http://localhost:8000/test/page0.html

# Or with recursion
./spider.py -r -l 2 http://localhost:8000/test/page0.html
```

## Architecture Overview

Spider is built in 5 main steps:

### Step 1: URL Validation & Fetching
- Validates URL format
- Handles missing schemes (adds http://)
- Fetches HTML with proper error handling
- Handles HTTP status codes and timeouts

### Step 2: HTML Parsing & Image Extraction
- Parses HTML using BeautifulSoup
- Finds all `<img>` tags
- Resolves relative URLs to absolute
- Filters by valid image extensions
- Removes duplicates

### Step 3: File Operations & Storage
- Creates download directory structure
- Generates unique filenames from URLs
- Detects already-downloaded images
- Saves binary data safely
- Validates content-type is image

### Step 4: Recursive Crawling & Depth Tracking
- Extracts links from HTML pages
- Filters external domain links (stays on-domain)
- Tracks visited URLs (prevents infinite loops)
- Maintains depth counter
- Recursively crawls found links up to depth limit

### Step 5: Final Polish & Testing
- Comprehensive error handling
- Rate limiting and respectful requests
- Complete CLI interface
- Full documentation and testing

## Command Examples

### Example 1: Download images from a news site (1 page)
```bash
./spider.py https://news.example.com/article
# Downloads all images from the article page to ./data/
```

### Example 2: Crawl an entire photography portfolio (3 levels deep)
```bash
./spider.py -r -l 3 -p ./portfolio_images/ https://photography.example.com
# Crawls the site 3 levels deep, downloading from all linked pages
```

### Example 3: Quick download from a specific page
```bash
./spider.py https://example.com/gallery
# Single page, saves to ./data/
```

### Example 4: Test with local server
```bash
# Terminal 1 (from project root)
python3 -m http.server 8000

# Terminal 2 (from project root)
source venv/bin/activate

# Single page test
./spider.py http://localhost:8000/test/page0.html

# Recursive test (depth 5)
./spider.py -r -l 5 http://localhost:8000/test/page0.html

# With custom save directory
./spider.py -r -l 5 -p ./test_downloads/ http://localhost:8000/test/page0.html
```

## Output Example

```
🕷️  Spider starting...
   URL: https://example.com
   Recursive: True, Depth: 2, Path: ./data/

📋 Step 1: Validating URL...
✅ URL valid: https://example.com

📋 Step 3: Setting up downloads...
✅ Download directory ready: data

📋 Step 4: Starting recursive crawl...

📍 Crawling (depth 1/2): https://example.com
   Found 12 <img> tags
   ✅ Extracted 8 valid image URLs
   ✅ Downloaded: photo1.jpg (245.3 KB)
   ✅ Downloaded: photo2.png (156.8 KB)
   ...
   Extracting links for next level...
   Found 5 links on this page

📍 Crawling (depth 2/2): https://example.com/gallery
   Found 20 <img> tags
   ✅ Extracted 15 valid image URLs
   ...

📊 Recursive Crawl Summary:
   📍 Pages visited: 6
   ✅ Images downloaded: 47
   📁 Saved to: data
```

## Supported Image Formats

- `.jpg` / `.jpeg`
- `.png`
- `.gif`
- `.bmp`

## Error Handling

Spider handles various error scenarios:

- **Network errors**: Timeouts, connection failures
- **HTTP errors**: 404 Not Found, 403 Forbidden, 429 Rate Limited, 5xx Server Errors
- **File errors**: Permission issues, invalid paths
- **HTML parsing**: Malformed HTML, missing attributes
- **Duplicate detection**: Skips already-downloaded images

## Privacy & Ethics

⚠️ **Important Considerations:**

- Respect website terms of service and `robots.txt`
- Obtain permission before scraping copyrighted content
- The 0.5s delay between requests is built-in to be respectful to servers
- Don't use this tool for mass scraping that could overload servers
- Be aware of local laws regarding web scraping

## Rate Limiting

Spider automatically includes:
- 0.5 second delay between requests
- Connection pooling (reuses TCP connections)
- Proper User-Agent headers

## Limitations

- Does not execute JavaScript (only parses static HTML)
- Does not handle pages requiring authentication
- Cannot access HTTPS content on systems with certificate issues
- Depth is measured in page links, not physical website structure

## Troubleshooting

### "Connection failed" error
- Check your internet connection
- Verify the URL is correct
- Try with `http://` instead of `https://` if the site has SSL issues

### "Permission denied" when saving files
- Check write permissions for the target directory
- Ensure the path exists and is accessible

### Downloads are slow
- Network speed varies; the 0.5s delay is intentional
- Larger images take longer to download
- Consider using `-l 1` for shallow crawls

### No images found
- The website might not have images
- Images might be loaded via JavaScript (not supported)
- Try a different page on the website

## Technical Details

- **Language**: Python 3.7+
- **HTTP Library**: requests
- **HTML Parser**: BeautifulSoup with lxml backend
- **Threading**: Single-threaded (respects rate limiting)
- **Memory**: Minimal (streams binary data, doesn't load full images into memory)

## License

This project is for educational purposes.

## Contributing

Contributions are welcome! Feel free to submit issues or improvements.

