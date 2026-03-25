# 🕷️ Spider Testing Guide

This guide explains how to test the Spider web scraper using the provided test files.

## Test Files Structure

All test files are organized in the `test/` directory for cleaner project structure.

### Image Files
- **Location**: `test/images/` directory
- **Files**: `image1.jpg` through `image5.bmp` (5 dummy PNG images)
- **Purpose**: Valid downloadable test files

### HTML Test Pages
- **test/page0.html** - Main landing page (DEPTH 1)
  - Contains 4 images
  - Links to: page1.html, page2.html

- **test/page1.html** - Gallery section (DEPTH 2)
  - Contains 3 images
  - Links to: page0.html, page2.html, page3.html

- **test/page2.html** - Portfolio section (DEPTH 3)
  - Contains 4 images
  - Links to: page0.html, page1.html, page3.html

- **test/page3.html** - Archive section (DEPTH 4)
  - Contains 2 images
  - Links to: page0.html, page2.html, page4.html

- **test/page4.html** - Final page (DEPTH 5 - MAX)
  - Contains 2 images
  - Links to: page0.html, page3.html, page5.html (should NOT be crawled)

- **test/page5.html** - Beyond max depth (DEPTH 6)
  - Contains 2 images
  - ⚠️ Should NOT be crawled if depth limit is respected

## Total Test Resources
- **Total Images**: 15 images across 5 pages
- **Total Pages**: 6 pages (1 beyond max)
- **Total Links**: Multiple inter-page connections
- **File Size**: ~75 bytes each image (minimal, for testing only)

## Testing Scenarios

### Scenario 1: Single Page Crawl (No Recursion)
```bash
# Start HTTP server from project root
python3 -m http.server 8000

# In another terminal
source venv/bin/activate
./spider.py http://localhost:8000/test/page0.html
```

**Expected Results:**
- ✅ Downloads 4 images from page0.html
- ✅ Does NOT follow any links
- ✅ Files saved to ./data/ directory

### Scenario 2: Single-Level Recursive Crawl
```bash
./spider.py -r -l 1 http://localhost:8000/test/page0.html
```

**Expected Results:**
- ✅ Downloads 4 images from page0.html
- ✅ Does NOT follow links (depth 1 = only current page)
- ✅ Total: 4 images

### Scenario 3: Two-Level Deep Crawl
```bash
./spider.py -r -l 2 http://localhost:8000/test/page0.html
```

**Expected Results:**
- ✅ Visits: page0.html (depth 1)
- ✅ Visits: page1.html, page2.html (depth 2)
- ✅ Does not visit: page3.html, page4.html, page5.html
- ✅ Total: ~11 images (4 + 3 + 4 = 11)

### Scenario 4: Five-Level Deep Crawl (Maximum)
```bash
./spider.py -r -l 5 http://localhost:8000/test/page0.html
```

**Expected Results:**
- ✅ Visits: page0 → page1 → page2 → page3 → page4 (depths 1-5)
- ✅ Does NOT visit: page5.html (depth 6, beyond limit)
- ✅ Total: 15 images (4 + 3 + 4 + 2 + 2 = 15)

### Scenario 5: Six-Level Crawl (Should Exceed)
```bash
./spider.py -r -l 6 http://localhost:8000/test/page0.html
```

**Expected Results:**
- ✅ Visits: page0 → page1 → page2 → page3 → page4 → page5 (depths 1-6)
- ✅ Total: 17 images (4 + 3 + 4 + 2 + 2 + 2 = 17)

## Verifying Depth Limiting

To verify depth limiting is working correctly:

1. Run `./spider.py -r -l 5 http://localhost:8000/test/page0.html`
2. Check the downloaded images: you should have max 15 images
3. Verify page5.html was NOT visited
4. Check console output shows "DEPTH 6" NOT being crawled

## Duplicate Detection Test

The pages intentionally reuse images (same image1.jpg appears in multiple pages).

**Expected Behavior:**
- ✅ First occurrence of `image1.jpg` downloaded
- ✅ Subsequent occurrences SKIPPED (duplicate detection)
- ✅ Filename appears once in directory

## Image Statistics Summary

| Page | Depth | Images | New Images | Links To |
|------|-------|--------|-----------|----------|
| page0.html | 1 | 4 | 4 | page1, page2 |
| page1.html | 2 | 3 | 3 | page0, page2, page3 |
| page2.html | 3 | 4 | 3 (1 dup) | page0, page1, page3 |
| page3.html | 4 | 2 | 1 (1 dup) | page0, page2, page4 |
| page4.html | 5 | 2 | 0 (2 dup) | page0, page3, page5 |
| page5.html | 6 | 2 | - | (should not crawl) |

**Total Unique Images**: 15 (from pages 0-4)

## Troubleshooting

### Images not downloading
- Verify HTTP server is running: `python3 -m http.server 8000`
- Check Spider can access localhost: test with single page first
- Verify images are in `test/images/` directory
- Make sure you're running the HTTP server from the project root (not from test/)

### Wrong number of images
- Count may vary due to duplicate detection
- Use `ls -la data/` to count downloaded files
- Compare with expected totals above

### Depth limiting not working
- Run with `-l 5` and verify page5 is NOT crawled
- Check console output for depth indicators
- Verify visited_urls tracking in code is working

## Quick Start Command

```bash
# Terminal 1 - From project root
python3 -m http.server 8000

# Terminal 2 - From project root
source venv/bin/activate
./spider.py -r -l 5 http://localhost:8000/test/page0.html -p ./test_downloads/
```

This will recursively crawl the entire test suite up to depth 5 and save ~15 images to `test_downloads/`
